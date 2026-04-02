# Copyright © 2011-2026 Splunk, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"): you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import json
import logging
import uuid
from collections.abc import Awaitable, Callable, Sequence
from dataclasses import asdict, dataclass
from functools import partial
from typing import Any, cast, final, override

from langchain.agents import create_agent  # pyright: ignore[reportUnknownVariableType]
from langchain.agents.middleware import (
    AgentMiddleware as LC_AgentMiddleware,
    AgentState as LC_AgentState,
    ModelRequest as LC_ModelRequest,
    ModelResponse as LC_ModelResponse,
)
from langchain.agents.middleware.summarization import TokenCounter as LC_TokenCounter
from langchain.agents.middleware.types import (
    ExtendedModelResponse as LC_ExtendedModelResponse,
    ModelCallResult as LC_ModelCallResult,
)
from langchain.messages import (
    AIMessage as LC_AIMessage,
    AnyMessage as LC_AnyMessage,
    HumanMessage as LC_HumanMessage,
    SystemMessage as LC_SystemMessage,
    ToolCall as LC_ToolCall,
    ToolMessage as LC_ToolMessage,
)
from langchain.tools import ToolException as LC_ToolException
from langchain.tools.tool_node import ToolCallRequest as LC_ToolCallRequest
from langchain_core.language_models import BaseChatModel
from langchain_core.messages.base import BaseMessage as LC_BaseMessage
from langchain_core.messages.utils import count_tokens_approximately
from langchain_core.tools import BaseTool, StructuredTool
from langgraph.graph.state import CompiledStateGraph
from langgraph.types import Command as LC_Command

from splunklib.ai.base_agent import BaseAgent
from splunklib.ai.core.backend import (
    AgentImpl,
    Backend,
    InvalidMessageTypeError,
    InvalidModelError,
)
from splunklib.ai.hooks import (
    after_model as hook_after_model,
    before_model as hook_before_model,
)
from splunklib.ai.messages import (
    AgentResponse,
    AIMessage,
    BaseMessage,
    HumanMessage,
    OutputT,
    SubagentCall,
    SubagentFailureResult,
    SubagentMessage,
    SubagentStructuredResult,
    SubagentTextResult,
    SystemMessage,
    ToolCall,
    ToolFailureResult,
    ToolMessage,
    ToolResult,
)
from splunklib.ai.middleware import (
    AgentMiddleware,
    AgentMiddlewareHandler,
    AgentRequest,
    AgentState,
    ModelMiddlewareHandler,
    ModelRequest,
    ModelResponse,
    SubagentMiddlewareHandler,
    SubagentRequest,
    SubagentResponse,
    ToolMiddlewareHandler,
    ToolRequest,
    ToolResponse,
    subagent_middleware,
    tool_middleware,
)
from splunklib.ai.model import AnthropicModel, OpenAIModel, PredefinedModel
from splunklib.ai.tools import Tool, ToolException, ToolType

# Represents a prefix reserved only for internal use.
# No user-visible tool or subagent name can be prefixed with it.
RESERVED_LC_TOOL_PREFIX = "__"

# Prepended to agent name when used as a tool.
# All subagents-as-tools have this prefix.
AGENT_PREFIX = f"{RESERVED_LC_TOOL_PREFIX}agent-"

# Prepended to a tool name in case it already starts with INTERNAL_TOOL_PREFIX. This
# prevents user-provided tools from starting with AGENT_PREFIX and also serves as a
# backward compatibility measure - we're free to use any prefixed tool name.
CONFLICTING_TOOL_PREFIX = f"{RESERVED_LC_TOOL_PREFIX}tool-"

# Prepended to a local tool name when passed to LangChain to both avoid name conflicts
# and to allow recovering tool type during LC -> SDK conversion
LOCAL_TOOL_PREFIX = f"{RESERVED_LC_TOOL_PREFIX}local-"

AGENT_AS_TOOLS_PROMPT = f"""
You are provided with Agents.
Agents are more advanced TOOLS, which start with "{AGENT_PREFIX}" prefix.

Do not call the tools if not needed.
"""

ANTHROPIC_CHAT_MODEL_TYPE = "anthropic-chat"


@final
class LangChainBackend(Backend):
    @override
    async def create_agent(
        self,
        agent: BaseAgent[OutputT],
    ) -> AgentImpl[OutputT]:
        return LangChainAgentImpl(agent)


@dataclass
class LangChainAgentImpl(AgentImpl[OutputT]):
    _agent: CompiledStateGraph[Any]
    _sdk_agent: BaseAgent[OutputT]

    def __init__(self, agent: BaseAgent[OutputT]) -> None:
        super().__init__()
        self._sdk_agent = agent

        tools = _prepare_langchain_tools(agent.tools)

        system_prompt = agent.system_prompt
        structured_subagents: list[str] = []
        if agent.agents:
            seen_names: set[str] = set()
            for subagent in agent.agents:
                # Call _agent_as_tool first, so that the empty name exception is
                # checked and raised first, before the duplicated name exception.
                tool = _agent_as_tool(subagent)

                if subagent.name in seen_names:
                    raise AssertionError(
                        f"Subagents share the same name: {subagent.name}"
                    )

                seen_names.add(subagent.name)
                tools.append(tool)

                if subagent.input_schema is not None:
                    structured_subagents.append(subagent.name)

                system_prompt = AGENT_AS_TOOLS_PROMPT + "\n" + system_prompt

        before_user_middlewares, after_user_middlewares = _debugging_middleware(
            agent.logger
        )

        middleware = before_user_middlewares
        middleware.extend(agent.middleware or [])
        middleware.extend(after_user_middlewares)

        model_impl = _create_langchain_model(agent.model)

        lc_middleware: list[LC_AgentMiddleware] = [
            _Middleware(m, model_impl, agent.logger) for m in (middleware or [])
        ]

        # This middleware is executed just after the tool execution and populates
        # the artifact field for failed tool calls, since in such cases we can't
        # populate the artifact in LC directly since this is an LC_ToolException that only
        # allows setting of the content field.
        # We do that here, to avoid doing this logic in the individual conversion helpers.
        #
        # TODO: once we move middlewares into one LC middleware, we should move
        # that piece of logic there (DVPL-12959).
        class _ToolFailureArtifact(LC_AgentMiddleware):
            @override
            async def awrap_tool_call(
                self,
                request: LC_ToolCallRequest,
                handler: Callable[
                    [LC_ToolCallRequest], Awaitable[LC_ToolMessage | LC_Command[None]]
                ],
            ) -> LC_ToolMessage | LC_Command[None]:
                resp = await handler(request)
                assert isinstance(resp, LC_ToolMessage)
                assert resp.name, "missing tool name"

                if resp.status == "error":
                    assert resp.artifact is None, "artifact is already populated"

                    if resp.name.startswith(AGENT_PREFIX):
                        resp.artifact = SubagentFailureResult(str(resp.content))  # pyright: ignore[reportUnknownArgumentType]
                    else:
                        resp.artifact = ToolFailureResult(str(resp.content))  # pyright: ignore[reportUnknownArgumentType]

                return resp

        class _SubagentArgumentPacker(LC_AgentMiddleware):
            # For non-structured subagents, the SubagentCall.args field is an `str | dict[str, Any]`,
            # to differentiate that we wrap the resulting args in an SubagentLCArgs.
            #
            # This middleware performs the corresponding pack/unpack at the two
            # points in the LangChain call graph where raw args are needed/retreived.
            #
            # TODO: once we move middlewares into one LC middleware, we should move
            # that piece of logic there (DVPL-12959).
            @override
            async def awrap_model_call(
                self,
                request: LC_ModelRequest,
                handler: Callable[[LC_ModelRequest], Awaitable[LC_ModelCallResult]],
            ) -> LC_ModelCallResult:
                # Unpack existing messages.
                messages: list[LC_AnyMessage] = []
                for msg in request.messages:
                    if isinstance(msg, LC_AIMessage):
                        new_calls: list[LC_ToolCall] = []
                        for call in msg.tool_calls:
                            new_calls.append(self.unpack_tool_call(call))
                        msg = msg.model_copy(update={"tool_calls": new_calls})
                    messages.append(msg)

                response = await handler(request.override(messages=messages))

                ai_message = response
                if isinstance(ai_message, LC_ExtendedModelResponse):
                    ai_message = ai_message.model_response
                if isinstance(ai_message, LC_ModelResponse):
                    ai_message = next(
                        (m for m in ai_message.result if isinstance(m, LC_AIMessage)),
                        None,
                    )
                    assert ai_message, "AIMessage not found found in response"

                # Pack new message.
                for call in ai_message.tool_calls:
                    if call["name"].startswith(AGENT_PREFIX):
                        if (
                            _denormalize_agent_name(call["name"])
                            in structured_subagents
                        ):
                            args = SubagentLCArgs(call["args"])
                        else:
                            content: str = call["args"].get("content", "")
                            args = SubagentLCArgs(content)
                        call["args"] = asdict(args)

                return response

            # Unpack args, just before tool call.
            @override
            async def awrap_tool_call(
                self,
                request: LC_ToolCallRequest,
                handler: Callable[
                    [LC_ToolCallRequest], Awaitable[LC_ToolMessage | LC_Command[None]]
                ],
            ) -> LC_ToolMessage | LC_Command[None]:
                return await handler(
                    request.override(
                        tool_call=self.unpack_tool_call(request.tool_call),
                    )
                )

            def unpack_tool_call(self, call: LC_ToolCall) -> LC_ToolCall:
                if call["name"].startswith(AGENT_PREFIX):
                    unpacked_args = SubagentLCArgs(**call["args"]).args
                    if isinstance(unpacked_args, str):
                        unpacked_args = {"content": unpacked_args}
                    return LC_ToolCall(
                        id=call["id"],
                        name=call["name"],
                        args=unpacked_args,
                    )
                return call

        lc_middleware.append(_ToolFailureArtifact())
        lc_middleware.append(_SubagentArgumentPacker())

        self._agent = create_agent(
            model=model_impl,
            tools=tools,
            system_prompt=system_prompt,
            response_format=agent.output_schema,
            middleware=lc_middleware,
        )

    def _with_agent_middleware(
        self,
        agent_invoke: Callable[[AgentRequest], Awaitable[AgentResponse[Any | None]]],
    ) -> Callable[[AgentRequest], Awaitable[AgentResponse[Any | None]]]:
        # When provided with a list of middlewares, e.g. [m1, m2, m3],
        # they are executed in the following order:
        #
        # m1 -> m2 -> m3 -> agent_invoke
        #
        # Each middleware wraps the next one in the chain.
        #
        # - m1's handler calls m2.agent_middleware(...)
        # - m2's handler calls m3.agent_middleware(...)
        # - m3's handler eventually calls agent_invoke(...)
        #
        # We build the chain by iterating in reverse order.
        # Each middleware wraps the previously constructed handler,
        # so the first middleware in the list becomes the outermost one.

        invoke = agent_invoke
        for middleware in reversed(self._sdk_agent.middleware or []):

            def make_next(
                m: AgentMiddleware, h: AgentMiddlewareHandler
            ) -> AgentMiddlewareHandler:
                async def next(r: AgentRequest) -> AgentResponse[Any | None]:
                    return await m.agent_middleware(r, h)

                return next

            invoke = make_next(middleware, invoke)

        return invoke

    @override
    async def invoke(
        self, messages: list[BaseMessage], thread_id: str
    ) -> AgentResponse[OutputT]:
        # TODO: What if we are passed len(messages) == 0 to invoke?
        # TODO: What if someone passed call_id that don't have a corresponding id with the response.
        # Possibly we should do a validation phase of messages here.

        async def invoke_agent(req: AgentRequest) -> AgentResponse[Any | None]:
            langchain_msgs = []

            # Prepend messages from conversation store.
            if self._sdk_agent.conversation_store:
                msgs = await self._sdk_agent.conversation_store.get_messages(thread_id)
                langchain_msgs.extend([_map_message_to_langchain(m) for m in msgs])

            langchain_msgs.extend([_map_message_to_langchain(m) for m in req.messages])

            # call the langchain agent
            result = await self._agent.ainvoke(
                {"messages": langchain_msgs},
            )

            sdk_msgs = [_map_message_from_langchain(m) for m in result["messages"]]
            assert type(sdk_msgs[-1]) is AIMessage, "last message was not an AIMessage"
            assert len(sdk_msgs[-1].calls) == 0, (
                "last message is an AIMessage with calls != 0"
            )

            # NOTE: Agent responses will always conform to output schema. Verifying
            # if an LLM made any mistakes or not is _always_ up to the developer.

            assert (
                self._sdk_agent.output_schema is None
                or type(result["structured_response"]) is self._sdk_agent.output_schema
            )

            if self._sdk_agent.output_schema:
                return AgentResponse(
                    structured_output=result["structured_response"],
                    messages=sdk_msgs,
                )
            else:
                return AgentResponse(structured_output=None, messages=sdk_msgs)

        result = await self._with_agent_middleware(invoke_agent)(
            AgentRequest(
                messages=messages,
            )
        )

        # TODO: should we move these checks to run in-between individual middlewares,
        # not after all were executed?

        if type(result.messages[-1]) is not AIMessage:
            raise AssertionError(
                "AgentMiddleware did not include an AIMessage at result.messages[-1]"
            )

        if len(result.messages[-1].calls) != 0:
            raise AssertionError("AgentMiddleware included tool calls in AIMessage")

        if self._sdk_agent.output_schema:
            if result.structured_output is None:
                raise AssertionError("Agent middleware discarded a structured output")

            if type(result.structured_output) is not self._sdk_agent.output_schema:
                raise AssertionError(
                    f"Agent middleware returned an invalid structured_output type: {type(result.structured_output)}, want: {self._sdk_agent.output_schema}"
                )

            # Store the resulting messages in the conversation store, after all
            # agent middlewares have been executed.
            if self._sdk_agent.conversation_store:
                await self._sdk_agent.conversation_store.store_messages(
                    thread_id, result.messages
                )

            return AgentResponse[OutputT](
                messages=result.messages,
                structured_output=result.structured_output,
            )
        else:
            if result.structured_output is not None:
                raise AssertionError(
                    "Agent middleware unexpectedly included a structured output"
                )

            # Store the resulting messages in the conversation store, after all
            # agent middlewares have been executed.
            if self._sdk_agent.conversation_store:
                await self._sdk_agent.conversation_store.store_messages(
                    thread_id, result.messages
                )

            return AgentResponse[OutputT](
                messages=result.messages,
                # HACK: This let's us put None in the structured_output field. It also shows
                # None as the field type if no `output_schema`was provided to the Agent class.
                structured_output=cast(OutputT, None),
            )


def _prepare_langchain_tools(agent_tools: Sequence[Tool]) -> list[BaseTool]:
    """We prefix every local tool name."""
    tools = list[BaseTool]()
    for a_tool in agent_tools:
        tools.append(_create_langchain_tool(a_tool))

    return tools


class _Middleware(LC_AgentMiddleware):
    _middleware: AgentMiddleware
    _model: BaseChatModel
    _logger: logging.Logger
    _name: str

    def __init__(
        self,
        middleware: AgentMiddleware,
        model: BaseChatModel,
        logger: logging.Logger,
    ) -> None:
        self._middleware = middleware
        self._model = model
        self._logger = logger
        self._name = str(uuid.uuid4())

    def _is_overridden(self, method_name: str) -> bool:
        """Return True if the middleware method was overridden by the user."""
        return getattr(type(self._middleware), method_name) is not getattr(
            AgentMiddleware, method_name
        )

    @property
    @override
    def name(self) -> str:
        return self._name

    @override
    async def awrap_model_call(
        self,
        request: LC_ModelRequest,
        handler: Callable[[LC_ModelRequest], Awaitable[LC_ModelCallResult]],
    ) -> LC_ModelCallResult:
        if not self._is_overridden("model_middleware"):
            # Optimization: if not overridden, then skip the conversion overhead.
            return await handler(request)

        sdk_response = await self._middleware.model_middleware(
            _convert_model_request_from_lc(request, self._model),
            _convert_model_handler_from_lc(handler, original_request=request),
        )
        return _convert_model_response_to_model_result(sdk_response)

    @override
    async def awrap_tool_call(
        self,
        request: LC_ToolCallRequest,
        handler: Callable[
            [LC_ToolCallRequest], Awaitable[LC_ToolMessage | LC_Command[None]]
        ],
    ) -> LC_ToolMessage | LC_Command[None]:
        call = _map_tool_call_from_langchain(request.tool_call)

        if isinstance(call, ToolCall):
            if not self._is_overridden("tool_middleware"):
                # Optimization: if not overridden, skip the conversion overhead.
                return await handler(request)

            sdk_response = await self._middleware.tool_middleware(
                _convert_tool_request_from_lc(request, self._model),
                _convert_tool_handler_from_lc(handler, original_request=request),
            )

            sdk_result = sdk_response.result
            match sdk_result:
                case ToolResult():
                    status = "success"
                    if sdk_result.structured_content:
                        # both content + structured_content
                        content = json.dumps(asdict(sdk_response))
                    else:
                        content = sdk_result.content
                case ToolFailureResult():
                    status = "error"
                    content = sdk_result.error_message
                    pass

            return LC_ToolMessage(
                name=_normalize_tool_name(call.name, call.type),
                tool_call_id=call.id,
                content=content,
                status=status,
                artifact=sdk_result,
            )

        if not self._is_overridden("subagent_middleware"):
            # Optimization: if not overridden, skip the conversion overhead.
            return await handler(request)

        sdk_response = await self._middleware.subagent_middleware(
            _convert_subagent_request_from_lc(request, self._model),
            _convert_subagent_handler_from_lc(handler, original_request=request),
        )

        sdk_result = sdk_response.result
        match sdk_result:
            case SubagentStructuredResult():
                status = "success"
                # both content + structured_content
                content = json.dumps(sdk_result.structured_output)
            case SubagentTextResult():
                status = "success"
                # both content + structured_content
                content = sdk_result.content
            case SubagentFailureResult():
                status = "error"
                content = sdk_result.error_message
                pass

        return LC_ToolMessage(
            name=_normalize_agent_name(call.name),
            tool_call_id=call.id,
            content=content,
            status=status,
            artifact=sdk_result,
        )


def _convert_tool_handler_from_lc(
    handler: Callable[
        [LC_ToolCallRequest], Awaitable[LC_ToolMessage | LC_Command[None]]
    ],
    original_request: LC_ToolCallRequest,
) -> ToolMiddlewareHandler:
    async def _sdk_handler(request: ToolRequest) -> ToolResponse:
        lc_request = _convert_tool_request_to_lc(request, original_request)
        result = await handler(lc_request)
        sdk_result = _convert_tool_message_from_lc(result)
        assert isinstance(sdk_result, ToolMessage), (
            "Expected tool response from tool middleware handler"
        )
        return ToolResponse(sdk_result.result)

    return _sdk_handler


def _convert_subagent_handler_from_lc(
    handler: Callable[
        [LC_ToolCallRequest], Awaitable[LC_ToolMessage | LC_Command[None]]
    ],
    original_request: LC_ToolCallRequest,
) -> SubagentMiddlewareHandler:
    async def _sdk_handler(
        request: SubagentRequest,
    ) -> SubagentResponse:
        lc_request = _convert_subagent_request_to_lc(request, original_request)
        result = await handler(lc_request)
        sdk_result = _convert_tool_message_from_lc(result)
        assert isinstance(sdk_result, SubagentMessage), (
            "Expected subagent response from subagent middleware handler"
        )
        return SubagentResponse(sdk_result.result)

    return _sdk_handler


def _convert_model_handler_from_lc(
    handler: Callable[[LC_ModelRequest], Awaitable[LC_ModelCallResult]],
    original_request: LC_ModelRequest,
) -> ModelMiddlewareHandler:
    async def _sdk_handler(request: ModelRequest) -> ModelResponse:
        lc_request = _convert_model_request_to_lc(request, original_request)
        result = await handler(lc_request)

        return _convert_model_result_from_lc(result)

    return _sdk_handler


def _convert_model_request_from_lc(
    request: LC_ModelRequest, model: BaseChatModel
) -> ModelRequest:
    system_message = (
        request.system_message.content.__str__() if request.system_message else ""
    )

    return ModelRequest(
        system_message=system_message,
        state=_convert_agent_state_from_langchain(request.state, model),
    )


def _convert_tool_request_from_lc(
    request: LC_ToolCallRequest, model: BaseChatModel
) -> ToolRequest:
    tool_call = _map_tool_call_from_langchain(request.tool_call)
    assert isinstance(tool_call, ToolCall), "Expected tool call"
    return ToolRequest(
        call=tool_call,
        state=_convert_agent_state_from_langchain(request.state, model),
    )


def _convert_subagent_request_from_lc(
    request: LC_ToolCallRequest,
    model: BaseChatModel,
) -> SubagentRequest:
    subagent_call = _map_tool_call_from_langchain(request.tool_call)
    assert isinstance(subagent_call, SubagentCall), "Expected subagent call"
    return SubagentRequest(
        call=subagent_call,
        state=_convert_agent_state_from_langchain(request.state, model),
    )


def _convert_tool_request_to_lc(
    request: ToolRequest, original_request: LC_ToolCallRequest
) -> LC_ToolCallRequest:
    return original_request.override(
        tool_call=_map_tool_call_to_langchain(request.call),
        state=_convert_agent_state_to_lc(request.state),
    )


def _convert_subagent_request_to_lc(
    request: SubagentRequest,
    original_request: LC_ToolCallRequest,
) -> LC_ToolCallRequest:
    return original_request.override(
        tool_call=_map_tool_call_to_langchain(request.call),
        state=_convert_agent_state_to_lc(request.state),
    )


def _convert_model_request_to_lc(
    request: ModelRequest,
    original_request: LC_ModelRequest,
) -> LC_ModelRequest:
    return original_request.override(
        system_message=LC_SystemMessage(content=request.system_message),
        state=_convert_agent_state_to_lc(request.state),
    )


def _convert_model_response_to_model_result(
    resp: ModelResponse,
) -> LC_ModelCallResult:
    lc_message = LC_AIMessage(content=resp.message.content)
    # This field can't be set via __init__()
    lc_message.tool_calls = [_map_tool_call_to_langchain(c) for c in resp.message.calls]
    if resp.structured_output is not None:
        return LC_ModelResponse(
            result=[lc_message],
            structured_response=resp.structured_output,
        )
    return lc_message


def _convert_tool_message_to_lc(
    message: ToolMessage | SubagentMessage,
) -> LC_ToolMessage:
    match message:
        case SubagentMessage():
            name = _normalize_agent_name(message.name)
            match message.result:
                case SubagentStructuredResult():
                    status = "success"
                    content = json.dumps(message.result.structured_output)
                case SubagentTextResult():
                    status = "success"
                    content = message.result.content
                case SubagentFailureResult():
                    status = "error"
                    content = message.result.error_message
        case ToolMessage():
            name = _normalize_tool_name(message.name, message.type)
            match message.result:
                case ToolResult():
                    if message.result.structured_content:
                        # both content + structured_content
                        content = json.dumps(asdict(message.result))
                    else:
                        content = message.result.content
                    status = "success"
                case ToolFailureResult():
                    status = "error"
                    content = message.result.error_message

    return LC_ToolMessage(
        name=name,
        tool_call_id=message.call_id,
        status=status,
        content=content,
        artifact=message.result,
    )


def _convert_tool_message_from_lc(
    message: LC_ToolMessage | LC_Command[None],
) -> ToolMessage | SubagentMessage:
    match message:
        case LC_ToolMessage(name=name) if name and name.startswith(AGENT_PREFIX):
            assert (
                isinstance(message.artifact, SubagentStructuredResult)
                or isinstance(message.artifact, SubagentTextResult)
                or isinstance(message.artifact, SubagentFailureResult)
            )
            return SubagentMessage(
                name=_denormalize_agent_name(name),
                call_id=message.tool_call_id,
                result=message.artifact,
            )
        case LC_ToolMessage():
            # If this is reached, we likely passed an invalid tool name to LangChain.
            assert message.name is not None, (
                "LangChain responded with a nameless tool call"
            )

            assert isinstance(message.artifact, ToolResult) or isinstance(
                message.artifact, ToolFailureResult
            )

            tool_type: ToolType = (
                ToolType.LOCAL
                if message.name.startswith(LOCAL_TOOL_PREFIX)
                else ToolType.REMOTE
            )
            return ToolMessage(
                name=_denormalize_tool_name(message.name),
                call_id=message.tool_call_id,
                type=tool_type,
                result=message.artifact,
            )
        case LC_Command():
            # NOTE: for now the command is not implemented
            # if this is gonna be useful we will implement it
            # in the future
            raise NotImplementedError("Command is not supported")


def _convert_model_result_from_lc(model_response: LC_ModelCallResult) -> ModelResponse:
    if isinstance(model_response, LC_ExtendedModelResponse):
        model_response = model_response.model_response

    if isinstance(model_response, LC_ModelResponse):
        ai_message = next(
            (m for m in model_response.result if isinstance(m, LC_AIMessage)), None
        )
        assert ai_message, "ModelResponse should contain at least one LC_AIMessage"
        structured_response = model_response.structured_response
    else:
        ai_message = model_response
        structured_response = None

    return ModelResponse(
        message=AIMessage(
            content=ai_message.content.__str__(),
            calls=[_map_tool_call_from_langchain(tc) for tc in ai_message.tool_calls],
        ),
        structured_output=structured_response,
    )


def _convert_agent_state_to_lc(state: AgentState) -> LC_AgentState[Any]:
    messages = [_map_message_to_langchain(m) for m in state.response.messages]
    return LC_AgentState(messages=messages)


def _debugging_middleware(
    logger: logging.Logger,
) -> tuple[list[AgentMiddleware], list[AgentMiddleware]]:
    @tool_middleware
    async def _tool_call(
        request: ToolRequest, handler: ToolMiddlewareHandler
    ) -> ToolResponse:
        call = request.call
        logger.debug(f"Tool call {call.name} stared; id={call.id}")
        try:
            response = await handler(request)

            if type(response.result) is ToolResult:
                logger.debug(f"Tool call {call.name} succeeded; id={call.id}")
            else:
                logger.debug(f"Tool call {call.name} failed; id={call.id}")

            return response
        except Exception:
            logger.debug(f"Tool call {call.name} failed; id={call.id}")
            raise

    @subagent_middleware
    async def _subagent_call(
        request: SubagentRequest,
        handler: SubagentMiddlewareHandler,
    ) -> SubagentResponse:
        call = request.call
        logger.debug(f"Subagent call {call.name} stared; id={call.id}")
        try:
            response = await handler(request)

            if (
                type(response.result) is SubagentStructuredResult
                or type(response.result) is SubagentTextResult
            ):
                logger.debug(f"Subagent call {call.name} succeeded; id={call.id}")
            else:
                logger.debug(f"Subagent call {call.name} failed; id={call.id}")

            return response
        except Exception:
            logger.debug(f"Subagent call {call.name} failed; id={call.id}")
            raise

    @hook_after_model
    def _debug_after_model(resp: ModelResponse) -> None:
        requested_tool_calls = [
            (call.name, call.id)
            for call in resp.message.calls
            if isinstance(call, ToolCall)
        ]
        requested_subagent_calls = [
            (call.name, call.id)
            for call in resp.message.calls
            if isinstance(call, SubagentCall)
        ]
        logger.debug(
            "LLM model invocation ended; "
            + f"{requested_tool_calls=}; "
            + f"{requested_subagent_calls=}"
        )

    @hook_before_model
    def _debug_before_model(_: ModelRequest) -> None:
        logger.debug("Invoking LLM model")

    before_user_hooks = [_debug_after_model]
    after_user_hooks = [_debug_before_model, _tool_call, _subagent_call]
    return before_user_hooks, after_user_hooks


def _create_langchain_tool(tool: Tool) -> BaseTool:
    async def _tool_call(
        **kwargs: dict[str, Any],
    ) -> tuple[dict[str, Any] | str, ToolResult]:
        try:
            result = await tool.func(**kwargs)
        except ToolException as e:
            raise LC_ToolException(*e.args) from e
        except LC_ToolException:
            assert False, (  # noqa: PT015
                "ToolException from LangChain should not be raised in tool.func"
            )

        # TODO: Should we change the splunklib.ai.tools.ToolResult.content to a str, instead of list[str]?
        text_content = "\n".join(result.content)

        artifact = ToolResult(text_content, result.structured_content)

        if result.structured_content:
            # For both local tools and remote tools (Splunk MCP Server App), the primary
            # payload is returned in structured_content. The content field is typically
            # minimal for remote tools and empty for local tools.
            #
            # FastMCP behaves slightly differently: when structured_content is returned,
            # it also includes json.dumps(structured_content) in the content field.
            #
            # If we introduce support for additional MCP implementations in the future,
            # this assumption may need to be revisited. For now, this approach is fine.
            # Worst-case scenario is the same information is provided to the LLM twice.
            return asdict(result), artifact  # both content + structured_content
        return text_content, artifact

    return StructuredTool(
        name=_normalize_tool_name(tool.name, tool.type),
        description=tool.description,
        args_schema=tool.input_schema,
        coroutine=_tool_call,
        response_format="content_and_artifact",
        handle_tool_error=True,
        tags=tool.tags,
    )


def langchain_backend_factory() -> LangChainBackend:
    return LangChainBackend()


def _normalize_agent_name(name: str) -> str:
    return f"{AGENT_PREFIX}{name}"


def _denormalize_agent_name(name: str) -> str:
    return name.removeprefix(AGENT_PREFIX)


def _normalize_tool_name(name: str, tool_type: ToolType) -> str:
    if tool_type == ToolType.LOCAL:
        return LOCAL_TOOL_PREFIX + name

    if name.startswith(RESERVED_LC_TOOL_PREFIX):
        # Tool name contains our reserved prefix, see comment
        # on CONFLICTING_TOOL_PREFIX for more details
        return CONFLICTING_TOOL_PREFIX + name

    return name


def _denormalize_tool_name(name: str) -> str:
    if name.startswith(RESERVED_LC_TOOL_PREFIX):
        assert "-" in name, "Invalid prefix in tool name"
        _prefix, name = name.split("-", maxsplit=1)

    return name


def _agent_as_tool(agent: BaseAgent[OutputT]) -> StructuredTool:
    if not agent.name:
        raise AssertionError("Agent must have a name to be used by other Agents")

    # TODO: The schemas that are inferred here could be better, we specify the schema as:
    # OutputT | str, but we know based on agent.output_schema whether this either OutputT or str.

    if agent.input_schema is None:

        async def _run(  # pyright: ignore[reportRedeclaration]
            content: str,
        ) -> tuple[OutputT | str, SubagentStructuredResult | SubagentTextResult]:
            result = await agent.invoke([HumanMessage(content=content)])
            if agent.output_schema:
                assert result.structured_output is not None
                return result.structured_output, SubagentStructuredResult(
                    structured_output=result.structured_output.model_dump(),
                )

            ai_message = result.messages[-1]
            assert type(ai_message) is AIMessage
            return ai_message.content, SubagentTextResult(content=ai_message.content)

        return StructuredTool.from_function(
            coroutine=_run,
            name=_normalize_agent_name(agent.name),
            description=agent.description,
            infer_schema=True,
            response_format="content_and_artifact",
        )

    InputSchema = agent.input_schema

    async def _run(
        **kwargs: dict[str, Any],
    ) -> tuple[OutputT | str, SubagentStructuredResult | SubagentTextResult]:
        req = InputSchema(**kwargs)
        request_text = f"INPUT_JSON:\n{req.model_dump_json()}\n"

        result = await agent.invoke([HumanMessage(content=request_text)])

        if agent.output_schema:
            assert result.structured_output is not None
            return result.structured_output, SubagentStructuredResult(
                structured_output=result.structured_output.model_dump(),
            )

        ai_message = result.messages[-1]
        assert type(ai_message) is AIMessage
        return ai_message.content, SubagentTextResult(content=ai_message.content)

    return StructuredTool.from_function(
        coroutine=_run,
        name=_normalize_agent_name(agent.name),
        description=agent.description,
        args_schema=InputSchema,
        response_format="content_and_artifact",
    )


@dataclass(frozen=True)
class SubagentLCArgs:
    args: str | dict[str, Any]


def _map_tool_call_from_langchain(tool_call: LC_ToolCall) -> ToolCall | SubagentCall:
    name = tool_call["name"]
    if name.startswith(AGENT_PREFIX):
        return SubagentCall(
            name=_denormalize_agent_name(name),
            args=SubagentLCArgs(**tool_call["args"]).args,
            id=tool_call["id"],
        )

    tool_type: ToolType = (
        ToolType.LOCAL if name.startswith(LOCAL_TOOL_PREFIX) else ToolType.REMOTE
    )
    return ToolCall(
        name=_denormalize_tool_name(name),
        args=tool_call["args"],
        id=tool_call["id"],
        type=tool_type,
    )


def _map_tool_call_to_langchain(call: ToolCall | SubagentCall) -> LC_ToolCall:
    match call:
        case SubagentCall():
            name = _normalize_agent_name(call.name)
            args = asdict(SubagentLCArgs(call.args))
        case ToolCall():
            name = _normalize_tool_name(call.name, call.type)
            args = call.args

    return LC_ToolCall(id=call.id, name=name, args=args)


def _map_message_from_langchain(message: LC_BaseMessage) -> BaseMessage:
    match message:
        case LC_AIMessage():
            return AIMessage(
                content=message.content.__str__(),
                calls=[_map_tool_call_from_langchain(tc) for tc in message.tool_calls],
            )
        case LC_HumanMessage():
            return HumanMessage(content=message.content.__str__())
        case LC_ToolMessage():
            return _convert_tool_message_from_lc(message)
        case LC_SystemMessage():
            return SystemMessage(content=message.content.__str__())
        case _:
            raise InvalidMessageTypeError("Invalid langchain message type")


def _map_message_to_langchain(message: BaseMessage) -> LC_AnyMessage:
    match message:
        case AIMessage():
            lc_message = LC_AIMessage(content=message.content)
            # This field can't be set via constructor
            lc_message.tool_calls = [
                _map_tool_call_to_langchain(c) for c in message.calls
            ]
            return lc_message
        case HumanMessage():
            return LC_HumanMessage(content=message.content)
        case SubagentMessage() | ToolMessage():
            return _convert_tool_message_to_lc(message)
        case SystemMessage():
            return LC_SystemMessage(content=message.content)
        case _:
            raise InvalidMessageTypeError("Invalid SDK message type")


def _convert_agent_state_from_langchain(
    state: LC_AgentState[Any], model: BaseChatModel
) -> AgentState:
    messages = state["messages"]
    total_tokens_counter = _get_approximate_token_counter(model)
    total_tokens = total_tokens_counter(messages)

    response = AgentResponse[Any | None](
        messages=[_map_message_from_langchain(m) for m in state["messages"]],
        structured_output=state.get("structured_response"),
    )

    return AgentState(
        response=response,
        total_steps=len(messages),
        token_count=total_tokens,
    )


def _get_approximate_token_counter(model: BaseChatModel) -> LC_TokenCounter:
    """Tune parameters of approximate token counter based on model type."""

    # NOTE: This is adapted from the backend provider library
    # 3.3 was estimated in an offline experiment, comparing with Claude's token-counting
    # API: https://platform.claude.com/docs/en/build-with-claude/token-counting
    if model._llm_type == ANTHROPIC_CHAT_MODEL_TYPE:  # pyright: ignore[reportPrivateUsage]
        return partial(count_tokens_approximately, chars_per_token=3.3)
    return count_tokens_approximately


def _create_langchain_model(model: PredefinedModel) -> BaseChatModel:
    match model:
        case OpenAIModel():
            try:
                from langchain_openai import ChatOpenAI

                return ChatOpenAI(
                    model=model.model,
                    base_url=model.base_url,
                    api_key=lambda: model.api_key,
                    temperature=model.temperature,
                    extra_body=model.extra_body,
                    http_async_client=model.httpx_client,
                )
            except ImportError:
                raise ImportError(
                    "OpenAI support is not installed.\n"
                    + "To enable OpenAI / ChatGPT models, install the optional extra:\n"
                    + 'pip install "splunk-sdk[openai]"\n'
                    + "# or if using uv:\n"
                    + "uv add splunk-sdk[openai]"
                )
        case AnthropicModel():
            try:
                from langchain_anthropic import ChatAnthropic

                kwargs: dict[str, Any] = {
                    "model_name": model.model,
                    "api_key": model.api_key,
                    "base_url": model.base_url,
                }
                if model.temperature is not None:
                    kwargs["temperature"] = model.temperature

                return ChatAnthropic(**kwargs)
            except ImportError:
                raise ImportError(
                    "Anthropic support is not installed.\n"
                    + "To enable Anthropic models, install the optional extra:\n"
                    + 'pip install "splunk-sdk[anthropic]"\n'
                    + "# or if using uv:\n"
                    + "uv add splunk-sdk[anthropic]"
                )
        case _:
            raise InvalidModelError(
                "Cannot create langchain model - invalid SDK model provided"
            )

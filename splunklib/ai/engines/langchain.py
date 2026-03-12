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
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.state import CompiledStateGraph, RunnableConfig
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
    SubagentMessage,
    SystemMessage,
    ToolCall,
    ToolMessage,
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
from splunklib.ai.model import OpenAIModel, PredefinedModel
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


@dataclass
class LangChainAgentImpl(AgentImpl[OutputT]):
    _agent: CompiledStateGraph[Any]
    _thread_id: uuid.UUID
    _config: RunnableConfig
    _output_schema: type[OutputT] | None
    _middleware: Sequence[AgentMiddleware]

    def __init__(
        self,
        system_prompt: str,
        model: BaseChatModel,
        tools: list[BaseTool],
        output_schema: type[OutputT] | None,
        lc_middleware: Sequence[LC_AgentMiddleware] | None = None,
        middleware: Sequence[AgentMiddleware] | None = None,
    ) -> None:
        super().__init__()
        self._output_schema = output_schema
        self._thread_id = uuid.uuid4()
        self._config = {"configurable": {"thread_id": self._thread_id}}
        self._middleware = middleware or []

        checkpointer = InMemorySaver()

        self._agent = create_agent(
            model=model,
            tools=tools,
            system_prompt=system_prompt,
            checkpointer=checkpointer,
            response_format=output_schema,
            middleware=lc_middleware or [],
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
        for middleware in reversed(self._middleware):

            def make_next(
                m: AgentMiddleware, h: AgentMiddlewareHandler
            ) -> AgentMiddlewareHandler:
                async def next(r: AgentRequest) -> AgentResponse[Any | None]:
                    return await m.agent_middleware(r, h)

                return next

            invoke = make_next(middleware, invoke)

        return invoke

    @override
    async def invoke(self, messages: list[BaseMessage]) -> AgentResponse[OutputT]:
        async def invoke_agent(req: AgentRequest) -> AgentResponse[Any | None]:
            langchain_msgs = [_map_message_to_langchain(m) for m in req.messages]

            # call the langchain agent
            result = await self._agent.ainvoke(
                {"messages": langchain_msgs},
                config=self._config,
            )

            sdk_msgs = [_map_message_from_langchain(m) for m in result["messages"]]

            # NOTE: Agent responses will always conform to output schema. Verifying
            # if an LLM made any mistakes or not is _always_ up to the developer.

            assert (
                self._output_schema is None
                or type(result["structured_response"]) is self._output_schema
            )

            if self._output_schema:
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

        if self._output_schema:
            if result.structured_output is None:
                raise AssertionError("Agent middleware discarded a structured output")

            if type(result.structured_output) is not self._output_schema:
                raise AssertionError(
                    f"Agent middleware returned an invalid structured_output type: {type(result.structured_output)}, want: {self._output_schema}"
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


@final
class LangChainBackend(Backend):
    @override
    async def create_agent(
        self,
        agent: BaseAgent[OutputT],
    ) -> AgentImpl[OutputT]:
        tools = _prepare_langchain_tools(agent.tools)

        system_prompt = agent.system_prompt
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

                system_prompt = AGENT_AS_TOOLS_PROMPT + "\n" + system_prompt

        before_user_middlewares, after_user_middlewares = _debugging_middleware(
            agent.logger
        )

        middleware = before_user_middlewares
        middleware.extend(agent.middleware or [])
        middleware.extend(after_user_middlewares)

        model_impl = _create_langchain_model(agent.model)
        middleware = [
            _Middleware(m, model_impl, agent.logger) for m in middleware or []
        ]

        return LangChainAgentImpl(
            system_prompt=system_prompt,
            model=model_impl,
            tools=tools,
            output_schema=agent.output_schema,
            lc_middleware=middleware,
            middleware=agent.middleware,
        )


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

            return LC_ToolMessage(
                name=_normalize_tool_name(call.name, call.type),
                tool_call_id=call.id,
                content=sdk_response.content,
                status=sdk_response.status,
            )

        if not self._is_overridden("subagent_middleware"):
            # Optimization: if not overridden, skip the conversion overhead.
            return await handler(request)

        sdk_response = await self._middleware.subagent_middleware(
            _convert_subagent_request_from_lc(request, self._model),
            _convert_subagent_handler_from_lc(handler, original_request=request),
        )

        return LC_ToolMessage(
            name=_normalize_agent_name(call.name),
            tool_call_id=call.id,
            content=sdk_response.content,
            status=sdk_response.status,
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
        return ToolResponse(content=sdk_result.content, status=sdk_result.status)

    return _sdk_handler


def _convert_subagent_handler_from_lc(
    handler: Callable[
        [LC_ToolCallRequest], Awaitable[LC_ToolMessage | LC_Command[None]]
    ],
    original_request: LC_ToolCallRequest,
) -> SubagentMiddlewareHandler:
    async def _sdk_handler(request: SubagentRequest) -> SubagentResponse:
        lc_request = _convert_subagent_request_to_lc(request, original_request)
        result = await handler(lc_request)
        sdk_result = _convert_tool_message_from_lc(result)
        assert isinstance(sdk_result, SubagentMessage), (
            "Expected subagent response from subagent middleware handler"
        )
        return SubagentResponse(content=sdk_result.content, status=sdk_result.status)

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
        case ToolMessage():
            name = _normalize_tool_name(message.name, message.type)

    return LC_ToolMessage(
        name=name,
        content=message.content,
        tool_call_id=message.call_id,
        status=message.status,
    )


def _convert_tool_message_from_lc(
    message: LC_ToolMessage | LC_Command[None],
) -> ToolMessage | SubagentMessage:
    match message:
        case LC_ToolMessage(name=name) if name and name.startswith(AGENT_PREFIX):
            return SubagentMessage(
                name=_denormalize_agent_name(name),
                content=message.content.__str__(),
                call_id=message.tool_call_id,
                status=message.status,
            )
        case LC_ToolMessage():
            # If this is reached, we likely passed an invalid tool name to LangChain.
            assert message.name is not None, (
                "LangChain responded with a nameless tool call"
            )

            tool_type: ToolType = (
                ToolType.LOCAL
                if message.name.startswith(LOCAL_TOOL_PREFIX)
                else ToolType.REMOTE
            )
            return ToolMessage(
                name=_denormalize_tool_name(message.name),
                content=message.content.__str__(),
                call_id=message.tool_call_id,
                status=message.status,
                type=tool_type,
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
            result = await handler(request)

            if result.status == "success":
                logger.debug(f"Tool call {call.name} succeeded; id={call.id}")
            else:
                logger.debug(f"Tool call {call.name} failed; id={call.id}")

            return result
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
            result = await handler(request)

            if result.status == "success":
                logger.debug(f"Subagent call {call.name} succeeded; id={call.id}")
            else:
                logger.debug(f"Subagent call {call.name} failed; id={call.id}")

            return result
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
    async def _tool_call(**kwargs: dict[str, Any]) -> dict[str, Any] | list[str]:
        try:
            result = await tool.func(**kwargs)
        except ToolException as e:
            raise LC_ToolException(*e.args) from e
        except LC_ToolException:
            assert False, (  # noqa: PT015
                "ToolException from LangChain should not be raised in tool.func"
            )

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
            return asdict(result)  # both content + structured_content
        return result.content

    return StructuredTool(
        name=_normalize_tool_name(tool.name, tool.type),
        description=tool.description,
        args_schema=tool.input_schema,
        coroutine=_tool_call,
        response_format="content",
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

    if agent.input_schema is None:

        async def _run(content: str) -> str:  # pyright: ignore[reportRedeclaration]
            result = await agent.invoke([HumanMessage(content=content)])
            assert agent.output_schema is None
            return result.messages[-1].content

        return StructuredTool.from_function(
            coroutine=_run,
            name=_normalize_agent_name(agent.name),
            description=agent.description,
            infer_schema=True,
        )

    InputSchema = agent.input_schema

    async def _run(**kwargs: dict[str, Any]) -> OutputT | str:
        req = InputSchema(**kwargs)
        request_text = f"INPUT_JSON:\n{req.model_dump_json()}\n"

        result = await agent.invoke([HumanMessage(content=request_text)])
        if agent.output_schema:
            return result.structured_output
        return result.messages[-1].content

    return StructuredTool.from_function(
        coroutine=_run,
        name=_normalize_agent_name(agent.name),
        description=agent.description,
        args_schema=InputSchema,
    )


def _map_tool_call_from_langchain(tool_call: LC_ToolCall) -> ToolCall | SubagentCall:
    name = tool_call["name"]
    if name.startswith(AGENT_PREFIX):
        return SubagentCall(
            name=_denormalize_agent_name(name),
            args=tool_call["args"],
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
        case ToolCall():
            name = _normalize_tool_name(call.name, call.type)

    return LC_ToolCall(id=call.id, name=name, args=call.args)


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
                    """OpenAI support is not installed.\n\n
                    To enable OpenAI / ChatGPT models, install the optional extra:\n\n
                      pip install "splunk-sdk[openai]"\n
                      # or if using uv:\n
                      uv add splunk-sdk[openai]"""
                )
        case _:
            raise InvalidModelError(
                "Cannot create langchain model - invalid SDK model provided"
            )

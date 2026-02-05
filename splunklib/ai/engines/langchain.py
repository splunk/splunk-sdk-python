#
# Copyright © 2011-2025 Splunk, Inc.
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

import uuid
from collections.abc import Sequence
from dataclasses import dataclass
from functools import partial
from time import monotonic
from typing import Any, cast, override

from langchain.agents import create_agent
from langchain.agents.middleware import (
    AgentMiddleware,
    AgentState,
    before_model,
)
from langchain.agents.middleware.summarization import TokenCounter
from langchain.messages import AIMessage as LC_AIMessage
from langchain.messages import HumanMessage as LC_HumanMessage
from langchain.messages import SystemMessage as LC_SystemMessage
from langchain.messages import ToolCall as LC_ToolCall
from langchain.messages import ToolMessage as LC_ToolMessage
from langchain.tools import ToolException as LC_ToolException
from langchain_core.language_models import BaseChatModel
from langchain_core.messages.base import BaseMessage as LC_BaseMessage
from langchain_core.messages.utils import count_tokens_approximately
from langchain_core.tools import BaseTool, StructuredTool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.state import CompiledStateGraph, RunnableConfig
from langgraph.runtime import Runtime

from splunklib.ai.base_agent import BaseAgent
from splunklib.ai.core.backend import (
    AgentImpl,
    Backend,
    InvalidMessageTypeError,
    InvalidModelError,
    InvalidToolNameError,
)
from splunklib.ai.messages import (
    AgentCall,
    AgentResponse,
    AIMessage,
    BaseMessage,
    HumanMessage,
    OutputT,
    SubagentMessage,
    SystemMessage,
    ToolCall,
    ToolMessage,
)
from splunklib.ai.model import OpenAIModel, PredefinedModel
from splunklib.ai.stop_conditions import (
    StepsLimitExceededException,
    StopConditions,
    TimeoutExceededException,
    TokenLimitExceededException,
)
from splunklib.ai.tools import Tool, ToolException

AGENT_PREFIX = "agent-"

AGENT_AS_TOOLS_PROMPT = f"""
You are provided with Agents.
Agents are more advanced TOOLS, which start with "{AGENT_PREFIX}" prefix.

Do not call the tools if not needed.
"""

ANTHROPIC_CHAT_MODEL_TYPE = "anthropic-chat"


@dataclass
class LangChainAgentImpl(AgentImpl[OutputT]):
    _agent: CompiledStateGraph
    _thread_id: uuid.UUID
    _config: RunnableConfig
    _output_schema: type[OutputT] | None

    def __init__(
        self,
        system_prompt: str,
        model: BaseChatModel,
        tools: list[BaseTool],
        output_schema: type[OutputT] | None,
        middleware: Sequence[AgentMiddleware] | None = None,
    ) -> None:
        super().__init__()
        self._output_schema = output_schema
        self._thread_id = uuid.uuid4()
        self._config = {"configurable": {"thread_id": self._thread_id}}

        checkpointer = InMemorySaver()
        middleware = middleware or []

        self._agent = create_agent(
            model=model,
            tools=tools,
            system_prompt=system_prompt,
            checkpointer=checkpointer,
            response_format=output_schema,
            middleware=middleware,
        )

    @override
    async def invoke(self, messages: list[BaseMessage]) -> AgentResponse[OutputT]:
        langchain_msgs = [_map_message_to_langchain(m) for m in messages]

        # call the langchain agent
        result = await self._agent.ainvoke(
            {"messages": langchain_msgs},
            config=self._config,
        )

        sdk_msgs = [_map_message_from_langchain(m) for m in result["messages"]]

        # NOTE: The Agent puts it's response into the output schema.
        # The response object is valid and matches the model, however, the response might not always make sense
        # and it's up to developers to make sure the Agent responds with correct data.
        if self._output_schema:
            return AgentResponse(
                structured_output=result["structured_response"],
                messages=sdk_msgs,
            )

        # HACK: this let's us put the None in the structured_output field.
        # It also shows None as type of the field if no `output_schema`
        # was provided to the Agent class.
        return AgentResponse(structured_output=cast(OutputT, None), messages=sdk_msgs)


class LangChainBackend(Backend):
    def __init__(self): ...

    @override
    async def create_agent(
        self,
        agent: BaseAgent[OutputT],
    ) -> AgentImpl[OutputT]:
        model_impl = _create_langchain_model(agent.model)

        system_prompt = agent.system_prompt
        tools = [_create_langchain_tool(t) for t in agent.tools]

        if agent.agents:
            seen_names: set[str] = set()
            for subagent in agent.agents:
                # Call _agent_as_tool first, such that the empty name exception is
                # checked and raised first, before the duplicated name exception.
                tool = _agent_as_tool(subagent)

                if subagent.name in seen_names:
                    raise AssertionError(
                        f"Subagents share the same name: {subagent.name}"
                    )

                seen_names.add(subagent.name)
                tools.append(tool)

                system_prompt = AGENT_AS_TOOLS_PROMPT + "\n" + system_prompt

        middleware = []
        if agent.loop_stop_conditions:
            middleware.extend(
                _create_middleware(agent.loop_stop_conditions, model_impl)
            )

        return LangChainAgentImpl(
            system_prompt=system_prompt,
            model=model_impl,
            tools=tools,
            output_schema=agent.output_schema,
            middleware=middleware,
        )


def _create_langchain_tool(tool: Tool) -> BaseTool:
    async def _tool_call(
        **kwargs: dict[str, Any],
    ) -> tuple[list[str], dict[str, Any] | None]:
        try:
            result = await tool.func(**kwargs)
        except ToolException as e:
            raise LC_ToolException(*e.args) from e
        except LC_ToolException:
            assert False, (
                "ToolException from langchain should not be raised in tool.func"
            )

        return result.content, result.structured_content

    return StructuredTool(
        name=tool.name,
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
    # TODO: should we check for collisions here?
    # TODO: we shouldn't change the name here - only add a prefix.
    # We should validate the name when the Agent is created
    name = "-".join(name.strip().split())
    return f"{AGENT_PREFIX}{name}"


def _denormalize_agent_name(name: str) -> str:
    return name.removeprefix(AGENT_PREFIX)


def _agent_as_tool(agent: BaseAgent[OutputT]):
    if not agent.name:
        raise AssertionError("Agent must have a name to be used by other Agents")

    if agent.input_schema is None:

        async def _run(content: str) -> str:
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

    async def _run(**kwargs) -> OutputT | str:
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


def _map_tool_call_from_langchain(tool_call: LC_ToolCall) -> ToolCall | AgentCall:
    if tool_call["name"].startswith(AGENT_PREFIX):
        return AgentCall(
            name=_denormalize_agent_name(tool_call["name"]),
            args=tool_call["args"],
            id=tool_call["id"],
        )

    return ToolCall(
        name=tool_call["name"],
        args=tool_call["args"],
        id=tool_call["id"],
    )


def _map_tool_call_to_langchain(call: ToolCall | AgentCall) -> LC_ToolCall:
    if AGENT_PREFIX in call.name:
        raise InvalidToolNameError(
            f"ToolCall name cannot contain agent prefix: {call.name}"
        )

    name = call.name
    if isinstance(call, AgentCall):
        name = _normalize_agent_name(call.name)

    return LC_ToolCall(
        name=name,
        args=call.args,
        id=call.id,
    )


def _map_message_from_langchain(message: LC_BaseMessage) -> BaseMessage:
    match message:
        case LC_AIMessage():
            return AIMessage(
                content=str(message.content),
                calls=[_map_tool_call_from_langchain(tc) for tc in message.tool_calls],
            )
        case LC_HumanMessage():
            return HumanMessage(content=str(message.content))
        case LC_ToolMessage(name=name) if name and name.startswith(AGENT_PREFIX):
            return SubagentMessage(
                name=_denormalize_agent_name(name),
                content=str(message.content),
                call_id=message.tool_call_id,
                status=message.status,
            )
        case LC_ToolMessage():
            # If this is reached, this likely means that we passed an invalid
            # tool name to langchain.
            assert message.name is not None, (
                "langchain responded with a tool call that does not have a name"
            )
            return ToolMessage(
                name=message.name,
                content=str(message.content),
                call_id=message.tool_call_id,
                status=message.status,
            )
        case LC_SystemMessage():
            return SystemMessage(content=str(message.content))
        case _:
            raise InvalidMessageTypeError("Invalid langchain message type")


def _map_message_to_langchain(message: BaseMessage) -> LC_BaseMessage:
    match message:
        case AIMessage():
            lc_message = LC_AIMessage(content=message.content)
            # this field can't be set via constructor
            lc_message.tool_calls = [
                _map_tool_call_to_langchain(c) for c in message.calls
            ]
            return lc_message
        case HumanMessage():
            return LC_HumanMessage(content=message.content)
        case SubagentMessage():
            return LC_ToolMessage(
                name=_normalize_agent_name(message.name),
                content=message.content,
                tool_call_id=message.call_id,
                status=message.status,
            )
        case ToolMessage():
            return LC_ToolMessage(
                content=message.content,
                tool_call_id=message.call_id,
                name=message.name,
                status=message.status,
            )
        case SystemMessage():
            return LC_SystemMessage(content=message.content)
        case _:
            raise InvalidMessageTypeError("Invalid SDK message type")


def _create_middleware(
    stop_conditions: StopConditions, model: BaseChatModel
) -> list[AgentMiddleware]:
    middlewares: list[AgentMiddleware] = []

    if limit := stop_conditions.steps_limit:
        middlewares.append(_max_steps_middleware(step_limit=limit))

    if limit := stop_conditions.token_limit:
        middlewares.append(_token_count_middleware(token_limit=limit, model=model))

    if seconds := stop_conditions.timeout_seconds:
        middlewares.append(_timeout_middleware(seconds=seconds))

    return middlewares


def _timeout_middleware(seconds: float) -> AgentMiddleware:
    # NOTE: the timeout timestamp is calculated when the Middleware is created
    now = monotonic()
    timeout = now + seconds

    @before_model(can_jump_to=["end"])
    def _check_timeout(state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        if monotonic() >= timeout:
            raise TimeoutExceededException(seconds)

    return _check_timeout


def _max_steps_middleware(step_limit: int) -> AgentMiddleware:
    @before_model(can_jump_to=["end"])
    def _check_message_limit(
        state: AgentState, runtime: Runtime
    ) -> dict[str, Any] | None:
        if len(state["messages"]) >= step_limit:
            raise StepsLimitExceededException(step_limit)
        return None

    return _check_message_limit


def _token_count_middleware(token_limit: int, model: BaseChatModel) -> AgentMiddleware:
    @before_model(can_jump_to=["end"])
    def _check_token_limit(
        state: AgentState, runtime: Runtime
    ) -> dict[str, Any] | None:
        messages = state["messages"]
        total_tokens = _get_approximate_token_counter(model)

        if total_tokens(messages) > token_limit:
            raise TokenLimitExceededException(token_limit)
        return None

    return _check_token_limit


def _get_approximate_token_counter(model: BaseChatModel) -> TokenCounter:
    """Tune parameters of approximate token counter based on model type."""

    # NOTE: this is copied from langchain library
    if model._llm_type == ANTHROPIC_CHAT_MODEL_TYPE:
        # 3.3 was estimated in an offline experiment, comparing with Claude's token-counting
        # API: https://platform.claude.com/docs/en/build-with-claude/token-counting
        return partial(count_tokens_approximately, chars_per_token=3.3)
    return count_tokens_approximately


def _create_langchain_model(model: PredefinedModel) -> BaseChatModel:
    match model:
        case OpenAIModel():
            try:
                from langchain_openai import ChatOpenAI  # noqa: F401

                return ChatOpenAI(
                    model=model.model,
                    base_url=model.base_url,
                    api_key=model.api_key,
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

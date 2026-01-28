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

from collections.abc import Sequence
from dataclasses import dataclass
from functools import partial
from time import monotonic
from typing import Any, override, cast
import uuid

from langchain.agents import create_agent
from langchain.agents.middleware import (
    AgentMiddleware,
    before_model,
    AgentState,
)
from langchain.agents.middleware.summarization import TokenCounter
from langchain.tools import ToolException as LCToolException
from langchain_core.language_models import BaseChatModel
from langchain_core.tools import BaseTool, StructuredTool
from langgraph.graph.state import CompiledStateGraph, RunnableConfig
from langgraph.checkpoint.memory import InMemorySaver
from langchain.messages import AIMessage, ToolMessage
from langgraph.runtime import Runtime
from langchain_core.messages.utils import count_tokens_approximately


from splunklib.ai.core.backend import AgentImpl, Backend
from splunklib.ai.model import OpenAIModel, PredefinedModel
from splunklib.ai.types import (
    Message,
    Role,
    BaseAgent,
    AgentResponse,
    OutputT,
    StopConditions,
    TimeoutExceededException,
    StepsLimitExceededException,
    TokenLimitExceededException,
    Tool,
    ToolException,
)


AGENT_AS_TOOLS_PROMPT = """
You are provided with Agents.
Agents are more advanced TOOLS, which start with "agent-" prefix.

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
    async def invoke(self, messages: list[Message]) -> AgentResponse[OutputT]:
        # translate incoming messages to langchain
        langchain_msgs = [
            {
                "role": _map_role_to_langchain(message.role),
                "content": message.content,
            }
            for message in messages
        ]

        # call the langchain agent
        result = await self._agent.ainvoke(
            {"messages": langchain_msgs},
            config=self._config,
        )

        # translate the response from langchain to the SDK
        # TODO: really need to append only the new results - this could be a good optimisation
        sdk_msgs = [
            Message(
                role=_map_role_from_langchain(message.type),
                content=message.content,
            )
            for message in result["messages"]
        ]

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
            tools.extend([_agent_as_tool(a) for a in agent.agents])
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
            raise LCToolException(*e.args) from e
        except LCToolException as e:
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
    name = "-".join(name.strip().lower().split())
    return f"agent-{name}"


def _agent_as_tool(agent: BaseAgent[OutputT]):
    assert agent.name, "Agent must have a name to be used by other Agents"
    assert agent.input_schema, (
        "Agent must have an input schema to be used by other Agents"
    )

    InputSchema = agent.input_schema

    async def _run(**kwargs) -> OutputT | str:
        req = InputSchema(**kwargs)
        request_text = f"INPUT_JSON:\n{req.model_dump_json()}\n"

        result = await agent.invoke([Message(role="user", content=request_text)])
        if agent.output_schema:
            return result.structured_output
        return result.messages[-1].content

    return StructuredTool.from_function(
        coroutine=_run,
        name=_normalize_agent_name(agent.name),
        description=agent.description,
        args_schema=InputSchema,
    )


def _map_role_from_langchain(role: str) -> Role:
    match role:
        case "human":
            return "user"
        case "system":
            return "system"
        case "ai":
            return "assistant"
        case "tool":
            return "tool"
        case _:
            raise Exception("Invalid langchain message type")


def _map_role_to_langchain(role: Role) -> str:
    match role:
        case "user":
            return "human"
        case "system":
            return "system"
        case "assistant":
            return "ai"
        case "tool":
            return "tool"


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
            raise Exception(
                "Cannot create langchain model - invalid SDK model provided"
            )

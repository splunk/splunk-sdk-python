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

from dataclasses import dataclass
from typing import override, cast
import uuid

from langchain.agents import create_agent
from langchain_core.language_models import BaseChatModel
from langchain_core.tools import BaseTool, StructuredTool
from langgraph.graph.state import CompiledStateGraph, RunnableConfig
from langgraph.checkpoint.memory import InMemorySaver

from splunklib.ai.core.backend import AgentImpl, Backend
from splunklib.ai.model import OllamaModel, OpenAIModel, PredefinedModel
from splunklib.ai.types import Message, Role, BaseAgent, AgentResponse, OutputT


AGENT_AS_TOOLS_PROMPT = """
You are provided with Agents.
Agents are more advanced TOOLS, which start with "agent-" prefix.

Do not call the tools if not needed.
"""


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
    ) -> None:
        super().__init__()
        self._output_schema = output_schema
        self._thread_id = uuid.uuid4()
        self._config = {"configurable": {"thread_id": self._thread_id}}

        checkpointer = InMemorySaver()

        self._agent = create_agent(
            model=model,
            tools=tools,
            system_prompt=system_prompt,
            checkpointer=checkpointer,
            response_format=output_schema,
        )

    @override
    def invoke(self, messages: list[Message]) -> AgentResponse[OutputT]:
        # translate incoming messages to langchain
        langchain_msgs = [
            {
                "role": _map_role_to_langchain(message.role),
                "content": message.content,
            }
            for message in messages
        ]

        # call the langchain agent
        result = self._agent.invoke(
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
    def create_agent(
        self,
        agent: BaseAgent[OutputT],
    ) -> AgentImpl[OutputT]:
        model_impl = _create_langchain_model(agent._model)

        system_prompt = agent._system_prompt
        tools = agent._tools.copy()

        if agent._agents:
            tools.extend([_agent_as_tool(a) for a in agent._agents])
            system_prompt = AGENT_AS_TOOLS_PROMPT + "\n" + system_prompt

        return LangChainAgentImpl(
            system_prompt=system_prompt,
            model=model_impl,
            tools=tools,
            output_schema=agent._output_schema,
        )


def langchain_backend_factory() -> LangChainBackend:
    return LangChainBackend()


def _normalize_agent_name(name: str) -> str:
    # TODO: should we check for collisions here?
    name = "-".join(name.strip().lower().split())
    return f"agent-{name}"


def _agent_as_tool(agent: BaseAgent[OutputT]):
    assert agent._name, "Agent must have a name to be used by other Agents"
    assert agent._input_schema, (
        "Agent must have an input schema to be used by other Agents"
    )

    InputSchema = agent._input_schema

    def _run(**kwargs) -> OutputT | str:
        req = InputSchema(**kwargs)
        request_text = f"INPUT_JSON:\n{req.model_dump_json()}\n"

        result = agent.invoke([Message(role="user", content=request_text)])
        if agent._output_schema:
            return result.structured_output
        return result.messages[-1].content

    return StructuredTool.from_function(
        func=_run,
        name=_normalize_agent_name(agent._name),
        description=agent._description,
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


def _create_langchain_model(model: PredefinedModel) -> BaseChatModel:
    match model:
        case OpenAIModel():
            try:
                from langchain_openai import ChatOpenAI  # noqa: F401

                return ChatOpenAI(
                    model=model.model,
                )
            except ImportError:
                raise ImportError(
                    """OpenAI support is not installed.\n\n
                    To enable OpenAI / ChatGPT models, install the optional extra:\n\n
                      pip install "splunk-sdk[openai]"\n
                      # or if using uv:\n
                      uv add splunk-sdk[openai]"""
                )
        case OllamaModel():
            try:
                from langchain_ollama import ChatOllama  # noqa: F401

                return ChatOllama(
                    model=model.model,
                    base_url=model.base_url,
                )
            except ImportError:
                raise ImportError(
                    """Ollama support is not installed.\n\n
                    To enable Ollama models, install the optional extra:\n\n
                      pip install "splunk-sdk[ollama]"\n
                      # or if using uv:\n
                      uv add splunk-sdk[ollama]"""
                )
        case _:
            raise Exception(
                "Cannot create langchain model - invalid SDK model provided"
            )

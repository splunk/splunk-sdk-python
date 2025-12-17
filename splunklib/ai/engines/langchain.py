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

from typing import override
from dataclasses import dataclass

from splunklib.ai.core.backend import Backend, AgentImpl
from splunklib.ai.types import Message, Role
from splunklib.ai.tool import Tool
from splunklib.ai.model import PredefinedModel, OpenAIModel, OllamaModel

from langchain.agents import create_agent
from langchain_core.language_models import BaseChatModel
from langchain_core.tools import BaseTool, StructuredTool
from langgraph.graph.state import CompiledStateGraph

from pydantic import BaseModel


@dataclass
class LangChainAgentImpl(AgentImpl):
    agent: CompiledStateGraph

    def __init__(
        self, system_prompt: str, model: BaseChatModel, tools: list[BaseTool]
    ) -> None:
        super().__init__()

        self.agent = create_agent(
            model=model,
            tools=tools,
            system_prompt=system_prompt,
        )

    @override
    def invoke(self, messages: list[Message]) -> list[Message]:
        # translate incoming messages to langchain
        langchain_msgs = [
            {
                "role": _map_role_to_langchain(message.role),
                "content": message.content,
            }
            for message in messages
        ]

        # call the langchain agent
        result = self.agent.invoke({"messages": langchain_msgs})

        # translate the response from langchain to the SDK
        # TODO: really need to append only the new results - this could be a good optimisation
        sdk_msgs = [
            Message(
                role=_map_role_from_langchain(message.type),
                content=message.content,
            )
            for message in result["messages"]
        ]

        return sdk_msgs


class LangChainBackend(Backend):
    def __init__(self): ...

    @override
    def create_agent(
        self,
        model: PredefinedModel,
        system_prompt: str,
        tools: list[Tool],
        output_schema: BaseModel | None,
        input_schema: BaseModel | None,
    ) -> AgentImpl:
        model_impl = _create_langchain_model(model)

        # NOTE: this is temporary, in the future we will use MCP even for local tools.
        _tools = [StructuredTool.from_function(tool.func) for tool in tools]

        return LangChainAgentImpl(
            system_prompt=system_prompt,
            model=model_impl,
            tools=_tools,
        )


def langchain_backend_factory() -> LangChainBackend:
    return LangChainBackend()


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

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
from dataclasses import dataclass, field
from typing import Literal, TypeVar, Generic

from langchain_core.tools import BaseTool
from pydantic import BaseModel
from splunklib.ai.model import PredefinedModel
from abc import ABC, abstractmethod

Role = Literal["system", "user", "assistant", "tool"]

OutputT = TypeVar("OutputT", default=None, covariant=True, bound=BaseModel | None)


@dataclass(frozen=True)
class Message:
    role: Role
    content: str


@dataclass(frozen=True)
class AgentResponse(Generic[OutputT]):
    # in case output_schema is provided, this will hold the parsed structured output
    structured_output: OutputT
    # Holds the full message history including tool calls and final response
    messages: list[Message] = field(default_factory=list)


class BaseAgent(Generic[OutputT], ABC):
    _system_prompt: str
    _model: PredefinedModel
    _tools: Sequence[BaseTool]
    _agents: Sequence["BaseAgent[BaseModel | None]"]
    _name: str = ""
    _description: str = ""
    _input_schema: type[BaseModel] | None = None
    _output_schema: type[OutputT] | None = None

    def __init__(
        self,
        system_prompt: str,
        model: PredefinedModel,
        description: str = "",
        name: str = "",
        tools: Sequence[BaseTool] | None = None,
        agents: Sequence["BaseAgent[BaseModel | None]"] | None = None,
        input_schema: type[BaseModel] | None = None,
        output_schema: type[OutputT] | None = None,
    ):
        self._system_prompt = system_prompt
        self._model = model
        self._name = name
        self._description = description
        # TODO: Backend should not be coupled to the BaseTool from langchain.
        #       We need to come up and create an abstraction for Tools, that can be used
        #       by backend and custom models.
        #       This field is now private, but should be exposed when this TODO is finished.
        self._tools = tuple(tools) if tools else ()
        self._agents = tuple(agents) if agents else ()
        self._input_schema = input_schema
        self._output_schema = output_schema

    @abstractmethod
    async def invoke(self, messages: list[Message]) -> AgentResponse[OutputT]: ...

    @property
    def system_prompt(self) -> str:
        return self._system_prompt

    @property
    def model(self) -> PredefinedModel:
        return self._model

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    def agents(self) -> Sequence["BaseAgent[BaseModel | None]"]:
        return self._agents

    @property
    def input_schema(self) -> type[BaseModel] | None:
        return self._input_schema

    @property
    def output_schema(self) -> type[OutputT] | None:
        return self._output_schema

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


@dataclass
class Message:
    role: Role
    content: str


@dataclass
class AgentResponse(Generic[OutputT]):
    # in case output_schema is provided, this will hold the parsed structured output
    structured_output: OutputT
    # Holds the full message history including tool calls and final response
    messages: list[Message] = field(default_factory=list)


class BaseAgent(Generic[OutputT], ABC):
    # TODO: create getters for the fields used in backend code
    _system_prompt: str
    _model: PredefinedModel
    _tools: list[BaseTool]
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
        tools: list[BaseTool] | None = None,
        agents: Sequence["BaseAgent[BaseModel | None]"] | None = None,
        input_schema: type[BaseModel] | None = None,
        output_schema: type[OutputT] | None = None,
    ):
        self._system_prompt = system_prompt
        self._model = model
        self._name = name
        self._description = description
        self._tools = tools or []
        self._agents = agents or []
        self._input_schema = input_schema
        self._output_schema = output_schema

    @abstractmethod
    async def invoke(self, messages: list[Message]) -> AgentResponse[OutputT]: ...

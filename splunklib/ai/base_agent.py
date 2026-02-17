#
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

from abc import ABC, abstractmethod
from collections.abc import Sequence
import secrets
from typing import Generic

from pydantic import BaseModel

from splunklib.ai.hooks import AgentHook
from splunklib.ai.messages import AgentResponse, BaseMessage, OutputT
from splunklib.ai.model import PredefinedModel
from splunklib.ai.tools import Tool


class BaseAgent(Generic[OutputT], ABC):
    _system_prompt: str
    _model: PredefinedModel
    _tools: Sequence[Tool]
    _agents: Sequence["BaseAgent[BaseModel | None]"]
    _name: str = ""
    _description: str = ""
    _input_schema: type[BaseModel] | None = None
    _output_schema: type[OutputT] | None = None
    _hooks: Sequence[AgentHook] | None = None
    _trace_id: str

    def __init__(
        self,
        system_prompt: str,
        model: PredefinedModel,
        description: str = "",
        name: str = "",
        tools: Sequence[Tool] | None = None,
        agents: Sequence["BaseAgent[BaseModel | None]"] | None = None,
        input_schema: type[BaseModel] | None = None,
        output_schema: type[OutputT] | None = None,
        hooks: Sequence[AgentHook] | None = None,
    ) -> None:
        self._system_prompt = system_prompt
        self._model = model
        self._name = name
        self._description = description
        self._tools = tuple(tools) if tools else ()
        self._agents = tuple(agents) if agents else ()
        self._input_schema = input_schema
        self._output_schema = output_schema
        self._hooks = tuple(hooks) if hooks else ()
        self._trace_id = secrets.token_hex(16)  # 32 Hex characters

    @abstractmethod
    async def invoke(self, messages: list[BaseMessage]) -> AgentResponse[OutputT]: ...

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
    def tools(self) -> Sequence[Tool]:
        return self._tools

    @property
    def agents(self) -> Sequence["BaseAgent[BaseModel | None]"]:
        return self._agents

    @property
    def input_schema(self) -> type[BaseModel] | None:
        return self._input_schema

    @property
    def output_schema(self) -> type[OutputT] | None:
        return self._output_schema

    @property
    def hooks(self) -> Sequence[AgentHook] | None:
        return self._hooks

    @property
    def trace_id(self) -> str:
        return self._trace_id

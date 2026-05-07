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
import secrets
from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Any, Generic

from pydantic import BaseModel

from splunklib.ai.conversation_store import ConversationStore
from splunklib.ai.limits import (
    AgentLimits,
)
from splunklib.ai.messages import AgentResponse, BaseMessage, OutputT
from splunklib.ai.middleware import AgentMiddleware
from splunklib.ai.model import PredefinedModel
from splunklib.ai.tool_settings import ToolSettings
from splunklib.ai.tools import Tool


class BaseAgent(Generic[OutputT], ABC):  # noqa: UP046 TODO[BJ]
    _system_prompt: str
    _model: PredefinedModel
    _tools: Sequence[Tool]
    _tool_settings: ToolSettings
    _agents: Sequence["BaseAgent[BaseModel | None]"]
    _name: str = ""
    _description: str = ""
    _input_schema: type[BaseModel] | None = None
    _output_schema: type[OutputT] | None = None
    _middleware: Sequence[AgentMiddleware] | None = None
    _trace_id: str
    _logger: logging.Logger
    _conversation_store: ConversationStore | None = None
    _thread_id: str
    _limits: AgentLimits

    def __init__(
        self,
        system_prompt: str,
        model: PredefinedModel,
        tool_settings: ToolSettings,
        description: str,
        name: str,
        tools: Sequence[Tool] | None,
        agents: Sequence["BaseAgent[BaseModel | None]"] | None,
        input_schema: type[BaseModel] | None,
        output_schema: type[OutputT] | None,
        middleware: Sequence[AgentMiddleware] | None,
        logger: logging.Logger | None,
        conversation_store: ConversationStore | None,
        thread_id: str,
        limits: AgentLimits,
    ) -> None:
        self._system_prompt = system_prompt
        self._model = model
        self._name = name
        self._description = description
        self._tools = tuple(tools) if tools else ()
        self._tool_settings = tool_settings
        self._agents = tuple(agents) if agents else ()
        self._input_schema = input_schema
        self._output_schema = output_schema
        self._limits = limits
        self._middleware = middleware
        self._trace_id = secrets.token_hex(16)  # 32 Hex characters
        self._conversation_store = conversation_store
        self._thread_id = thread_id

        if logger is None:
            # Create a no-op logger to skip checking for its existence.
            logger = logging.Logger(name="fake", level=logging.CRITICAL + 100)
            assert len(logger.handlers) == 0
        self._logger = logger

    @abstractmethod
    async def invoke(
        self, messages: list[BaseMessage], thread_id: str | None = None
    ) -> AgentResponse[OutputT]: ...

    @abstractmethod
    async def invoke_with_data(
        self,
        instructions: str,
        data: str | dict[str, Any],
        thread_id: str | None = None,
    ) -> AgentResponse[OutputT]: ...

    @property
    def logger(self) -> logging.Logger:
        return self._logger

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
    def middleware(self) -> Sequence[AgentMiddleware] | None:
        return self._middleware

    @property
    def trace_id(self) -> str:
        return self._trace_id

    @property
    def tool_settings(self) -> ToolSettings:
        return self._tool_settings

    @property
    def conversation_store(self) -> ConversationStore | None:
        return self._conversation_store

    @property
    def default_thread_id(self) -> str:
        return self._thread_id

    @property
    def limits(self) -> AgentLimits:
        return self._limits

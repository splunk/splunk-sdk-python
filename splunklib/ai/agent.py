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

import os
from collections.abc import Sequence
from contextlib import AbstractAsyncContextManager
from typing import override

from pydantic import BaseModel

from splunklib.ai.core.backend import AgentImpl
from splunklib.ai.core.backend_registry import get_backend
from splunklib.ai.model import PredefinedModel
from splunklib.ai.tools import load_mcp_tools, locate_tools_path_by_sdk_location
from splunklib.ai.types import (
    AgentResponse,
    BaseAgent,
    Message,
    OutputT,
    StopConditions,
    Tool,
)
from splunklib.client import Service

# For testing purposes, overrides the automatically inferred tools.py path.
_testing_local_tools_path: str | None = None


class Agent(BaseAgent[OutputT], AbstractAsyncContextManager):
    _use_mcp_tools: bool
    _service: Service

    # TODO: We should have a logger inside of an agent, debugging and such.

    def __init__(
        self,
        model: PredefinedModel,
        system_prompt: str,
        service: Service,
        use_mcp_tools: bool = False,  # TODO: should we default to True?
        agents: Sequence[BaseAgent[BaseModel | None]] | None = None,
        output_schema: type[OutputT] | None = None,
        input_schema: type[BaseModel] | None = None,
        loop_stop_conditions: StopConditions | None = None,
        name: str = "",  # Only used by Subgents
        description: str = "",  # Only used by Subagents
    ) -> None:
        super().__init__(
            model=model,
            system_prompt=system_prompt,
            name=name,
            description=description,
            agents=agents,
            input_schema=input_schema,
            output_schema=output_schema,
            loop_stop_conditions=loop_stop_conditions,
        )

        self._use_mcp_tools = use_mcp_tools
        self._service = service
        self._impl = None

    @override
    async def __aenter__(self):
        # TODO: replace these with if && raise
        # See: https://docs.python.org/3/reference/simple_stmts.html#the-assert-statement
        assert self._impl is None, "Agent is already in `async with` context"

        if self._use_mcp_tools:
            self._tools = await _load_tools_from_mcp(self._service)

        backend = get_backend()
        self._impl: AgentImpl[OutputT] | None = await backend.create_agent(self)

        return self

    @override
    async def __aexit__(self, exc_type, exc_value, traceback):
        self._impl = None  # Make sure invoke fails if called after exit.
        return None

    @override
    async def invoke(self, messages: list[Message]) -> AgentResponse[OutputT]:
        assert self._impl is not None, "Agent must be used inside 'async with'"
        return await self._impl.invoke(messages)


async def _load_tools_from_mcp(
    service: Service,
) -> list[Tool]:
    local_tools_path = _testing_local_tools_path
    if local_tools_path is None:
        local_tools_path = locate_tools_path_by_sdk_location()

    if not os.path.exists(local_tools_path):
        local_tools_path = None

    return await load_mcp_tools(service, local_tools_path)

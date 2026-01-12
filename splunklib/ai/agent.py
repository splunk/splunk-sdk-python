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

import asyncio
from collections.abc import Sequence
import os
from typing import override

from langchain_core.tools import BaseTool
from pydantic import BaseModel

from splunklib.ai.core.backend import AgentImpl
from splunklib.ai.core.backend_registry import get_backend
from splunklib.ai.model import PredefinedModel
from splunklib.ai.tools import load_mcp_tools, locate_tools_path_by_sdk_location
from splunklib.ai.types import BaseAgent, Message, AgentResponse, OutputT
from splunklib.client import Service

# For testing purposes, overrides the automatically inferred tools.py path.
_testing_local_tools_path: str | None = None


class Agent(BaseAgent[OutputT]):
    _use_mcp_tools: bool

    def __init__(
        self,
        model: PredefinedModel,
        system_prompt: str,
        use_mcp_tools: bool = False,
        service: Service | None = None,  # TODO: make it non-optional.
        agents: Sequence[BaseAgent[BaseModel | None]] | None = None,
        output_schema: type[OutputT] | None = None,
        input_schema: type[BaseModel] | None = None,
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
        )

        self._use_mcp_tools = use_mcp_tools
        if self._use_mcp_tools:
            self._tools = _load_tools_from_mcp(service)

        backend = get_backend()
        self._impl: AgentImpl[OutputT] = backend.create_agent(self)

    @override
    def invoke(self, messages: list[Message]) -> AgentResponse[OutputT]:
        return self._impl.invoke(messages)


def _load_tools_from_mcp(
    service: Service | None,
) -> list[BaseTool]:
    lc_tools: list[BaseTool] = []

    local_tools_path = _testing_local_tools_path
    if local_tools_path is None:
        local_tools_path = locate_tools_path_by_sdk_location()

    if os.path.exists(local_tools_path):
        # TODO: we should make the Agent async, and drop the asyncio.run call.
        # So that constructor does not have any side effects, we could also load tools
        # lazily on first use (or in __aenter__).
        lc_tools = asyncio.run(load_mcp_tools(service, local_tools_path))

    return lc_tools

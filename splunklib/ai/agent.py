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
import os

from langchain_core.tools import BaseTool
from pydantic import BaseModel

from splunklib.ai.core.backend import AgentImpl
from splunklib.ai.core.backend_registry import get_backend
from splunklib.ai.model import PredefinedModel
from splunklib.ai.tools import load_mcp_tools, locate_tools_path_by_sdk_location
from splunklib.ai.types import Message
from splunklib.client import Service

# For testing purposes, overrides the automatically inferred tools.py path.
_testing_local_tools_path: str | None = None


class Agent:
    _system_prompt: str
    _use_mcp_tools: bool
    _output_schema: BaseModel | None
    _input_schema: BaseModel | None

    def __init__(
        self,
        model: PredefinedModel,
        system_prompt: str,
        use_mcp_tools: bool = False,
        service: Service | None = None,  # TODO: make it non-optional.
        output_schema: BaseModel | None = None,
        input_schema: BaseModel | None = None,
    ) -> None:
        self._system_prompt = system_prompt
        self._use_mcp_tools = use_mcp_tools
        self._output_schema = output_schema
        self._input_schema = input_schema

        lc_tools: list[BaseTool] = []
        if self._use_mcp_tools:
            local_tools_path = _testing_local_tools_path
            if local_tools_path is None:
                local_tools_path = locate_tools_path_by_sdk_location()

            if os.path.exists(local_tools_path):
                # TODO: we should make the Agent async, and drop the asyncio.run call.
                # So that constructor does not have any side effects, we could also load tools
                # lazily on first use (or in __aenter__).
                lc_tools = asyncio.run(load_mcp_tools(service, local_tools_path))

        backend = get_backend()

        self._impl: AgentImpl = backend.create_agent(
            model,
            system_prompt,
            lc_tools,
            output_schema,
            input_schema,
        )

    def invoke(self, messages: list[Message]) -> list[Message]:
        return self._impl.invoke(messages)

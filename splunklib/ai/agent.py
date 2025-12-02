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

from splunklib.ai.types import Message
from splunklib.ai.tool import Tool
from splunklib.ai.core.backend_registry import get_backend
from splunklib.ai.core.backend import AgentImpl
from splunklib.ai.model import PredefinedModel

from pydantic import BaseModel


class Agent:
    _system_prompt: str
    # NOTE: passing tools explicitly will be removed in the future.
    # Leaving it for now for testing purposes.
    _tools: list[Tool]
    # TODO: add support for this in langchain backend
    _use_mcp_tools: bool
    _output_schema: BaseModel | None
    _input_schema: BaseModel | None

    def __init__(
        self,
        model: PredefinedModel,
        system_prompt: str,
        tools: list[Tool] | None = None,
        use_mcp_tools: bool = True,
        output_schema: BaseModel | None = None,
        input_schema: BaseModel | None = None,
    ) -> None:
        self._system_prompt = system_prompt
        # TODO: load tools from MCP Server here
        self._tools = tools or []
        self._use_mcp_tools = use_mcp_tools
        self._output_schema = output_schema
        self._input_schema = input_schema

        backend = get_backend()

        self._impl: AgentImpl = backend.create_agent(
            model,
            system_prompt,
            self._tools,
            output_schema,
            input_schema,
        )

    def invoke(self, messages: list[Message]) -> list[Message]:
        return self._impl.invoke(messages)

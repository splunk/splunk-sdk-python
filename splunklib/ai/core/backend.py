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

from typing import Protocol

from langchain_core.tools import BaseTool
from pydantic import BaseModel

from splunklib.ai.model import PredefinedModel
from splunklib.ai.types import Message


class AgentImpl(Protocol):
    """Backend-specific agent implementation used by the public `Agent` wrapper."""

    def invoke(self, messages: list[Message]) -> list[Message]: ...


class Backend(Protocol):
    """
    Abstraction layer for engine-specific agent backends.
    """

    def create_agent(
        self,
        model: PredefinedModel,
        system_prompt: str,
        # TODO: Backend should not be coupled to the BaseTool from langchain.
        #       We need to come up and create an abstraction for Tools, that can be used
        #       by backend and custom models.
        tools: list[BaseTool],
        output_schema: BaseModel | None,
        input_schema: BaseModel | None,
    ) -> AgentImpl: ...

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

from typing import Protocol

from splunklib.ai.base_agent import BaseAgent
from splunklib.ai.messages import AgentResponse, BaseMessage, OutputT


class InvalidModelError(Exception):
    """Raised when an invalid model is specified for a backend."""


class InvalidMessageTypeError(Exception):
    """Raised when a message type is not supported by the backend."""


class AgentImpl(Protocol[OutputT]):
    """Backend-specific agent implementation used by the public `Agent` wrapper."""

    async def invoke(
        self, messages: list[BaseMessage], thread_id: str
    ) -> AgentResponse[OutputT]: ...


class Backend(Protocol):
    """
    Abstraction layer for engine-specific agent backends.
    """

    async def create_agent(
        self,
        agent: BaseAgent[OutputT],
    ) -> AgentImpl[OutputT]: ...

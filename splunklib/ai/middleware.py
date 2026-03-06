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

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any, Literal, override

from splunklib.ai.messages import (
    AIMessage,
    AgentResponse,
    BaseMessage,
    SubagentCall,
    ToolCall,
)


@dataclass(frozen=True)
class AgentState:
    """AgentState is passed to middleware and contains information about the current state of the agent execution."""

    # holds messages exchanged so far in the conversation
    response: AgentResponse[Any | None]
    # steps taken so far in the conversation
    total_steps: int
    # tokens used so far in the conversation
    token_count: float


@dataclass
class ToolRequest:
    call: ToolCall
    state: AgentState


@dataclass
class ToolResponse:
    content: str
    status: Literal["success", "error"] = "success"


ToolMiddlewareHandler = Callable[[ToolRequest], Awaitable[ToolResponse]]


@dataclass
class SubagentRequest:
    call: SubagentCall
    state: AgentState


@dataclass
class SubagentResponse:
    content: str
    status: Literal["success", "error"] = "success"


SubagentMiddlewareHandler = Callable[[SubagentRequest], Awaitable[SubagentResponse]]


@dataclass
class ModelRequest:
    system_message: str
    state: AgentState


ModelMiddlewareHandler = Callable[[ModelRequest], Awaitable[AIMessage]]


@dataclass
class AgentRequest:
    messages: list[BaseMessage]


AgentMiddlewareHandler = Callable[[AgentRequest], Awaitable[AgentResponse[Any | None]]]


class AgentMiddleware:
    async def tool_middleware(
        self,
        request: ToolRequest,
        handler: ToolMiddlewareHandler,
    ) -> ToolResponse:
        """Executed in between tool calls"""

        return await handler(request)

    async def subagent_middleware(
        self,
        request: SubagentRequest,
        handler: SubagentMiddlewareHandler,
    ) -> SubagentResponse:
        """Executed in between subagent calls"""

        return await handler(request)

    async def model_middleware(
        self,
        request: ModelRequest,
        handler: ModelMiddlewareHandler,
    ) -> AIMessage:
        """Executed in between the LLM calls"""

        return await handler(request)

    async def agent_middleware(
        self,
        request: AgentRequest,
        handler: AgentMiddlewareHandler,
    ) -> AgentResponse[Any | None]:
        """Executed in between invoke"""

        return await handler(request)


def tool_middleware(
    func: Callable[[ToolRequest, ToolMiddlewareHandler], Awaitable[ToolResponse]],
) -> AgentMiddleware:
    class _CustomMiddleware(AgentMiddleware):
        @override
        async def tool_middleware(
            self,
            request: ToolRequest,
            handler: ToolMiddlewareHandler,
        ) -> ToolResponse:
            return await func(request, handler)

    return _CustomMiddleware()


def subagent_middleware(
    func: Callable[
        [SubagentRequest, SubagentMiddlewareHandler], Awaitable[SubagentResponse]
    ],
) -> AgentMiddleware:
    class _CustomMiddleware(AgentMiddleware):
        @override
        async def subagent_middleware(
            self,
            request: SubagentRequest,
            handler: SubagentMiddlewareHandler,
        ) -> SubagentResponse:
            return await func(request, handler)

    return _CustomMiddleware()


def model_middleware(
    func: Callable[[ModelRequest, ModelMiddlewareHandler], Awaitable[AIMessage]],
) -> AgentMiddleware:
    class _CustomMiddleware(AgentMiddleware):
        @override
        async def model_middleware(
            self,
            request: ModelRequest,
            handler: ModelMiddlewareHandler,
        ) -> AIMessage:
            return await func(request, handler)

    return _CustomMiddleware()


def agent_middleware(
    func: Callable[
        [AgentRequest, AgentMiddlewareHandler], Awaitable[AgentResponse[Any | None]]
    ],
) -> AgentMiddleware:
    class _CustomMiddleware(AgentMiddleware):
        @override
        async def agent_middleware(
            self,
            request: AgentRequest,
            handler: AgentMiddlewareHandler,
        ) -> AgentResponse[Any | None]:
            return await func(request, handler)

    return _CustomMiddleware()

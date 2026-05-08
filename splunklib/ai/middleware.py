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

from collections.abc import Awaitable, Callable, Sequence
from dataclasses import dataclass
from typing import Any, override

from splunklib.ai.messages import (
    AgentResponse,
    AIMessage,
    BaseMessage,
    SubagentCall,
    SubagentFailureResult,
    SubagentStructuredResult,
    SubagentTextResult,
    ToolCall,
    ToolFailureResult,
    ToolResult,
)


@dataclass(frozen=True, kw_only=True)
class AgentState:
    """AgentState is available through certain middlewares and contains information about the current state of an agent execution."""

    # holds messages exchanged so far in the conversation
    messages: Sequence[BaseMessage]

    thread_id: str


@dataclass(frozen=True, kw_only=True)
class ToolRequest:
    call: ToolCall
    state: AgentState


@dataclass(frozen=True, kw_only=True)
class ToolResponse:
    result: ToolResult | ToolFailureResult


ToolMiddlewareHandler = Callable[[ToolRequest], Awaitable[ToolResponse]]


@dataclass(frozen=True, kw_only=True)
class SubagentRequest:
    call: SubagentCall
    state: AgentState


@dataclass(frozen=True, kw_only=True)
class SubagentResponse:
    result: SubagentStructuredResult | SubagentTextResult | SubagentFailureResult


SubagentMiddlewareHandler = Callable[
    [SubagentRequest],
    Awaitable[SubagentResponse],
]


@dataclass(frozen=True, kw_only=True)
class ModelRequest:
    system_message: str
    state: AgentState


@dataclass(frozen=True, kw_only=True)
class ModelResponse:
    message: AIMessage
    structured_output: Any | None = None

    def __post_init__(self) -> None:
        if len(self.message.structured_output_calls) > 1:
            raise AssertionError(
                f"len(message.structured_output_calls) is not equal to 0 or 1 but {len(self.message.structured_output_calls)}"
            )


ModelMiddlewareHandler = Callable[[ModelRequest], Awaitable[ModelResponse]]


@dataclass(frozen=True, kw_only=True)
class AgentRequest:
    messages: Sequence[BaseMessage]
    thread_id: str


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
    ) -> ModelResponse:
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
        [SubagentRequest, SubagentMiddlewareHandler],
        Awaitable[SubagentResponse],
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
    func: Callable[[ModelRequest, ModelMiddlewareHandler], Awaitable[ModelResponse]],
) -> AgentMiddleware:
    class _CustomMiddleware(AgentMiddleware):
        @override
        async def model_middleware(
            self,
            request: ModelRequest,
            handler: ModelMiddlewareHandler,
        ) -> ModelResponse:
            return await func(request, handler)

    return _CustomMiddleware()


def agent_middleware(
    func: Callable[[AgentRequest, AgentMiddlewareHandler], Awaitable[AgentResponse[Any | None]]],
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

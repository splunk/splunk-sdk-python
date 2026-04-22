import inspect
from collections.abc import Awaitable, Callable
from time import monotonic
from typing import Any, override

from splunklib.ai.messages import AgentResponse
from splunklib.ai.middleware import (
    AgentMiddleware,
    AgentMiddlewareHandler,
    AgentRequest,
    ModelMiddlewareHandler,
    ModelRequest,
    ModelResponse,
)

DEFAULT_TIMEOUT_SECONDS: float = 600.0
DEFAULT_STEP_LIMIT: int = 100
DEFAULT_TOKEN_LIMIT: int = 200_000


class AgentStopException(Exception):
    """Custom exception to indicate conversation stopping conditions."""


class TokenLimitExceededException(AgentStopException):
    """Raised by `Agent.invoke`, when token limit exceeds"""

    def __init__(self, token_limit: float) -> None:
        super().__init__(f"Token limit of {token_limit} exceeded.")


class StepsLimitExceededException(AgentStopException):
    """Raised by `Agent.invoke`, when steps limit exceeds"""

    def __init__(self, steps_limit: int) -> None:
        super().__init__(f"Steps limit of {steps_limit} exceeded.")


class TimeoutExceededException(AgentStopException):
    """Raised by `Agent.invoke`, when timeout exceeds"""

    def __init__(self, timeout_seconds: float) -> None:
        super().__init__(f"Timed out after {timeout_seconds} seconds.")


def before_model(
    func: Callable[[ModelRequest], None | Awaitable[None]],
) -> AgentMiddleware:
    """This hook is called before each model call."""

    class _Middleware(AgentMiddleware):
        @override
        async def model_middleware(
            self,
            request: ModelRequest,
            handler: ModelMiddlewareHandler,
        ) -> ModelResponse:
            res = func(request)
            if inspect.isawaitable(res):
                await res
            return await handler(request)

    return _Middleware()


def after_model(
    func: Callable[[ModelResponse], None | Awaitable[None]],
) -> AgentMiddleware:
    """This hook is called after each model call."""

    class _Middleware(AgentMiddleware):
        @override
        async def model_middleware(
            self,
            request: ModelRequest,
            handler: ModelMiddlewareHandler,
        ) -> ModelResponse:
            handler_response = await handler(request)
            res = func(handler_response)
            if inspect.isawaitable(res):
                await res
            return handler_response

    return _Middleware()


def before_agent(
    func: Callable[[AgentRequest], None | Awaitable[None]],
) -> AgentMiddleware:
    """This hook is called once per agent invocation. Before any model calls."""

    class _Middleware(AgentMiddleware):
        @override
        async def agent_middleware(
            self,
            request: AgentRequest,
            handler: AgentMiddlewareHandler,
        ) -> AgentResponse[Any | None]:
            res = func(request)
            if inspect.isawaitable(res):
                await res
            return await handler(request)

    return _Middleware()


def after_agent(
    func: Callable[[AgentResponse[Any | None]], None | Awaitable[None]],
) -> AgentMiddleware:
    """This hook is called once per agent invocation. After all model calls."""

    class _Middleware(AgentMiddleware):
        @override
        async def agent_middleware(
            self,
            request: AgentRequest,
            handler: AgentMiddlewareHandler,
        ) -> AgentResponse[Any | None]:
            handler_response = await handler(request)
            res = func(handler_response)
            if inspect.isawaitable(res):
                await res
            return handler_response

    return _Middleware()


class TokenLimitMiddleware(AgentMiddleware):
    """Stops agent execution when the token count of messages passed to the model exceeds the given limit."""

    _limit: int

    def __init__(self, limit: int) -> None:
        self._limit = limit

    @override
    async def model_middleware(
        self,
        request: ModelRequest,
        handler: ModelMiddlewareHandler,
    ) -> ModelResponse:
        if request.state.token_count >= self._limit:
            raise TokenLimitExceededException(token_limit=self._limit)
        return await handler(request)


class StepLimitMiddleware(AgentMiddleware):
    """Stops agent execution when the number of steps taken reaches the given limit."""

    _limit: int

    def __init__(self, limit: int) -> None:
        self._limit = limit

    @override
    async def model_middleware(
        self,
        request: ModelRequest,
        handler: ModelMiddlewareHandler,
    ) -> ModelResponse:
        if request.state.total_steps >= self._limit:
            raise StepsLimitExceededException(steps_limit=self._limit)
        return await handler(request)


class TimeoutLimitMiddleware(AgentMiddleware):
    """Stops agent execution when wall-clock time within an invoke exceeds the given seconds.

    The deadline resets on every invoke call - it measures time from the start of
    each invocation, not from agent construction.

    Do not share instances between agents.
    """

    _seconds: float
    _deadline: float | None

    def __init__(self, seconds: float) -> None:
        self._seconds = seconds
        self._deadline = None

    @override
    async def agent_middleware(
        self,
        request: AgentRequest,
        handler: AgentMiddlewareHandler,
    ) -> AgentResponse[Any | None]:
        # WARN: this might not work with agents handling
        # different threads at the same time.
        self._deadline = monotonic() + self._seconds
        return await handler(request)

    @override
    async def model_middleware(
        self,
        request: ModelRequest,
        handler: ModelMiddlewareHandler,
    ) -> ModelResponse:
        if self._deadline is not None and monotonic() >= self._deadline:
            raise TimeoutExceededException(timeout_seconds=self._seconds)
        return await handler(request)

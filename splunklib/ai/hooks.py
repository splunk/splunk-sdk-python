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
from splunklib.ai.structured_output import StructuredOutputGenerationException

DEFAULT_TIMEOUT_SECONDS: float = 600.0
DEFAULT_STEP_LIMIT: int = 100
DEFAULT_TOKEN_LIMIT: int = 200_000
DEFAULT_STRUCTURED_OUTPUT_RETRY_LIMIT: int = 3


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


class StructuredOutputRetryLimitExceededException(AgentStopException):
    """Raised by `Agent.invoke`, when structured output retry limit exceeds"""

    def __init__(self, retry_count: int) -> None:
        super().__init__(f"Structured output retry limit of {retry_count} exceeded")


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
    _deadline_per_thread_id: dict[str, float]

    def __init__(self, seconds: float) -> None:
        self._seconds = seconds
        self._deadline_per_thread_id = {}

    @override
    async def agent_middleware(
        self,
        request: AgentRequest,
        handler: AgentMiddlewareHandler,
    ) -> AgentResponse[Any | None]:
        try:
            # Agent loop starting.
            self._deadline_per_thread_id[request.thread_id] = (
                monotonic() + self._seconds
            )
            return await handler(request)
        finally:
            del self._deadline_per_thread_id[request.thread_id]  # don't leak memory

    @override
    async def model_middleware(
        self,
        request: ModelRequest,
        handler: ModelMiddlewareHandler,
    ) -> ModelResponse:
        if monotonic() >= self._deadline_per_thread_id[request.state.thread_id]:
            raise TimeoutExceededException(timeout_seconds=self._seconds)
        return await handler(request)


class StructuredOutputRetryLimitMiddleware(AgentMiddleware):
    """Stops agent execution when the agent exceeds structured output
    retry limit during a single agent loop invocation. Pass 0 to disable retries.
    """

    _limit: int
    _retries_per_thread_id: dict[str, int]

    def __init__(self, limit: int) -> None:
        self._limit = limit
        self._retries_per_thread_id = {}

    @override
    async def agent_middleware(
        self,
        request: AgentRequest,
        handler: AgentMiddlewareHandler,
    ) -> AgentResponse[Any | None]:
        try:
            # Agent loop starting.
            self._retries_per_thread_id[request.thread_id] = 0
            return await handler(request)
        finally:
            del self._retries_per_thread_id[request.thread_id]  # don't leak memory

    @override
    async def model_middleware(
        self,
        request: ModelRequest,
        handler: ModelMiddlewareHandler,
    ) -> ModelResponse:
        try:
            return await handler(request)
        except StructuredOutputGenerationException:
            self._retries_per_thread_id[request.state.thread_id] += 1
            if self._retries_per_thread_id[request.state.thread_id] > self._limit:
                raise StructuredOutputRetryLimitExceededException(self._limit)
            raise  # re-raise, to retry structured output generation

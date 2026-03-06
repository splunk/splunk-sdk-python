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


def token_limit(limit: float) -> AgentMiddleware:
    """This hook can be used to stop the agent execution if the token usage exceeds a certain limit."""

    @before_model
    def _token_limit_hook(req: ModelRequest) -> None:
        if req.state.token_count > limit:
            raise TokenLimitExceededException(token_limit=limit)

    return _token_limit_hook


def step_limit(limit: int) -> AgentMiddleware:
    """This hook can be used to stop the agent execution if the number of steps exceeds a certain limit."""

    @before_model
    def _step_limit_hook(req: ModelRequest) -> None:
        if req.state.total_steps >= limit:
            raise StepsLimitExceededException(steps_limit=limit)

    return _step_limit_hook


def timeout_limit(seconds: float) -> AgentMiddleware:
    """This hook can be used to stop the agent execution if the time limit exceeds a certain limit."""

    now = monotonic()
    timeout = now + seconds

    @before_model
    def _timeout_limit_hook(_: ModelRequest) -> None:
        if monotonic() >= timeout:
            raise TimeoutExceededException(timeout_seconds=seconds)

    return _timeout_limit_hook

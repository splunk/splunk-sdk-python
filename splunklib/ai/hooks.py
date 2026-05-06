import inspect
from collections.abc import Awaitable, Callable
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

from dataclasses import dataclass
from time import monotonic
from typing import Any, Callable, Literal, Protocol, final, override

from splunklib.ai.messages import AgentResponse

# Hook type decides when the hook is called during agent execution.
# before_model: before each model call
# after_model: after each model call
# before_agent: once per agent invocation, before any model calls
# after_agent: once per agent invocation, after all model calls
HookType = Literal["before_model", "after_model", "before_agent", "after_agent"]


@dataclass(frozen=True)
class AgentState:
    """AgentState is passed to each hook and contains information about the current state of the agent execution."""

    # holds messages exchanged so far in the conversation
    response: AgentResponse[Any | None]
    # steps taken so far in the conversation
    total_steps: int
    # tokens used so far in the conversation
    token_count: float


class AgentHook(Protocol):
    """AgentHook is a callable that can be registered to be called at specific points during the agent execution.

    Use decorators `before_model`, `after_model`, `before_agent`, `after_agent` to create hooks from simple functions.
    """

    type: HookType
    # Name of the middleware must be unique
    name: str

    def __call__(self, state: AgentState) -> None:
        """Called at specific points during the agent execution, depending on the hook type."""


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


def _create_hook(
    type: HookType,
    func: Callable[[AgentState], None],
    name: str | None = None,
) -> AgentHook:
    mw_name = name or func.__name__
    mw_type = type

    @final
    class CustomHook(AgentHook):
        type = mw_type
        name = mw_name

        @override
        def __call__(self, state: AgentState) -> None:
            return func(state)

    return CustomHook()


def before_model(func: Callable[[AgentState], None]) -> AgentHook:
    """This hook is called before each model call."""

    return _create_hook("before_model", func)


def after_model(func: Callable[[AgentState], None]) -> AgentHook:
    """This hook is called after each model call."""

    return _create_hook("after_model", func)


def before_agent(func: Callable[[AgentState], None]) -> AgentHook:
    """This hook is called once per agent invocation. Before any model calls."""

    return _create_hook("before_agent", func)


def after_agent(func: Callable[[AgentState], None]) -> AgentHook:
    """This hook is called once per agent invocation. After all model calls."""

    return _create_hook("after_agent", func)


def token_limit(limit: float) -> AgentHook:
    """This hook can be used to stop the agent execution if the token usage exceeds a certain limit."""

    def _token_limit_hook(state: AgentState) -> None:
        if state.token_count > limit:
            raise TokenLimitExceededException(token_limit=limit)

    return _create_hook("before_model", _token_limit_hook, name="builtin_token_limit")


def step_limit(limit: int) -> AgentHook:
    """This hook can be used to stop the agent execution if the number of steps exceeds a certain limit."""

    def _step_limit_hook(state: AgentState) -> None:
        if state.total_steps >= limit:
            raise StepsLimitExceededException(steps_limit=limit)

    return _create_hook("before_model", _step_limit_hook, name="builtin_step_limit")


def timeout_limit(seconds: float) -> AgentHook:
    """This hook can be used to stop the agent execution if the time limit exceeds a certain limit."""

    now = monotonic()
    timeout = now + seconds

    def _timeout_limit_hook(_state: AgentState) -> None:
        if monotonic() >= timeout:
            raise TimeoutExceededException(timeout_seconds=seconds)

    return _create_hook(
        "before_model", _timeout_limit_hook, name="builtin_timeout_limit"
    )

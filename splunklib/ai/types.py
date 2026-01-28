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

from abc import ABC, abstractmethod
from collections.abc import Awaitable, Sequence
from dataclasses import dataclass, field
from typing import Any, Callable, Generic, Literal, TypeVar

from pydantic import BaseModel

from splunklib.ai.model import PredefinedModel

Role = Literal["system", "user", "assistant", "tool"]

OutputT = TypeVar("OutputT", default=None, covariant=True, bound=BaseModel | None)


@dataclass(frozen=True)
class Message:
    role: Role
    content: str


@dataclass(frozen=True)
class AgentResponse(Generic[OutputT]):
    # in case output_schema is provided, this will hold the parsed structured output
    structured_output: OutputT
    # Holds the full message history including tool calls and final response
    messages: list[Message] = field(default_factory=list)


@dataclass(frozen=True)
class StopConditions:
    """Controls the stopping conditions for an agent's loop execution.

    Those conditions are applied to the whole Agent's lifetime.
    Meaning that they span across all invoke method calls.
    """

    # Maximum number of tokens the agent can use before stopping.
    token_limit: int | None = None
    # Maximum number of steps the agent can take before stopping.
    steps_limit: int | None = None
    # Time limit in seconds for the entire agent execution.
    timeout_seconds: float | None = None


class AgentStopException(Exception):
    """Custom exception to indicate conversation stopping conditions."""


class TokenLimitExceededException(AgentStopException):
    def __init__(self, token_limit: int) -> None:
        super().__init__(f"Token limit of {token_limit} exceeded.")


class StepsLimitExceededException(AgentStopException):
    def __init__(self, steps_limit: int) -> None:
        super().__init__(f"Steps limit of {steps_limit} exceeded.")


class TimeoutExceededException(AgentStopException):
    def __init__(self, timeout_seconds: float) -> None:
        super().__init__(f"Timed out after {timeout_seconds} seconds.")


class ToolException(Exception):
    """Custom exception to indicate tool execution errors."""


@dataclass(frozen=True)
class ToolResult:
    content: list[str]
    structured_content: dict[str, Any] | None


@dataclass(frozen=True)
class Tool:
    name: str
    description: str
    input_schema: dict[str, Any]
    func: Callable[..., Awaitable[ToolResult]]
    tags: list[str] | None = None

class BaseAgent(Generic[OutputT], ABC):
    _system_prompt: str
    _model: PredefinedModel
    _tools: Sequence[Tool]
    _agents: Sequence["BaseAgent[BaseModel | None]"]
    _name: str = ""
    _description: str = ""
    _input_schema: type[BaseModel] | None = None
    _output_schema: type[OutputT] | None = None
    _loop_stop_conditions: StopConditions | None = None

    def __init__(
        self,
        system_prompt: str,
        model: PredefinedModel,
        description: str = "",
        name: str = "",
        tools: Sequence[Tool] | None = None,
        agents: Sequence["BaseAgent[BaseModel | None]"] | None = None,
        input_schema: type[BaseModel] | None = None,
        output_schema: type[OutputT] | None = None,
        loop_stop_conditions: StopConditions | None = None,
    ) -> None:
        self._system_prompt = system_prompt
        self._model = model
        self._name = name
        self._description = description
        self._tools = tuple(tools) if tools else ()
        self._agents = tuple(agents) if agents else ()
        self._input_schema = input_schema
        self._output_schema = output_schema
        self._loop_stop_conditions = loop_stop_conditions

    @abstractmethod
    async def invoke(self, messages: list[Message]) -> AgentResponse[OutputT]: ...

    @property
    def system_prompt(self) -> str:
        return self._system_prompt

    @property
    def model(self) -> PredefinedModel:
        return self._model

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    def tools(self) -> Sequence[Tool]:
        return self._tools

    @property
    def agents(self) -> Sequence["BaseAgent[BaseModel | None]"]:
        return self._agents

    @property
    def input_schema(self) -> type[BaseModel] | None:
        return self._input_schema

    @property
    def output_schema(self) -> type[OutputT] | None:
        return self._output_schema

    @property
    def loop_stop_conditions(self) -> StopConditions | None:
        return self._loop_stop_conditions

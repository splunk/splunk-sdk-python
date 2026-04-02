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

from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any, Generic, Literal, TypeVar

from pydantic import BaseModel

from splunklib.ai.tools import ToolType


@dataclass(frozen=True)
class ToolCall:
    name: str
    args: dict[str, Any]
    id: str | None  # TODO: can be None?
    type: ToolType


@dataclass(frozen=True)
class SubagentCall:
    name: str
    args: str | dict[str, Any]
    id: str | None  # TODO: can be None?
    thread_id: str | None


@dataclass(frozen=True)
class BaseMessage:
    role: str = field(init=False)

    def __post_init__(self) -> None:
        if type(self) is BaseMessage:
            raise TypeError(
                "BaseMessage is an abstract class and cannot be instantiated"
            )


@dataclass(frozen=True)
class HumanMessage(BaseMessage):
    """
    Message originating from a human user.

    Represents user-provided input to the system, typically used
    to prompt, guide, or respond to the assistant during a
    conversation.
    """

    role: Literal["user"] = field(default="user", init=False)
    content: str


@dataclass(frozen=True)
class AIMessage(BaseMessage):
    """
    Message produced by an LLM.

    In addition to plain text content, an AIMessage may include
    agent or tool invocations, representing actions the model is
    requesting the Agent to execute.
    """

    role: Literal["assistant"] = field(default="assistant", init=False)
    content: str

    calls: Sequence[ToolCall | SubagentCall]


@dataclass(frozen=True)
class ToolResult:
    """
    ToolResult represents a result of a successful tool call.
    """

    content: str
    structured_content: dict[str, Any] | None


@dataclass(frozen=True)
class SubagentStructuredResult:
    """
    SubagentStructuredResult represents a result of a successful subagent call.
    Returned by subagent calls that have an output schema.
    """

    structured_output: dict[str, Any]


@dataclass(frozen=True)
class SubagentTextResult:
    """
    SubagentTextResult represents a result of a successful subagent call.
    Returned by subagent calls that don't have an output schema.
    """

    content: str


@dataclass(frozen=True)
class ToolFailureResult:
    """
    Represents the result of a failed sub-agent call.

    This type of failure is non-fatal, i.e. it does not stop the agent loop.
    Instead, the error information is returned to the LLM.
    """

    error_message: str


@dataclass(frozen=True)
class SubagentFailureResult:
    """
    Represents the result of a failed tool call.

    This type of failure is non-fatal, i.e. it does not stop the agent loop.
    Instead, the error information is returned to the LLM.
    """

    error_message: str


@dataclass(frozen=True)
class ToolMessage(BaseMessage):
    """ToolMessage represents a response of a tool call"""

    role: Literal["tool"] = field(default="tool", init=False)

    name: str
    type: ToolType
    call_id: str
    result: ToolResult | ToolFailureResult


@dataclass(frozen=True)
class SystemMessage(BaseMessage):
    """
    A message used to prime or control agent behavior.
    """

    role: Literal["system"] = field(default="system", init=False)
    content: str


@dataclass(frozen=True)
class SubagentMessage(BaseMessage):
    """
    SubagentMessage represents a response of an agent invocation
    """

    role: Literal["subagent"] = field(default="subagent", init=False)

    name: str
    call_id: str
    result: SubagentStructuredResult | SubagentTextResult | SubagentFailureResult


OutputT = TypeVar("OutputT", default=None, covariant=True, bound=BaseModel | None)

# TODO: We should make sure that the list[BaseMessage] is JSON serializable
# and deserializable. This might become important with custom checkpointers
# where developers might want to store messages in say KV store.


@dataclass(frozen=True)
class AgentResponse(Generic[OutputT]):
    # in case output_schema is provided, this will hold the parsed structured output
    structured_output: OutputT
    # Holds the full message history including tool calls and final response
    # The last message is and must always be an AIMessage with len(calls) == 0.
    messages: list[BaseMessage]

    @property
    def final_message(self) -> AIMessage:
        """final_message returns the last AIMessage at self.messages[-1]."""

        # Make sure that it is valid, otherwise report that.
        # These exceptions should never be reached in a valid code and always
        # are a programmers fault.
        if type(self.messages[-1]) is not AIMessage:
            raise AssertionError(
                "Invalid AgentResponse, self.messages[-1] is not of type: AIMessage"
            )
        if len(self.messages[-1].calls) != 0:
            raise AssertionError("Invalid AgentResponse, self.messages[-1].calls != 0")

        return self.messages[-1]

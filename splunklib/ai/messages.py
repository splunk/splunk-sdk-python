#
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

OutputT = TypeVar("OutputT", default=None, covariant=True, bound=BaseModel | None)


@dataclass(frozen=True)
class ToolCall:
    name: str
    args: dict[str, Any]
    id: str | None


@dataclass(frozen=True)
class AgentCall:
    name: str
    args: dict[str, Any]
    id: str | None


@dataclass(frozen=True)
class BaseMessage:
    role: str = ""
    content: str = field(default="")

    def __post_init__(self):
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

    role: Literal["user"] = "user"


@dataclass(frozen=True)
class AIMessage(BaseMessage):
    """
    Message produced by an LLM.

    In addition to plain text content, an AIMessage may include
    agent or tool invocations, representing actions the model is
    requesting the Agent to execute.
    """

    role: Literal["assistant"] = "assistant"
    calls: Sequence[ToolCall | AgentCall] = field(
        default_factory=list[ToolCall | AgentCall]
    )


@dataclass(frozen=True)
class ToolMessage(BaseMessage):
    """
    ToolMessage represents a response of a tool call
    """

    role: Literal["tool"] = "tool"
    name: str = field(default="")
    call_id: str = field(default="")
    status: Literal["success", "error"] = "success"


@dataclass(frozen=True)
class SystemMessage(BaseMessage):
    """
    A message used to prime or control agent behavior.
    """

    role: Literal["system"] = "system"


@dataclass(frozen=True)
class SubagentMessage(BaseMessage):
    """
    SubagentMessage represents a response of an agent invocation
    """

    role: Literal["subagent"] = "subagent"
    name: str = field(default="")
    call_id: str = field(default="")
    status: Literal["success", "error"] = "success"


@dataclass(frozen=True)
class AgentResponse(Generic[OutputT]):
    # in case output_schema is provided, this will hold the parsed structured output
    structured_output: OutputT
    # Holds the full message history including tool calls and final response
    messages: list[BaseMessage] = field(default_factory=list)

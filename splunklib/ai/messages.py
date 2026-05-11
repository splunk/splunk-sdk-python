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


@dataclass(frozen=True, kw_only=True)
class TextBlock:
    """Plain text content block returned by a model."""

    text: str
    id: str | None = field(default=None)
    extras: dict[str, Any] | None = field(default=None)
    """ This field contains LLM-specific metadata.

    It should be returned to the LLM unchanged in subsequent LLM calls.
    The contents of this field is not guaranteed to be stable
    and might change as SDK evolves.
    """


@dataclass(frozen=True, kw_only=True)
class OpaqueBlock:
    """Content block of an unrecognized or unsupported type.

    The raw provider dict is preserved in `_data` so it can be sent back
    to the model unchanged on subsequent calls.
    """

    _data: dict[str, Any]
    """This is raw data coming from the backend library.

    This field is used to preserve the content blocks returned
    from LLM, but not supported by the SDK.

    DO NOT change the contents of this field.

    If adding logic based around contents of this
    field, keep in mind things could BREAK in the future,
    once first class support is added to new content blocks.
    """


# Type alias for all content block variants.
ContentBlock = TextBlock | OpaqueBlock


@dataclass(frozen=True, kw_only=True)
class ToolCall:
    id: str
    name: str
    type: ToolType
    args: dict[str, Any]


@dataclass(frozen=True, kw_only=True)
class SubagentCall:
    id: str
    name: str
    args: str | dict[str, Any]
    thread_id: str | None


@dataclass(frozen=True, kw_only=True)
class StructuredOutputCall:
    id: str
    name: str
    args: dict[str, Any]


@dataclass(frozen=True, kw_only=True)
class BaseMessage:
    role: str = field(init=False)

    def __post_init__(self) -> None:
        if type(self) is BaseMessage:
            raise TypeError("BaseMessage is an abstract class and cannot be instantiated")


@dataclass(frozen=True, kw_only=True)
class HumanMessage(BaseMessage):
    """
    Message originating from a human user.

    Represents user-provided input to the system, typically used
    to prompt, guide, or respond to the assistant during a
    conversation.
    """

    role: Literal["user"] = field(default="user", init=False)
    content: str


@dataclass(frozen=True, kw_only=True)
class AIMessage(BaseMessage):
    """
    Message produced by an LLM.

    In addition to plain text content, an AIMessage may include
    agent or tool invocations, representing actions the model is
    requesting the Agent to execute.

    AIMessage might contain structured_output_calls, when the LLM model
    does not support natively structured outputs, in such cases the
    LLM returns the structured output as part of a tool call,
    stored in that field.
    """

    role: Literal["assistant"] = field(default="assistant", init=False)
    content: str | list[str | ContentBlock]

    calls: Sequence[ToolCall | SubagentCall]
    structured_output_calls: Sequence[StructuredOutputCall] = field(default_factory=tuple)
    extras: dict[str, Any] | None = field(default=None)
    """ This field contains LLM-specific metadata.

    It should be returned to the LLM unchanged in subsequent LLM calls.
    The contents of this field is not guaranteed to be stable
    and might change as SDK evolves.
    """


@dataclass(frozen=True, kw_only=True)
class ToolResult:
    """
    ToolResult represents a result of a successful tool call.
    """

    content: str
    structured_content: dict[str, Any] | None


@dataclass(frozen=True, kw_only=True)
class SubagentStructuredResult:
    """
    SubagentStructuredResult represents a result of a successful subagent call.
    Returned by subagent calls that have an output schema.
    """

    structured_output: dict[str, Any]


@dataclass(frozen=True, kw_only=True)
class SubagentTextResult:
    """
    SubagentTextResult represents a result of a successful subagent call.
    Returned by subagent calls that don't have an output schema.
    """

    content: str


@dataclass(frozen=True, kw_only=True)
class ToolFailureResult:
    """
    Represents the result of a failed sub-agent call.

    This type of failure is non-fatal, i.e. it does not stop the agent loop.
    Instead, the error information is returned to the LLM.
    """

    error_message: str


@dataclass(frozen=True, kw_only=True)
class SubagentFailureResult:
    """
    Represents the result of a failed tool call.

    This type of failure is non-fatal, i.e. it does not stop the agent loop.
    Instead, the error information is returned to the LLM.
    """

    error_message: str


@dataclass(frozen=True, kw_only=True)
class ToolMessage(BaseMessage):
    """ToolMessage represents a response of a tool call"""

    role: Literal["tool"] = field(default="tool", init=False)

    name: str
    type: ToolType
    call_id: str
    result: ToolResult | ToolFailureResult


@dataclass(frozen=True, kw_only=True)
class SystemMessage(BaseMessage):
    """
    A message used to prime or control agent behavior.
    """

    role: Literal["system"] = field(default="system", init=False)
    content: str


@dataclass(frozen=True, kw_only=True)
class SubagentMessage(BaseMessage):
    """
    SubagentMessage represents a response of an agent invocation
    """

    role: Literal["subagent"] = field(default="subagent", init=False)

    name: str
    call_id: str
    result: SubagentStructuredResult | SubagentTextResult | SubagentFailureResult


@dataclass(frozen=True, kw_only=True)
class StructuredOutputMessage(BaseMessage):
    """
    StructuredMessage represents a response to the StructuredOutputCall.
    """

    role: Literal["tool-strategy-response"] = field(default="tool-strategy-response", init=False)

    call_id: str
    name: str
    status: Literal["success", "error"]
    content: str


OutputT = TypeVar("OutputT", default=None, covariant=True, bound=BaseModel | None)

# TODO: We should make sure that the list[BaseMessage] is JSON serializable
# and deserializable. This might become important with custom checkpointers
# where developers might want to store messages in say KV store.


@dataclass(frozen=True, kw_only=True)
class AgentResponse(Generic[OutputT]):
    # in case output_schema is provided, this will hold the parsed structured output
    structured_output: OutputT
    # Holds the full message history including tool calls and final response.
    #
    # Normally messages[-1] is the final AIMessage, but when the tool strategy
    # is used for structured output generation, messages[-1] may be a
    # StructuredOutputMessage instead. Use final_message to get
    # the final AIMessage reliably.
    messages: list[BaseMessage]

    @property
    def final_message(self) -> AIMessage:
        """
        final_message returns the AIMessage that ended the agentic loop.
        """

        for msg in reversed(self.messages):
            if isinstance(msg, AIMessage):
                if len(msg.calls) != 0:
                    raise AssertionError(
                        "AgentResponse.messages is invalid; unexpected AIMessage with len(call) != 0"
                    )
                return msg
            elif isinstance(msg, StructuredOutputMessage):
                continue
            else:
                raise AssertionError(
                    f"AgentResponse.messages is invalid; unexpected message type {type(msg)}"
                )

        raise AssertionError("AgentResponse.messages is invalid; there are no messages in the list")

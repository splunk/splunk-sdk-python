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

from dataclasses import dataclass

DEFAULT_TIMEOUT_SECONDS: float = 600.0
DEFAULT_STEP_LIMIT: int = 100
DEFAULT_TOKEN_LIMIT: int = 200_000
DEFAULT_STRUCTURED_OUTPUT_RETRY_LIMIT: int = 3


@dataclass(frozen=True, kw_only=True)
class AgentLimits:
    """Built-in safety limits applied to every Agent invocation."""

    timeout: float | None = DEFAULT_TIMEOUT_SECONDS
    """Maximum wall-clock time in seconds allowed for a single invoke call.
    The deadline resets on every invoke. Raises `TimeoutExceededException` when exceeded.
    """

    max_steps: int | None = DEFAULT_STEP_LIMIT
    """Maximum number of messages allowed in the conversation before the
    agent loop is stopped. Checked before each model call.
    Raises `StepsLimitExceededException` when exceeded.
    """

    max_tokens: int | None = DEFAULT_TOKEN_LIMIT
    """Maximum number of tokens (approximate) allowed in the messages
    passed to the model. Checked before each model call.
    Raises `TokenLimitExceededException` when exceeded.
    """

    max_structured_output_retires: int | None = DEFAULT_STRUCTURED_OUTPUT_RETRY_LIMIT
    """Maximum number of structured output generation retries allowed
    within a single `invoke` call.
    Raises `StructuredOutputRetryLimitExceededException` when exceeded.
    """


class AgentStopException(Exception):
    """Custom exception to indicate conversation stopping conditions."""


class TokenLimitExceededException(AgentStopException):
    """Raised by `Agent.invoke`, when token limit exceeds"""

    def __init__(self, token_limit: int) -> None:
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

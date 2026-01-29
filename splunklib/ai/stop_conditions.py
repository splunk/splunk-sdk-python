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


from dataclasses import dataclass


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

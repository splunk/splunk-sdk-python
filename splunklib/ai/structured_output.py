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

from splunklib.ai.messages import AIMessage


@dataclass(frozen=True, kw_only=True)
class StructuredOutputMultipleToolCallsError:
    pass


@dataclass(frozen=True, kw_only=True)
class StructuredOutputValidationError:
    validation_error: str


class StructuredOutputGenerationException(Exception):
    _message: AIMessage
    _error: StructuredOutputValidationError | StructuredOutputMultipleToolCallsError

    def __init__(
        self,
        message: AIMessage,
        error: StructuredOutputValidationError | StructuredOutputMultipleToolCallsError,
    ) -> None:
        self._message = message
        self._error = error

        if len(self.message.structured_output_calls) > 1 and not isinstance(
            self._error, StructuredOutputMultipleToolCallsError
        ):
            raise AssertionError(
                "AIMessage contains more than one structured_output_calls, but error is not StructuredOutputMultipleToolCallsError"
            )
        if len(self.message.structured_output_calls) <= 1 and not isinstance(
            self._error, StructuredOutputValidationError
        ):
            raise AssertionError("error is not StructuredOutputValidationError, but should be")

        match self.error:
            case StructuredOutputValidationError():
                super().__init__(
                    f"Failed to generate structured output: {self.error.validation_error}"
                )
            case StructuredOutputMultipleToolCallsError():
                super().__init__(
                    "Failed to generate structured output: LLM returned multiple structured outputs"
                )

    @property
    def message(self) -> AIMessage:
        return self._message

    @property
    def error(
        self,
    ) -> StructuredOutputValidationError | StructuredOutputMultipleToolCallsError:
        return self._error

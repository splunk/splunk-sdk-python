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

import os
from typing import Any, override
from unittest.mock import patch

import pytest
from pydantic import BaseModel, Field, model_validator
from pydantic.dataclasses import dataclass

from splunklib.ai import Agent
from splunklib.ai.hooks import (
    StructuredOutputRetryLimitExceededException,
    StructuredOutputRetryLimitMiddleware,
)
from splunklib.ai.messages import (
    AgentResponse,
    AIMessage,
    HumanMessage,
    StructuredOutputCall,
    StructuredOutputMessage,
    SubagentCall,
    SubagentFailureResult,
    SubagentMessage,
    ToolCall,
)
from splunklib.ai.middleware import (
    AgentMiddleware,
    AgentMiddlewareHandler,
    AgentRequest,
    ModelMiddlewareHandler,
    ModelRequest,
    ModelResponse,
    SubagentMiddlewareHandler,
    SubagentRequest,
    SubagentResponse,
    ToolMiddlewareHandler,
    ToolRequest,
    ToolResponse,
    model_middleware,
    subagent_middleware,
    tool_middleware,
)
from splunklib.ai.structured_output import (
    StructuredOutputGenerationException,
    StructuredOutputMultipleToolCallsError,
    StructuredOutputValidationError,
)
from splunklib.ai.tool_settings import ToolSettings
from splunklib.ai.tools import ToolType
from tests.ai_testlib import AITestCase, ai_snapshot_test


class AssertNoCallMiddleware(AgentMiddleware):
    @override
    async def tool_middleware(
        self,
        request: ToolRequest,
        handler: ToolMiddlewareHandler,
    ) -> ToolResponse:
        raise AssertionError("tool called")

    @override
    async def subagent_middleware(
        self,
        request: SubagentRequest,
        handler: SubagentMiddlewareHandler,
    ) -> SubagentResponse:
        raise AssertionError("subagent called")


@dataclass
class AssertSingleAgentMiddlewareCall(AgentMiddleware):
    called: bool = False

    @override
    async def agent_middleware(
        self,
        request: AgentRequest,
        handler: AgentMiddlewareHandler,
    ) -> AgentResponse[Any | None]:
        assert not self.called, "agent middleware called twice"
        self.called = True
        return await handler(request)


class TestStructuredOutput(AITestCase):
    @patch("splunklib.ai.engines.langchain._testing_force_tool_strategy", True)
    @pytest.mark.asyncio
    @ai_snapshot_test()
    async def test_tool_strategy(self) -> None:
        pytest.importorskip("langchain_openai")

        class Person(BaseModel):
            name: str = Field(description="The person's full name", min_length=1)
            age: int = Field(description="The person's age in years", ge=0, le=150)

        @model_middleware
        async def _model_middleware(
            request: ModelRequest,
            handler: ModelMiddlewareHandler,
        ) -> ModelResponse:
            try:
                resp = await handler(request)
            except StructuredOutputGenerationException:
                raise AssertionError(
                    "handler failed with StructuredOutputGenerationException"
                )

            assert resp.structured_output is not None

            assert len(resp.message.structured_output_calls) == 1
            assert (
                Person(**resp.message.structured_output_calls[0].args)
                == resp.structured_output
            )
            assert resp.message.structured_output_calls[0].name == "Person"

            return resp

        async with Agent(
            model=(await self.model()),
            system_prompt="Respond with structured data",
            output_schema=Person,
            service=self.service,
            middleware=[
                _model_middleware,
                AssertNoCallMiddleware(),
                AssertSingleAgentMiddlewareCall(),
            ],
        ) as agent:
            result = await agent.invoke(
                [
                    HumanMessage(
                        content="fill in the details for Person model",
                    )
                ]
            )

            response = result.structured_output

            assert type(response) == Person, "Response is not of type Person"
            assert response.name != "", "Name field is empty"
            assert 0 <= response.age <= 150, "Age field is out of bounds"

            calls = result.final_message.structured_output_calls
            assert len(calls) == 1
            assert calls[0].name == "Person"
            assert Person(**calls[0].args) == result.structured_output

    @patch("splunklib.ai.engines.langchain._testing_force_tool_strategy", True)
    @pytest.mark.asyncio
    @ai_snapshot_test()
    async def test_tool_strategy_retry(self) -> None:
        pytest.importorskip("langchain_openai")

        class Person(BaseModel):
            name: str = Field(description="The person's full name", min_length=1)

            @model_validator(mode="after")
            def is_uppercase(self) -> "Person":
                if self.name.upper() != self.name:
                    raise ValueError("Invalid name: ALL letters must be capitalized")
                return self

        after_first_model_call = False

        @model_middleware
        async def _model_middleware(
            request: ModelRequest,
            handler: ModelMiddlewareHandler,
        ) -> ModelResponse:
            nonlocal after_first_model_call

            try:
                resp = await handler(request)
            except StructuredOutputGenerationException as e:
                assert not after_first_model_call, (
                    "generation error after first model call"
                )
                after_first_model_call = True

                assert isinstance(e.error, StructuredOutputValidationError), (
                    "invalid e.error"
                )
                assert "ALL letters must be capitalized" in e.error.validation_error, (
                    "invalid validation_error"
                )
                assert len(e.message.structured_output_calls) == 1, (
                    "missing structured_output_calls"
                )

                try:
                    Person(**e.message.structured_output_calls[0].args)
                    raise AssertionError(
                        "args are valid, but got an StructuredOutputGenerationException"
                    )
                except Exception as e:
                    pass

                raise  # re-raise the StructuredOutputGenerationException

            assert after_first_model_call, "generation error did not happen"
            assert resp.structured_output is not None, "missing structured_output"
            assert len(resp.message.structured_output_calls) == 1, (
                "unexpected amount of structured_output_calls"
            )
            assert resp.message.structured_output_calls[0].name == "Person", (
                "invalid structured output tool name"
            )
            assert (
                Person(**resp.message.structured_output_calls[0].args)
                == resp.structured_output
            ), "invalid structured_output"

            return resp

        async with Agent(
            model=(await self.model()),
            system_prompt="Respond with structured data",
            output_schema=Person,
            service=self.service,
            middleware=[
                _model_middleware,
                AssertNoCallMiddleware(),
                AssertSingleAgentMiddlewareCall(),
            ],
        ) as agent:
            result = await agent.invoke(
                [
                    HumanMessage(
                        content="Hi, return a response with name set to Mike",
                    )
                ]
            )

            response = result.structured_output
            assert type(response) is Person, "Response is not of type Person"
            assert response.name == "MIKE", "Invalid name"

            calls = result.final_message.structured_output_calls
            assert len(calls) == 1
            assert calls[0].name == "Person"
            assert Person(**calls[0].args) == result.structured_output

            assert isinstance(result.messages[-1], StructuredOutputMessage)
            assert result.messages[-1].name == "Person"

            assert isinstance(result.messages[-2], AIMessage)
            assert len(result.messages[-2].structured_output_calls) == 1
            structured_call = result.messages[-2].structured_output_calls[0]
            Person(**structured_call.args)  # serves as an assertion
            assert structured_call.id == result.messages[-1].call_id
            assert structured_call.name == "Person"

            assert isinstance(
                result.messages[-3], StructuredOutputMessage
            )  # contains validation error
            assert isinstance(result.messages[-4], AIMessage)

        assert after_first_model_call

    @pytest.mark.asyncio
    @ai_snapshot_test()
    async def test_provider_strategy_retry(self) -> None:
        pytest.importorskip("langchain_openai")

        # Note that here we assume that our CI runs model that supports provider strategy.

        class Person(BaseModel):
            name: str = Field(description="The person's full name", min_length=1)

            @model_validator(mode="after")
            def is_uppercase(self) -> "Person":
                if self.name.upper() != self.name:
                    raise ValueError("Invalid name: ALL letters must be capitalized")
                return self

        after_first_model_call = False

        @model_middleware
        async def _model_middleware(
            request: ModelRequest,
            handler: ModelMiddlewareHandler,
        ) -> ModelResponse:
            nonlocal after_first_model_call

            try:
                resp = await handler(request)
            except StructuredOutputGenerationException as e:
                assert not after_first_model_call, (
                    "generation error after first model call"
                )
                after_first_model_call = True

                assert isinstance(e.error, StructuredOutputValidationError), (
                    "invalid e.error"
                )
                assert "ALL letters must be capitalized" in e.error.validation_error, (
                    "invalid validation_error"
                )

                try:
                    Person.model_validate_json(self.parse_content(e.message))
                    raise AssertionError(
                        "args are valid, but got an StructuredOutputGenerationException"
                    )
                except Exception as e:
                    pass

                raise  # re-raise the StructuredOutputGenerationException

            assert after_first_model_call, "generation error did not happen"
            assert resp.structured_output is not None, "missing structured_output"
            assert (
                Person.model_validate_json(self.parse_content(resp.message))
                == resp.structured_output
            ), "invalid structured output"

            return resp

        async with Agent(
            model=(await self.model()),
            system_prompt="Respond with structured data",
            output_schema=Person,
            service=self.service,
            middleware=[
                _model_middleware,
                AssertNoCallMiddleware(),
                AssertSingleAgentMiddlewareCall(),
            ],
        ) as agent:
            result = await agent.invoke(
                [
                    HumanMessage(
                        content="Hi, return a response with name set to Mike",
                    )
                ]
            )

            response = result.structured_output
            assert type(response) is Person, "Response is not of type Person"
            assert response.name == "MIKE", "Invalid name"

            assert len(result.final_message.structured_output_calls) == 0
            assert (
                Person.model_validate_json(self.parse_content(result.final_message))
                == result.structured_output
            )

            assert isinstance(result.messages[-1], AIMessage)
            assert isinstance(
                result.messages[-2], HumanMessage
            )  # re-try message, contains validation error
            assert isinstance(result.messages[-3], AIMessage)

        assert after_first_model_call

    @pytest.mark.asyncio
    @patch(
        "splunklib.ai.agent._testing_local_tools_path",
        os.path.join(os.path.dirname(__file__), "testdata", "weather.py"),
    )
    @patch("splunklib.ai.agent._testing_app_id", "app_id")
    @ai_snapshot_test()
    async def test_provider_strategy_with_tool_calls(self) -> None:
        pytest.importorskip("langchain_openai")

        # Note that here we assume that our CI runs model that supports provider strategy.

        class Person(BaseModel):
            name: str = Field(description="The person's full name", min_length=1)

        after_first_model_call = False

        @model_middleware
        async def _model_middleware(
            _request: ModelRequest,
            _handler: ModelMiddlewareHandler,
        ) -> ModelResponse:
            nonlocal after_first_model_call

            if after_first_model_call:
                return ModelResponse(
                    message=AIMessage(content="", calls=[]),
                    structured_output=Person(name="Mike"),
                )

            after_first_model_call = True
            return ModelResponse(
                message=AIMessage(
                    content="",
                    calls=[
                        ToolCall(
                            id="call-1",
                            name="temperature",
                            args={"city": "Krakow"},
                            type=ToolType.LOCAL,
                        )
                    ],
                ),
                structured_output=Person(name="Mike"),
            )

        tool_called = False

        @tool_middleware
        async def _tool_middleware(
            request: ToolRequest,
            handler: ToolMiddlewareHandler,
        ) -> ToolResponse:
            nonlocal tool_called
            tool_called = True
            return await handler(request)

        async with Agent(
            model=(await self.model()),
            system_prompt="Respond with structured data",
            output_schema=Person,
            service=self.service,
            middleware=[
                _model_middleware,
                _tool_middleware,
                AssertSingleAgentMiddlewareCall(),
            ],
            tool_settings=ToolSettings(local=True, remote=None),
        ) as agent:
            result = await agent.invoke([HumanMessage(content="")])
            assert result.structured_output.name == "Mike"

        assert after_first_model_call
        assert tool_called

    @patch(
        "splunklib.ai.agent._testing_local_tools_path",
        os.path.join(os.path.dirname(__file__), "testdata", "weather.py"),
    )
    @patch("splunklib.ai.agent._testing_app_id", "app_id")
    @patch("splunklib.ai.engines.langchain._testing_force_tool_strategy", True)
    @pytest.mark.asyncio
    @ai_snapshot_test()
    async def test_tool_strategy_with_tool_calls(self) -> None:
        pytest.importorskip("langchain_openai")

        # Note that here we assume that our CI runs model that supports provider strategy.

        class Person(BaseModel):
            name: str = Field(description="The person's full name", min_length=1)

        after_first_model_call = False

        @model_middleware
        async def _model_middleware(
            _request: ModelRequest,
            _handler: ModelMiddlewareHandler,
        ) -> ModelResponse:
            nonlocal after_first_model_call

            if after_first_model_call:
                return ModelResponse(
                    message=AIMessage(content="", calls=[]),
                    structured_output=Person(name="Mike"),
                )

            after_first_model_call = True
            return ModelResponse(
                message=AIMessage(
                    content="",
                    structured_output_calls=[
                        StructuredOutputCall(
                            id="call-2", name="Person", args={"name": "Mike"}
                        ),
                    ],
                    calls=[
                        ToolCall(
                            id="call-1",
                            name="temperature",
                            args={"city": "Krakow"},
                            type=ToolType.LOCAL,
                        )
                    ],
                ),
                structured_output=Person(name="Mike"),
            )

        tool_called = False

        @tool_middleware
        async def _tool_middleware(
            request: ToolRequest,
            handler: ToolMiddlewareHandler,
        ) -> ToolResponse:
            nonlocal tool_called
            tool_called = True
            return await handler(request)

        async with Agent(
            model=(await self.model()),
            system_prompt="Respond with structured data",
            output_schema=Person,
            service=self.service,
            middleware=[
                _model_middleware,
                _tool_middleware,
                AssertSingleAgentMiddlewareCall(),
            ],
            tool_settings=ToolSettings(local=True, remote=None),
        ) as agent:
            result = await agent.invoke([HumanMessage(content="")])
            assert result.structured_output.name == "Mike"

        assert after_first_model_call
        assert tool_called

    @pytest.mark.asyncio
    @patch(
        "splunklib.ai.agent._testing_local_tools_path",
        os.path.join(os.path.dirname(__file__), "testdata", "weather.py"),
    )
    @patch("splunklib.ai.agent._testing_app_id", "app_id")
    @ai_snapshot_test()
    async def test_provider_strategy_with_tool_calls_failure(
        self,
    ) -> None:
        pytest.importorskip("langchain_openai")

        # Note that here we assume that our CI runs model that supports provider strategy.

        class Person(BaseModel):
            name: str = Field(description="The person's full name", min_length=1)

        after_first_model_call = False

        @model_middleware
        async def _model_middleware(
            _request: ModelRequest,
            _handler: ModelMiddlewareHandler,
        ) -> ModelResponse:
            nonlocal after_first_model_call

            if after_first_model_call:
                return ModelResponse(
                    message=AIMessage(content="", calls=[]),
                    structured_output=Person(name="Mike"),
                )

            after_first_model_call = True
            raise StructuredOutputGenerationException(
                message=AIMessage(
                    content="",
                    calls=[
                        ToolCall(
                            id="call-1",
                            name="temperature",
                            args={"city": "Krakow"},
                            type=ToolType.LOCAL,
                        )
                    ],
                ),
                error=StructuredOutputValidationError(
                    validation_error="Invalid output"
                ),
            )

        tool_called = False

        @tool_middleware
        async def _tool_middleware(
            request: ToolRequest,
            handler: ToolMiddlewareHandler,
        ) -> ToolResponse:
            nonlocal tool_called
            tool_called = True
            return await handler(request)

        async with Agent(
            model=(await self.model()),
            system_prompt="Respond with structured data",
            output_schema=Person,
            service=self.service,
            middleware=[
                _model_middleware,
                _tool_middleware,
                AssertSingleAgentMiddlewareCall(),
            ],
            tool_settings=ToolSettings(local=True, remote=None),
        ) as agent:
            result = await agent.invoke([HumanMessage(content="")])
            assert result.structured_output.name == "Mike"

        assert after_first_model_call
        assert tool_called

    @pytest.mark.asyncio
    @patch(
        "splunklib.ai.agent._testing_local_tools_path",
        os.path.join(os.path.dirname(__file__), "testdata", "weather.py"),
    )
    @patch("splunklib.ai.agent._testing_app_id", "app_id")
    @patch("splunklib.ai.engines.langchain._testing_force_tool_strategy", True)
    @ai_snapshot_test()
    async def test_tool_strategy_with_tool_calls_failure(
        self,
    ) -> None:
        pytest.importorskip("langchain_openai")

        class Person(BaseModel):
            name: str = Field(description="The person's full name", min_length=1)

        after_first_model_call = False

        @model_middleware
        async def _model_middleware(
            _request: ModelRequest,
            _handler: ModelMiddlewareHandler,
        ) -> ModelResponse:
            nonlocal after_first_model_call

            if after_first_model_call:
                return ModelResponse(
                    message=AIMessage(content="", calls=[]),
                    structured_output=Person(name="Mike"),
                )

            after_first_model_call = True
            raise StructuredOutputGenerationException(
                message=AIMessage(
                    content="",
                    calls=[
                        ToolCall(
                            id="call-1",
                            name="temperature",
                            args={"city": "Krakow"},
                            type=ToolType.LOCAL,
                        )
                    ],
                    structured_output_calls=[
                        StructuredOutputCall(
                            id="call-2", name="Person", args={"name": "Mike"}
                        ),
                    ],
                ),
                error=StructuredOutputValidationError(
                    validation_error="Invalid output"
                ),
            )

        tool_called = False

        @tool_middleware
        async def _tool_middleware(
            request: ToolRequest,
            handler: ToolMiddlewareHandler,
        ) -> ToolResponse:
            nonlocal tool_called
            tool_called = True
            return await handler(request)

        async with Agent(
            model=(await self.model()),
            system_prompt="Respond with structured data",
            output_schema=Person,
            service=self.service,
            middleware=[
                _model_middleware,
                _tool_middleware,
                AssertSingleAgentMiddlewareCall(),
            ],
            tool_settings=ToolSettings(local=True, remote=None),
        ) as agent:
            result = await agent.invoke([HumanMessage(content="")])
            assert result.structured_output.name == "Mike"

        assert after_first_model_call
        assert tool_called

    @pytest.mark.asyncio
    @ai_snapshot_test()
    async def test_provider_strategy_reject_output_in_middleware(self) -> None:
        pytest.importorskip("langchain_openai")

        # Note that here we assume that our CI runs model that supports provider strategy.

        class Person(BaseModel):
            name: str = Field(description="The person's full name", min_length=1)

        @model_middleware
        async def _model_middleware(
            request: ModelRequest,
            handler: ModelMiddlewareHandler,
        ) -> ModelResponse:
            resp = await handler(request)
            assert isinstance(resp.structured_output, Person)
            if resp.structured_output.name.upper() != resp.structured_output.name:
                raise StructuredOutputGenerationException(
                    message=resp.message,
                    error=StructuredOutputValidationError(
                        validation_error="Validation error: name must have ALL letters capitalized"
                    ),
                )
            return resp

        async with Agent(
            model=(await self.model()),
            system_prompt="Respond with structured data",
            output_schema=Person,
            service=self.service,
            middleware=[_model_middleware, AssertNoCallMiddleware()],
        ) as agent:
            result = await agent.invoke(
                [HumanMessage(content="My name is Mike, what is my name?")]
            )
            assert result.structured_output.name == "MIKE"

    @pytest.mark.asyncio
    @patch("splunklib.ai.engines.langchain._testing_force_tool_strategy", True)
    @ai_snapshot_test()
    async def test_tool_strategy_reject_output_in_middleware(self) -> None:
        pytest.importorskip("langchain_openai")

        class Person(BaseModel):
            name: str = Field(description="The person's full name", min_length=1)

        @model_middleware
        async def _model_middleware(
            request: ModelRequest,
            handler: ModelMiddlewareHandler,
        ) -> ModelResponse:
            resp = await handler(request)
            assert isinstance(resp.structured_output, Person)
            if resp.structured_output.name.upper() != resp.structured_output.name:
                raise StructuredOutputGenerationException(
                    message=resp.message,
                    error=StructuredOutputValidationError(
                        validation_error="Validation error: name must have ALL letters capitalized"
                    ),
                )
            return resp

        async with Agent(
            model=(await self.model()),
            system_prompt="Respond with structured data",
            output_schema=Person,
            service=self.service,
            middleware=[_model_middleware, AssertSingleAgentMiddlewareCall()],
        ) as agent:
            result = await agent.invoke(
                [HumanMessage(content="My name is Mike, what is my name?")]
            )
            assert result.structured_output.name == "MIKE"

    @pytest.mark.asyncio
    @patch("splunklib.ai.engines.langchain._testing_force_tool_strategy", True)
    @ai_snapshot_test()
    async def test_tool_strategy_multiple_tool_calls(self) -> None:
        pytest.importorskip("langchain_openai")

        class Person(BaseModel):
            name: str = Field(description="The person's full name", min_length=1)

        @model_middleware
        async def _model_middleware(
            request: ModelRequest,
            handler: ModelMiddlewareHandler,
        ) -> ModelResponse:
            try:
                return await handler(request)
            except StructuredOutputGenerationException as e:
                assert isinstance(e.error, StructuredOutputMultipleToolCallsError)
                assert len(e.message.structured_output_calls) == 2
                assert e.message.structured_output_calls[0].name == "Person"
                assert e.message.structured_output_calls[1].name == "Person"

                name1 = e.message.structured_output_calls[0].args["name"].lower()
                name2 = e.message.structured_output_calls[0].args["name"].lower()
                assert (name1 == "mike" and name2 == "john") or (
                    name1 == "john" or name2 == "mike"
                )

                raise

        async with Agent(
            model=(await self.model()),
            system_prompt=(
                "Respond with structured data. CALL __output-Person for each name you were provided."
            ),
            output_schema=Person,
            service=self.service,
            middleware=[
                _model_middleware,
                AssertNoCallMiddleware(),
                AssertSingleAgentMiddlewareCall(),
            ],
        ) as agent:
            result = await agent.invoke(
                [HumanMessage(content="My name is Mike and John, return our names?")]
            )

            # During retry phase, the LLM understood that it should only call it once,
            # thus we get a valid output here.
            assert (
                result.structured_output.name.lower() == "mike"
                or result.structured_output.name.lower() == "john"
            )

    @pytest.mark.asyncio
    @ai_snapshot_test()
    async def test_provider_strategy_recovery(self) -> None:
        pytest.importorskip("langchain_openai")

        # Note that here we assume that our CI runs model that supports provider strategy.

        class Person(BaseModel):
            name: str = Field(description="The person's full name", min_length=1)

            @model_validator(mode="after")
            def is_uppercase(self) -> "Person":
                if self.name.upper() != self.name:
                    raise ValueError("Invalid name: ALL letters must be capitalized")
                return self

        class PersonNotRestricted(BaseModel):
            name: str = Field(description="The person's full name", min_length=1)

        @model_middleware
        async def _model_middleware(
            request: ModelRequest,
            handler: ModelMiddlewareHandler,
        ) -> ModelResponse:
            try:
                return await handler(request)
            except StructuredOutputGenerationException as e:
                assert isinstance(e.error, StructuredOutputValidationError)
                assert "ALL letters must be capitalized" in e.error.validation_error
                assert len(e.message.structured_output_calls) == 0

                args = PersonNotRestricted.model_validate_json(
                    self.parse_content(e.message)
                )
                args.name = args.name.upper()

                return ModelResponse(
                    message=e.message,
                    structured_output=Person.model_validate(args.model_dump()),
                )

            raise AssertionError(  # pyright: ignore[reportUnreachable]
                "handler did not fail with StructuredOutputGenerationException"
            )

        async with Agent(
            model=(await self.model()),
            system_prompt="Respond with structured data",
            output_schema=Person,
            service=self.service,
            middleware=[
                _model_middleware,
                AssertNoCallMiddleware(),
                AssertSingleAgentMiddlewareCall(),
            ],
        ) as agent:
            result = await agent.invoke(
                [HumanMessage(content="My name is Mike, what is my name?")]
            )
            assert len(result.messages) == 2
            assert result.structured_output.name == "MIKE"

    @pytest.mark.asyncio
    @patch("splunklib.ai.engines.langchain._testing_force_tool_strategy", True)
    @ai_snapshot_test()
    async def test_tool_strategy_recovery(self) -> None:
        pytest.importorskip("langchain_openai")

        class Person(BaseModel):
            name: str = Field(description="The person's full name", min_length=1)

            @model_validator(mode="after")
            def is_uppercase(self) -> "Person":
                if self.name.upper() != self.name:
                    raise ValueError("Invalid name: ALL letters must be capitalized")
                return self

        class PersonNotRestricted(BaseModel):
            name: str = Field(description="The person's full name", min_length=1)

        @model_middleware
        async def _model_middleware(
            request: ModelRequest,
            handler: ModelMiddlewareHandler,
        ) -> ModelResponse:
            try:
                return await handler(request)
            except StructuredOutputGenerationException as e:
                assert isinstance(e.error, StructuredOutputValidationError)
                assert "ALL letters must be capitalized" in e.error.validation_error
                assert len(e.message.structured_output_calls) == 1

                args = PersonNotRestricted.model_validate(
                    e.message.structured_output_calls[0].args
                )
                args.name = args.name.upper()

                return ModelResponse(
                    message=e.message,
                    structured_output=Person.model_validate(args.model_dump()),
                )

            raise AssertionError(  # pyright: ignore[reportUnreachable]
                "handler did not fail with StructuredOutputGenerationException"
            )

        async with Agent(
            model=(await self.model()),
            system_prompt="Respond with structured data",
            output_schema=Person,
            service=self.service,
            middleware=[
                _model_middleware,
                AssertNoCallMiddleware(),
                AssertSingleAgentMiddlewareCall(),
            ],
        ) as agent:
            result = await agent.invoke(
                [HumanMessage(content="My name is Mike, what is my name?")]
            )
            assert len(result.messages) == 3
            assert result.structured_output.name == "MIKE"

    @pytest.mark.asyncio
    @ai_snapshot_test()
    async def test_default_retry_limit(self) -> None:
        pytest.importorskip("langchain_openai")

        class Person(BaseModel):
            name: str = Field(description="The person's full name", min_length=1)

        model_call_count = 0

        @model_middleware
        async def _model_middleware(
            _request: ModelRequest,
            _handler: ModelMiddlewareHandler,
        ) -> ModelResponse:
            nonlocal model_call_count
            model_call_count += 1

            raise StructuredOutputGenerationException(
                message=AIMessage(content="", calls=[]),
                error=StructuredOutputValidationError(
                    validation_error="Invalid output"
                ),
            )

        async with Agent(
            model=(await self.model()),
            system_prompt="Respond with structured data",
            output_schema=Person,
            service=self.service,
            middleware=[_model_middleware],
        ) as agent:
            with pytest.raises(
                StructuredOutputRetryLimitExceededException,
                match="Structured output retry limit of 3 exceeded",
            ):
                await agent.invoke(
                    [HumanMessage(content="My name is Mike, what is my name?")]
                )

        assert model_call_count == 4

    @pytest.mark.asyncio
    @ai_snapshot_test()
    async def test_custom_retry_limit_retry(self) -> None:
        pytest.importorskip("langchain_openai")

        class Person(BaseModel):
            name: str = Field(description="The person's full name", min_length=1)

        limits = [0, 1, 20]
        for limit in limits:
            with self.subTest(limit):
                model_call_count = 0

                @model_middleware
                async def _model_middleware(
                    _request: ModelRequest,
                    _handler: ModelMiddlewareHandler,
                ) -> ModelResponse:
                    nonlocal model_call_count
                    model_call_count += 1

                    raise StructuredOutputGenerationException(
                        message=AIMessage(content="", calls=[]),
                        error=StructuredOutputValidationError(
                            validation_error="Invalid output"
                        ),
                    )

                async with Agent(
                    model=(await self.model()),
                    system_prompt="Respond with structured data",
                    output_schema=Person,
                    service=self.service,
                    middleware=[
                        StructuredOutputRetryLimitMiddleware(limit),
                        _model_middleware,
                    ],
                ) as agent:
                    with pytest.raises(
                        StructuredOutputRetryLimitExceededException,
                        match=f"Structured output retry limit of {limit} exceeded",
                    ):
                        await agent.invoke(
                            [HumanMessage(content="My name is Mike, what is my name?")]
                        )

                # We expect limit + 1, since first LLM call is not a retry.
                assert model_call_count == limit + 1

    @pytest.mark.asyncio
    @ai_snapshot_test()
    async def test_retry_limit_is_per_agent_loop(self) -> None:
        pytest.importorskip("langchain_openai")

        class Person(BaseModel):
            name: str = Field(description="The person's full name", min_length=1)

        after_first_call = False

        @model_middleware
        async def _model_middleware(
            _request: ModelRequest,
            _handler: ModelMiddlewareHandler,
        ) -> ModelResponse:
            if after_first_call:
                return ModelResponse(
                    message=AIMessage(content="", calls=[]),
                    structured_output=Person(name="Mike"),
                )
            else:
                raise StructuredOutputGenerationException(
                    message=AIMessage(content="", calls=[]),
                    error=StructuredOutputValidationError(
                        validation_error="Invalid output"
                    ),
                )

        async with Agent(
            model=(await self.model()),
            system_prompt="Respond with structured data",
            output_schema=Person,
            service=self.service,
            middleware=[
                _model_middleware,
            ],
        ) as agent:
            with pytest.raises(
                StructuredOutputRetryLimitExceededException,
                match="Structured output retry limit of 3 exceeded",
            ):
                await agent.invoke(
                    [HumanMessage(content="My name is Mike, what is my name?")]
                )

            after_first_call = True

            # Since structured output retry limit is per agent loop, this should not fail.
            await agent.invoke(
                [HumanMessage(content="My name is Mike, what is my name?")]
            )

    @pytest.mark.asyncio
    @ai_snapshot_test()
    async def test_retry_limit_subagents(self) -> None:
        pytest.importorskip("langchain_openai")

        # This test uses subagent to make sure that StructuredOutputRetryLimitMiddleware
        # works properly with different thread_ids, since each subagent call gets a different
        # thread_id and also makes sure that it works while used concurrently, since
        # subagents are called in such way.

        class Person(BaseModel):
            name: str = Field(description="The person's full name", min_length=1)

        subagent_llm_call_count = 0

        @model_middleware
        async def _subagent_model_middleware(
            _request: ModelRequest,
            _handler: ModelMiddlewareHandler,
        ) -> ModelResponse:
            nonlocal subagent_llm_call_count
            subagent_llm_call_count += 1

            raise StructuredOutputGenerationException(
                message=AIMessage(content="", calls=[]),
                error=StructuredOutputValidationError(
                    validation_error="Invalid output"
                ),
            )

        after_first_model_response = False

        @model_middleware
        async def _supervisor_model_middleware(
            request: ModelRequest,
            _handler: ModelMiddlewareHandler,
        ) -> ModelResponse:
            nonlocal after_first_model_response
            if after_first_model_response:
                messages = request.state.messages
                assert len(messages) == 5
                assert isinstance(messages[0], HumanMessage)
                assert isinstance(messages[1], AIMessage)

                for subagent_message in messages[2:]:
                    assert isinstance(subagent_message, SubagentMessage)
                    assert isinstance(subagent_message.result, SubagentFailureResult)
                    assert (
                        subagent_message.result.error_message
                        == "Subagent invocation failed: Structured output retry limit of 3 exceeded"
                    )

                return ModelResponse(
                    message=AIMessage(content="End agent loop", calls=[])
                )
            else:
                after_first_model_response = True
                return ModelResponse(
                    message=AIMessage(
                        content="Calling subagents",
                        calls=[
                            SubagentCall(id="a-1", name="foo", args="", thread_id=None),
                            SubagentCall(id="a-2", name="foo", args="", thread_id=None),
                            SubagentCall(id="a-3", name="foo", args="", thread_id=None),
                        ],
                    ),
                )

        # Middleware that makes the StructuredOutputRetryLimitExceededException non-fatal.
        @subagent_middleware
        async def _supervisor_subagent_middleware(
            request: SubagentRequest,
            handler: SubagentMiddlewareHandler,
        ) -> SubagentResponse:
            try:
                return await handler(request)
            except StructuredOutputRetryLimitExceededException as e:
                return SubagentResponse(
                    result=SubagentFailureResult(
                        error_message=f"Subagent invocation failed: {e}"
                    )
                )

        async with (
            Agent(
                model=(await self.model()),
                system_prompt="Respond with structured data",
                output_schema=Person,
                service=self.service,
                middleware=[_subagent_model_middleware],
                name="foo",
            ) as subagent,
            Agent(
                model=(await self.model()),
                system_prompt="Respond with structured data",
                service=self.service,
                middleware=[
                    _supervisor_model_middleware,
                    _supervisor_subagent_middleware,
                ],
                agents=[subagent],
            ) as supervisor,
        ):
            await supervisor.invoke(
                [HumanMessage(content="My name is Mike, what is my name?")]
            )

        assert subagent_llm_call_count == 12

    # TODO: test what happens if model/agent middleware removes the structured_output.
    #       do we detect that? We should and raise in invoke, that output was removed.

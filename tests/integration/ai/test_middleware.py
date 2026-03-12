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
from pydantic import BaseModel, Field

from splunklib.ai import Agent
from splunklib.ai.messages import (
    AIMessage,
    AgentResponse,
    HumanMessage,
    SubagentCall,
    SubagentMessage,
    ToolCall,
    ToolMessage,
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
    agent_middleware,
    model_middleware,
    subagent_middleware,
    tool_middleware,
)
from tests.ai_testlib import AITestCase


class TestMiddleware(AITestCase):
    @patch(
        "splunklib.ai.agent._testing_local_tools_path",
        os.path.join(os.path.dirname(__file__), "testdata", "weather.py"),
    )
    @patch("splunklib.ai.agent._testing_app_id", "app_id")
    @pytest.mark.asyncio
    async def test_agent_middleware_tool_call(self) -> None:
        pytest.importorskip("langchain_openai")

        middleware_called = False

        @tool_middleware
        async def test_middleware(
            request: ToolRequest, handler: ToolMiddlewareHandler
        ) -> ToolResponse:
            nonlocal middleware_called
            middleware_called = True

            call = request.call
            assert call.name == "temperature"
            assert call.args == {"city": "Krakow"}

            state = request.state
            assert len(state.response.messages) == 2

            result = await handler(request)
            assert isinstance(result, ToolResponse)
            assert result.status == "success"
            return result

        async with Agent(
            model=await self.model(),
            system_prompt="Your name is stefan",
            service=self.service,
            middleware=[test_middleware],
            use_mcp_tools=True,
        ) as agent:
            res = await agent.invoke(
                [HumanMessage(content="What is the weather like today in Krakow?")]
            )

            response = res.messages[-1].content
            assert "31.5" in response
            assert middleware_called, "Middleware was not called"

    @patch(
        "splunklib.ai.agent._testing_local_tools_path",
        os.path.join(os.path.dirname(__file__), "testdata", "weather.py"),
    )
    @patch("splunklib.ai.agent._testing_app_id", "app_id")
    @pytest.mark.asyncio
    async def test_agent_middleware_tool_call_exception_raised(self) -> None:
        pytest.importorskip("langchain_openai")

        @tool_middleware
        async def test_middleware(
            _request: ToolRequest, _handler: ToolMiddlewareHandler
        ) -> ToolResponse:
            raise Exception("testing")

        async with Agent(
            model=await self.model(),
            system_prompt="Your name is stefan",
            service=self.service,
            middleware=[test_middleware],
            use_mcp_tools=True,
        ) as agent:
            with pytest.raises(Exception, match="testing"):
                await agent.invoke(
                    [HumanMessage(content="What is the weather like today in Krakow?")]
                )

    @patch(
        "splunklib.ai.agent._testing_local_tools_path",
        os.path.join(os.path.dirname(__file__), "testdata", "weather.py"),
    )
    @patch("splunklib.ai.agent._testing_app_id", "app_id")
    @pytest.mark.asyncio
    async def test_agent_middleware_tool_call_retry(self) -> None:
        pytest.importorskip("langchain_openai")

        middleware_called = False

        @tool_middleware
        async def test_middleware(
            request: ToolRequest, handler: ToolMiddlewareHandler
        ) -> ToolResponse:
            nonlocal middleware_called
            middleware_called = True

            first_result = await handler(request)
            second_result = await handler(request)
            assert isinstance(first_result, ToolResponse)
            assert first_result.status == "success"
            assert second_result == first_result
            return second_result

        async with Agent(
            model=await self.model(),
            system_prompt="Your name is stefan",
            service=self.service,
            middleware=[test_middleware],
            use_mcp_tools=True,
        ) as agent:
            res = await agent.invoke(
                [HumanMessage(content="What is the weather like today in Krakow?")]
            )

            response = res.messages[-1].content
            assert "31.5" in response
            assert middleware_called, "Middleware was not called"

    @patch(
        "splunklib.ai.agent._testing_local_tools_path",
        os.path.join(os.path.dirname(__file__), "testdata", "weather.py"),
    )
    @patch("splunklib.ai.agent._testing_app_id", "app_id")
    @pytest.mark.asyncio
    async def test_agent_middleware_tool_made_up_response(self) -> None:
        pytest.importorskip("langchain_openai")

        middleware_called = False

        @tool_middleware
        async def test_middleware(
            request: ToolRequest, _handler: ToolMiddlewareHandler
        ) -> ToolResponse:
            nonlocal middleware_called
            middleware_called = True

            call = request.call
            assert call.id, "Invalid call id received"
            return ToolResponse(content="0.5C")

        async with Agent(
            model=await self.model(),
            system_prompt="Your name is stefan",
            service=self.service,
            middleware=[test_middleware],
            use_mcp_tools=True,
        ) as agent:
            res = await agent.invoke(
                [HumanMessage(content="What is the weather like today in Kraków?")]
            )

            response = res.messages[-1].content
            assert "0.5" in response, "Invalid response from LLM"

            tool_message = next(
                (tm for tm in res.messages if isinstance(tm, ToolMessage)), None
            )
            assert tool_message, "ToolMessage not found in messages"
            assert tool_message.content == "0.5C", "Invalid response from Tool"
            assert middleware_called, "Middleware was not called"

    @patch(
        "splunklib.ai.agent._testing_local_tools_path",
        os.path.join(os.path.dirname(__file__), "testdata", "weather.py"),
    )
    @patch("splunklib.ai.agent._testing_app_id", "app_id")
    @pytest.mark.asyncio
    async def test_agent_two_tool_middlewares(self) -> None:
        pytest.importorskip("langchain_openai")

        first_called = False
        second_called = False

        @tool_middleware
        async def first_middleware(
            request: ToolRequest, handler: ToolMiddlewareHandler
        ) -> ToolResponse:
            assert not second_called, "Second middleware was called before the first"

            nonlocal first_called
            first_called = True
            return await handler(request)

        @tool_middleware
        async def second_middleware(
            request: ToolRequest, handler: ToolMiddlewareHandler
        ) -> ToolResponse:
            assert first_called, "First middleware wasn't called before the second"

            nonlocal second_called
            second_called = True
            return await handler(request)

        async with Agent(
            model=await self.model(),
            system_prompt="You are a helpful assistant",
            service=self.service,
            middleware=[first_middleware, second_middleware],
            use_mcp_tools=True,
        ) as agent:
            res = await agent.invoke(
                [HumanMessage(content="What is the weather like today in Krakow?")]
            )
            assert "31.5" in res.messages[-1].content
            assert first_called, "First middleware was called after the second"
            assert second_called, "Second middleware was called before the first"

    @patch(
        "splunklib.ai.agent._testing_local_tools_path",
        os.path.join(os.path.dirname(__file__), "testdata", "weather.py"),
    )
    @patch("splunklib.ai.agent._testing_app_id", "app_id")
    @pytest.mark.asyncio
    async def test_agent_tool_and_model_middlewares(self) -> None:
        pytest.importorskip("langchain_openai")

        tool_called = False
        model_called = False

        @tool_middleware
        async def tool_test_middleware(
            request: ToolRequest, handler: ToolMiddlewareHandler
        ) -> ToolResponse:
            nonlocal tool_called
            tool_called = True
            return await handler(request)

        @model_middleware
        async def model_test_middleware(
            request: ModelRequest, handler: ModelMiddlewareHandler
        ) -> ModelResponse:
            nonlocal model_called
            model_called = True
            return await handler(request)

        async with Agent(
            model=await self.model(),
            system_prompt="You are a helpful assistant",
            service=self.service,
            middleware=[tool_test_middleware, model_test_middleware],
            use_mcp_tools=True,
        ) as agent:
            res = await agent.invoke(
                [HumanMessage(content="What is the weather like today in Krakow?")]
            )
            assert "31.5" in res.messages[-1].content
            assert tool_called
            assert model_called

    @patch(
        "splunklib.ai.agent._testing_local_tools_path",
        os.path.join(os.path.dirname(__file__), "testdata", "weather.py"),
    )
    @patch("splunklib.ai.agent._testing_app_id", "app_id")
    @pytest.mark.asyncio
    async def test_agent_class_middleware_model_tool_subagent(self) -> None:
        pytest.importorskip("langchain_openai")

        model_called = False
        tool_called = False
        subagent_called = False

        class ExampleMiddleware(AgentMiddleware):
            @override
            async def model_middleware(
                self, request: ModelRequest, handler: ModelMiddlewareHandler
            ) -> ModelResponse:
                nonlocal model_called
                model_called = True
                return await handler(request)

            @override
            async def tool_middleware(
                self, request: ToolRequest, handler: ToolMiddlewareHandler
            ) -> ToolResponse:
                nonlocal tool_called
                tool_called = True
                return await handler(request)

            @override
            async def subagent_middleware(
                self, request: SubagentRequest, handler: SubagentMiddlewareHandler
            ) -> SubagentResponse:
                nonlocal subagent_called
                subagent_called = True
                return await handler(request)

        middleware = ExampleMiddleware()

        async with Agent(
            model=await self.model(),
            system_prompt="You are a helpful assistant.",
            service=self.service,
            middleware=[middleware],
            use_mcp_tools=True,
        ) as agent:
            tool_result = await agent.invoke(
                [HumanMessage(content="What is the weather like today in Krakow?")]
            )
            assert "31.5" in tool_result.messages[-1].content

        class NicknameGeneratorInput(BaseModel):
            name: str = Field(description="The person's full name", min_length=1)

        async with (
            Agent(
                model=await self.model(),
                system_prompt=(
                    "You are a helpful assistant that generates nicknames. A valid "
                    + "nickname consists of the provided name suffixed with '-zilla.'"
                ),
                service=self.service,
                name="NicknameGeneratorAgent",
                description="Pass a name and get a nickname",
                input_schema=NicknameGeneratorInput,
            ) as subagent,
            Agent(
                model=await self.model(),
                system_prompt="You are a supervisor agent that MUST use other agents",
                agents=[subagent],
                service=self.service,
                middleware=[middleware],
            ) as supervisor,
        ):
            subagent_result = await supervisor.invoke(
                [HumanMessage(content="Generate a nickname for Chris")]
            )
            assert "Chris-zilla" in subagent_result.messages[-1].content

        assert model_called
        assert tool_called
        assert subagent_called

    @pytest.mark.asyncio
    async def test_agent_uses_subagent(self) -> None:
        pytest.importorskip("langchain_openai")

        middleware_called = False

        class NicknameGeneratorInput(BaseModel):
            name: str = Field(description="The person's full name", min_length=1)

        @subagent_middleware
        async def test_middleware(
            request: SubagentRequest, handler: SubagentMiddlewareHandler
        ) -> SubagentResponse:
            nonlocal middleware_called
            middleware_called = True

            call = request.call
            assert call.name == "NicknameGeneratorAgent"
            assert call.args == {"name": "Chris"}

            first_result = await handler(request)
            second_result = await handler(request)
            assert isinstance(first_result, SubagentResponse)
            assert first_result.status == "success"
            assert second_result == first_result
            return second_result

        async with (
            Agent(
                model=await self.model(),
                system_prompt=(
                    "You are a helpful assistant that generates nicknames. A valid "
                    + "nickname consists of the provided name suffixed with '-zilla.'"
                ),
                service=self.service,
                name="NicknameGeneratorAgent",
                description="Pass a name and get a nickname",
                input_schema=NicknameGeneratorInput,
            ) as subagent,
            Agent(
                model=await self.model(),
                system_prompt="You are a supervisor agent that MUST use other agents",
                agents=[subagent],
                service=self.service,
                middleware=[test_middleware],
            ) as supervisor,
        ):
            result = await supervisor.invoke(
                [
                    HumanMessage(
                        content="hi, my name is Chris. Generate a nickname for me"
                    )
                ]
            )

            subagent_message = next(
                (m for m in result.messages if isinstance(m, SubagentMessage)), None
            )
            assert subagent_message, "No subagent message found in response"

            response = result.messages[-1].content
            assert "Chris-zilla" in response, "Agent did generate valid nickname"

            assert middleware_called, "Middleware was not called"

    @pytest.mark.asyncio
    async def test_agent_middleware_subagent_made_up_response(self) -> None:
        pytest.importorskip("langchain_openai")

        middleware_called = False

        class NicknameGeneratorInput(BaseModel):
            name: str = Field(description="The person's full name", min_length=1)

        @subagent_middleware
        async def test_middleware(
            request: SubagentRequest, _handler: SubagentMiddlewareHandler
        ) -> SubagentResponse:
            nonlocal middleware_called
            middleware_called = True

            call = request.call
            assert call.id, "Invalid call id received"
            return SubagentResponse(content="Chris-superstar")

        async with (
            Agent(
                model=await self.model(),
                system_prompt=(
                    "You are a helpful assistant that generates nicknames. A valid "
                    + "nickname consists of the provided name suffixed with '-zilla.'"
                ),
                service=self.service,
                name="NicknameGeneratorAgent",
                description="Pass a name and get a nickname",
                input_schema=NicknameGeneratorInput,
            ) as subagent,
            Agent(
                model=await self.model(),
                system_prompt="You are a supervisor agent that MUST use other agents",
                agents=[subagent],
                service=self.service,
                middleware=[test_middleware],
            ) as supervisor,
        ):
            result = await supervisor.invoke(
                [HumanMessage(content="Generate a nickname for Chris")]
            )

            response = result.messages[-1].content
            assert "Chris-superstar" in response, "Invalid response from LLM"

            subagent_message = next(
                (sm for sm in result.messages if isinstance(sm, SubagentMessage)), None
            )
            assert subagent_message, "SubagentMessage not found in messages"
            assert subagent_message.content == "Chris-superstar", (
                "Invalid response from subagent"
            )
            assert middleware_called, "Middleware was not called"

    @pytest.mark.asyncio
    @patch(
        "splunklib.ai.agent._testing_local_tools_path",
        os.path.join(os.path.dirname(__file__), "testdata", "weather.py"),
    )
    @patch("splunklib.ai.agent._testing_app_id", "app_id")
    async def test_agent_middleware_model_retry(self) -> None:
        pytest.importorskip("langchain_openai")

        middleware_called = False

        @model_middleware
        async def test_middleware(
            request: ModelRequest, handler: ModelMiddlewareHandler
        ) -> ModelResponse:
            nonlocal middleware_called
            middleware_called = True

            first_result = await handler(request)
            assert isinstance(first_result, ModelResponse)

            second_result = await handler(request)

            # Only if it's a model response that contains the tool calls
            if first_result.message.calls:
                tool_call = first_result.message.calls[0]
                assert isinstance(tool_call, ToolCall)

                second_tool_call = first_result.message.calls[0]
                assert isinstance(second_tool_call, ToolCall)

                assert tool_call.name == second_tool_call.name == "temperature"
                assert tool_call.args == second_tool_call.args == {"city": "Kraków"}

            return second_result

        async with Agent(
            model=await self.model(),
            system_prompt=(
                "You are a helpful assistant. "
                + "You MUST use available tools when asked about weather."
            ),
            service=self.service,
            middleware=[test_middleware],
            use_mcp_tools=True,
        ) as agent:
            await agent.invoke(
                [HumanMessage(content="What is the weather like today in Kraków?")]
            )

            assert middleware_called, "Middleware was not called"

    @pytest.mark.asyncio
    async def test_agent_middleware_model_retry_subagent_call(self) -> None:
        pytest.importorskip("langchain_openai")

        middleware_called = False

        class NicknameGeneratorInput(BaseModel):
            name: str = Field(description="The person's full name", min_length=1)

        @model_middleware
        async def test_middleware(
            request: ModelRequest, handler: ModelMiddlewareHandler
        ) -> ModelResponse:
            nonlocal middleware_called
            middleware_called = True

            first_result = await handler(request)
            assert isinstance(first_result, ModelResponse)

            second_result = await handler(request)

            # only if it's a model response that contains the subagent calls
            if first_result.message.calls:
                subagent_call = first_result.message.calls[0]
                assert isinstance(subagent_call, SubagentCall)

                second_subagent_call = first_result.message.calls[0]
                assert isinstance(second_subagent_call, SubagentCall)

                assert (
                    subagent_call.name
                    == second_subagent_call.name
                    == "NicknameGeneratorAgent"
                )
                assert (
                    subagent_call.args == second_subagent_call.args == {"name": "Chris"}
                )

            return second_result

        async with (
            Agent(
                model=await self.model(),
                system_prompt=(
                    "You are a helpful assistant that generates nicknames. A valid "
                    + "nickname consists of the provided name suffixed with '-zilla.'"
                ),
                service=self.service,
                name="NicknameGeneratorAgent",
                description="Pass a name and get a nickname",
                input_schema=NicknameGeneratorInput,
            ) as subagent,
            Agent(
                model=await self.model(),
                system_prompt="You are a supervisor agent that MUST use other agents",
                agents=[subagent],
                service=self.service,
                middleware=[test_middleware],
            ) as supervisor,
        ):
            result = await supervisor.invoke(
                [HumanMessage(content="Generate a nickname for Chris")]
            )

            response = result.messages[-1].content
            assert "Chris-zilla" in response, "Agent did generate valid nickname"
            assert middleware_called, "Middleware was not called"

    @pytest.mark.asyncio
    async def test_agent_middleware_model_made_up_response(self) -> None:
        pytest.importorskip("langchain_openai")

        middleware_called = False

        @model_middleware
        async def test_middleware(
            _request: ModelRequest, _handler: ModelMiddlewareHandler
        ) -> ModelResponse:
            nonlocal middleware_called
            middleware_called = True

            return ModelResponse(
                message=AIMessage(content="My response is made up", calls=[])
            )

        async with Agent(
            model=await self.model(),
            system_prompt="Your name is stefan",
            service=self.service,
            middleware=[test_middleware],
        ) as agent:
            res = await agent.invoke(
                [
                    HumanMessage(
                        content="Dzień dobry, what is the weather like today in Kraków?"
                    )
                ]
            )

            response = res.messages[-1].content
            assert "My response is made up" == response
            assert middleware_called, "Middleware was not called"

    @pytest.mark.asyncio
    async def test_agent_middleware_model_exception_raised(self) -> None:
        pytest.importorskip("langchain_openai")

        @model_middleware
        async def test_middleware(
            _request: ModelRequest, _handler: ModelMiddlewareHandler
        ) -> ModelResponse:
            raise Exception("testing")

        async with Agent(
            model=await self.model(),
            system_prompt="Your name is stefan",
            service=self.service,
            middleware=[test_middleware],
        ) as agent:
            with pytest.raises(Exception, match="testing"):
                await agent.invoke(
                    [
                        HumanMessage(
                            content="Dzień dobry, what is the weather like today in Kraków?"
                        )
                    ]
                )

    @pytest.mark.asyncio
    async def test_model_middleware_structured_output(self) -> None:
        pytest.importorskip("langchain_openai")

        # Regression test - make sure that model middleware does not
        # cause structured output to be dropped.

        class Output(BaseModel):
            name: str = Field(description="name of the Person")

        @model_middleware
        async def test_middleware(
            req: ModelRequest, handler: ModelMiddlewareHandler
        ) -> ModelResponse:
            return await handler(req)

        async with Agent(
            model=await self.model(),
            system_prompt="Your name is stefan",
            service=self.service,
            middleware=[test_middleware],
            output_schema=Output,
        ) as agent:
            resp = await agent.invoke([HumanMessage(content="What is your name?")])
            assert resp.structured_output.name.lower() == "stefan"

    @pytest.mark.asyncio
    async def test_model_middleware_modify_structured_output(self) -> None:
        pytest.importorskip("langchain_openai")

        class Output(BaseModel):
            name: str = Field(description="name of the Person")

        @model_middleware
        async def test_middleware(
            req: ModelRequest, handler: ModelMiddlewareHandler
        ) -> ModelResponse:
            resp = await handler(req)
            assert type(resp.structured_output) is Output
            resp.structured_output.name = "Mike"
            return resp

        async with Agent(
            model=await self.model(),
            system_prompt="Your name is stefan",
            service=self.service,
            middleware=[test_middleware],
            output_schema=Output,
        ) as agent:
            resp = await agent.invoke([HumanMessage(content="What is your name?")])
            assert resp.structured_output.name == "Mike"

    @pytest.mark.asyncio
    async def test_model_middleware_made_up_structured_output(self) -> None:
        pytest.importorskip("langchain_openai")

        class Output(BaseModel):
            name: str = Field(description="name of the Person")

        @model_middleware
        async def test_middleware(
            _req: ModelRequest, _handler: ModelMiddlewareHandler
        ) -> ModelResponse:
            return ModelResponse(
                message=AIMessage(content="Stefan", calls=[]),
                structured_output=Output(name="Stefan"),
            )

        async with Agent(
            model=await self.model(),
            system_prompt="Your name is stefan",
            service=self.service,
            middleware=[test_middleware],
            output_schema=Output,
        ) as agent:
            resp = await agent.invoke([HumanMessage(content="What is your name?")])
            assert resp.structured_output.name.lower() == "stefan"

    @pytest.mark.asyncio
    async def test_agent_middleware(self) -> None:
        pytest.importorskip("langchain_openai")

        @agent_middleware
        async def test_middleware(
            req: AgentRequest,
            handler: AgentMiddlewareHandler,
        ) -> AgentResponse:
            assert len(req.messages) == 1
            assert req.messages[0] == HumanMessage(
                content="What is the weather like today in Krakow?"
            )
            resp = await handler(req)
            assert len(resp.messages) > 1
            assert isinstance(resp.messages[-1], AIMessage)
            return resp

        async with Agent(
            model=await self.model(),
            system_prompt="Your name is stefan",
            service=self.service,
            middleware=[test_middleware],
        ) as agent:
            resp = await agent.invoke(
                [HumanMessage(content="What is the weather like today in Krakow?")]
            )
            assert len(resp.messages) > 1
            assert isinstance(resp.messages[-1], AIMessage)

    @pytest.mark.asyncio
    async def test_agent_middleware_class_based(self) -> None:
        pytest.importorskip("langchain_openai")

        class Middleware(AgentMiddleware):
            @override
            async def agent_middleware(
                self,
                request: AgentRequest,
                handler: AgentMiddlewareHandler,
            ) -> AgentResponse[Any | None]:
                return AgentResponse(
                    messages=[
                        HumanMessage(
                            content="What is the weather like today in Krakow?"
                        ),
                        AIMessage(content="Cloudy", calls=[]),
                    ],
                    structured_output=None,
                )

        async with Agent(
            model=await self.model(),
            system_prompt="Your name is stefan",
            service=self.service,
            middleware=[Middleware()],
        ) as agent:
            resp = await agent.invoke(
                [HumanMessage(content="What is the weather like today in Krakow?")]
            )
            assert len(resp.messages) > 1
            assert isinstance(resp.messages[-1], AIMessage)

    @pytest.mark.asyncio
    async def test_agent_middleware_exception(self) -> None:
        pytest.importorskip("langchain_openai")

        @agent_middleware
        async def test_middleware(
            _req: AgentRequest,
            _handler: AgentMiddlewareHandler,
        ) -> AgentResponse:
            raise Exception("testing")

        async with Agent(
            model=await self.model(),
            system_prompt="Your name is stefan",
            service=self.service,
            middleware=[test_middleware],
        ) as agent:
            with pytest.raises(Exception, match="testing"):
                _ = await agent.invoke(
                    [HumanMessage(content="What is the weather like today in Krakow?")]
                )

    @pytest.mark.asyncio
    async def test_agent_middleware_fake_response(self) -> None:
        pytest.importorskip("langchain_openai")

        @agent_middleware
        async def test_middleware(
            _req: AgentRequest,
            _handler: AgentMiddlewareHandler,
        ) -> AgentResponse:
            return AgentResponse(
                messages=[
                    HumanMessage(content="What is the weather like today in Krakow?"),
                    AIMessage(content="Cloudy", calls=[]),
                ],
                structured_output=None,
            )

        async with Agent(
            model=await self.model(),
            system_prompt="Your name is stefan",
            service=self.service,
            middleware=[test_middleware],
        ) as agent:
            resp = await agent.invoke(
                [HumanMessage(content="What is the weather like today in Krakow?")]
            )
            assert len(resp.messages) == 2
            assert resp.messages[1] == AIMessage(content="Cloudy", calls=[])

    @pytest.mark.asyncio
    async def test_agent_middleware_retry(self) -> None:
        pytest.importorskip("langchain_openai")

        @agent_middleware
        async def test_middleware(
            req: AgentRequest,
            handler: AgentMiddlewareHandler,
        ) -> AgentResponse:
            resp = await handler(req)
            assert len(resp.messages) > 1
            assert isinstance(resp.messages[-1], AIMessage)
            resp = await handler(req)
            assert len(resp.messages) > 1
            assert isinstance(resp.messages[-1], AIMessage)
            return resp

        async with Agent(
            model=await self.model(),
            system_prompt="Your name is stefan",
            service=self.service,
            middleware=[test_middleware],
        ) as agent:
            resp = await agent.invoke(
                [HumanMessage(content="What is the weather like today in Krakow?")]
            )
            assert len(resp.messages) > 1
            assert isinstance(resp.messages[-1], AIMessage)

    @pytest.mark.asyncio
    async def test_agent_middleware_multiple(self) -> None:
        pytest.importorskip("langchain_openai")

        test1_called = False
        test2_called = False

        @agent_middleware
        async def test1_middleware(
            req: AgentRequest,
            handler: AgentMiddlewareHandler,
        ) -> AgentResponse:
            nonlocal test1_called, test2_called
            assert not test1_called and not test2_called
            test1_called = True
            resp = await handler(req)
            assert test1_called and test2_called
            return resp

        @agent_middleware
        async def test2_middleware(
            _req: AgentRequest,
            _handler: AgentMiddlewareHandler,
        ) -> AgentResponse:
            nonlocal test1_called, test2_called
            assert test1_called and not test2_called
            test2_called = True
            return AgentResponse(
                messages=[
                    HumanMessage(content="What is the weather like today in Krakow?"),
                    AIMessage(content="Cloudy", calls=[]),
                ],
                structured_output=None,
            )

        async with Agent(
            model=await self.model(),
            system_prompt="Your name is stefan",
            service=self.service,
            middleware=[test1_middleware, test2_middleware],
        ) as agent:
            resp = await agent.invoke(
                [HumanMessage(content="What is the weather like today in Krakow?")]
            )
            assert len(resp.messages) > 1
            assert isinstance(resp.messages[-1], AIMessage)

    @pytest.mark.asyncio
    async def test_agent_middleware_structured_output(self) -> None:
        pytest.importorskip("langchain_openai")

        class Output(BaseModel):
            name: str = Field(description="name of the Person")

        @agent_middleware
        async def test_middleware(
            req: AgentRequest,
            handler: AgentMiddlewareHandler,
        ) -> AgentResponse:
            resp = await handler(req)
            assert resp.structured_output is not None
            assert type(resp.structured_output) is Output
            assert resp.structured_output.name.lower() == "stefan"
            return resp

        async with Agent(
            model=await self.model(),
            system_prompt="Your name is Stefan",
            service=self.service,
            middleware=[test_middleware],
            output_schema=Output,
        ) as agent:
            resp = await agent.invoke([HumanMessage(content="What is your name?")])
            assert resp.structured_output is not None
            assert type(resp.structured_output) is Output
            assert resp.structured_output.name.lower() == "stefan"

    @pytest.mark.asyncio
    async def test_agent_middleware_missing_structured_output(self) -> None:
        pytest.importorskip("langchain_openai")

        class Output(BaseModel):
            name: str = Field(description="name of the Person")

        @agent_middleware
        async def test_middleware(
            _req: AgentRequest,
            _handler: AgentMiddlewareHandler,
        ) -> AgentResponse:
            return AgentResponse(
                messages=[
                    HumanMessage(content="What is your name?"),
                    AIMessage(content="Stefan", calls=[]),
                ],
                structured_output=None,
            )

        async with Agent(
            model=await self.model(),
            system_prompt="Your name is Stefan",
            service=self.service,
            middleware=[test_middleware],
            output_schema=Output,
        ) as agent:
            with pytest.raises(
                AssertionError, match="Agent middleware discarded a structured output"
            ):
                _ = await agent.invoke([HumanMessage(content="What is your name?")])

    @pytest.mark.asyncio
    async def test_agent_middleware_invalid_structured_output_type(self) -> None:
        pytest.importorskip("langchain_openai")

        class Output(BaseModel):
            name: str = Field(description="name of the Person")

        class Output2(BaseModel):
            name: str = Field(description="name of the Person")

        @agent_middleware
        async def test_middleware(
            _req: AgentRequest,
            _handler: AgentMiddlewareHandler,
        ) -> AgentResponse:
            return AgentResponse[Any | None](
                messages=[
                    HumanMessage(content="What is your name?"),
                    AIMessage(content="Stefan", calls=[]),
                ],
                structured_output=Output2(name="Stefan"),
            )

        async with Agent(
            model=await self.model(),
            system_prompt="Your name is Stefan",
            service=self.service,
            middleware=[test_middleware],
            output_schema=Output,
        ) as agent:
            with pytest.raises(
                AssertionError,
                match="Agent middleware returned an invalid structured_output type:",
            ):
                _ = await agent.invoke([HumanMessage(content="What is your name?")])

    @pytest.mark.asyncio
    async def test_agent_middleware_unexpected_additional_structured_output(
        self,
    ) -> None:
        pytest.importorskip("langchain_openai")

        class Output(BaseModel):
            name: str = Field(description="name of the Person")

        @agent_middleware
        async def test_middleware(
            _req: AgentRequest,
            _handler: AgentMiddlewareHandler,
        ) -> AgentResponse:
            return AgentResponse[Any | None](
                messages=[
                    HumanMessage(content="What is your name?"),
                    AIMessage(content="Stefan", calls=[]),
                ],
                structured_output=Output(name="Stefan"),
            )

        async with Agent(
            model=await self.model(),
            system_prompt="Your name is Stefan",
            service=self.service,
            middleware=[test_middleware],
        ) as agent:
            with pytest.raises(
                AssertionError,
                match="Agent middleware unexpectedly included a structured output",
            ):
                _ = await agent.invoke([HumanMessage(content="What is your name?")])

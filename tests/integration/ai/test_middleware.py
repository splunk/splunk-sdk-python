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
from typing import override
from unittest.mock import patch

import pytest
from pydantic import BaseModel, Field

from splunklib.ai import Agent
from splunklib.ai.messages import (
    AIMessage,
    HumanMessage,
    SubagentCall,
    SubagentMessage,
    ToolCall,
    ToolMessage,
)
from splunklib.ai.middleware import (
    AgentMiddleware,
    ModelMiddlewareHandler,
    ModelRequest,
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
        ) -> AIMessage:
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
            ) -> AIMessage:
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
        ) -> AIMessage:
            nonlocal middleware_called
            middleware_called = True

            first_result = await handler(request)
            assert isinstance(first_result, AIMessage)

            second_result = await handler(request)

            # Only if it's a model response that contains the tool calls
            if first_result.calls:
                tool_call = first_result.calls[0]
                assert isinstance(tool_call, ToolCall)

                second_tool_call = first_result.calls[0]
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
        ) -> AIMessage:
            nonlocal middleware_called
            middleware_called = True

            first_result = await handler(request)
            assert isinstance(first_result, AIMessage)

            second_result = await handler(request)

            # only if it's a model response that contains the subagent calls
            if first_result.calls:
                subagent_call = first_result.calls[0]
                assert isinstance(subagent_call, SubagentCall)

                second_subagent_call = first_result.calls[0]
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
        ) -> AIMessage:
            nonlocal middleware_called
            middleware_called = True

            return AIMessage(content="My response is made up")

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
        ) -> AIMessage:
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

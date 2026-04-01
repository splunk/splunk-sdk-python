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

import pytest

from splunklib.ai import Agent
from splunklib.ai.conversation_store import InMemoryStore
from splunklib.ai.messages import AgentResponse, AIMessage, HumanMessage
from splunklib.ai.middleware import (
    AgentMiddlewareHandler,
    AgentRequest,
    ModelMiddlewareHandler,
    ModelRequest,
    ModelResponse,
    agent_middleware,
    model_middleware,
)
from tests.ai_testlib import AITestCase


class TestConversationStore(AITestCase):
    @pytest.mark.asyncio
    async def test_agent_does_not_remember_state_without_store(self) -> None:
        pytest.importorskip("langchain_openai")

        async with Agent(
            model=(await self.model()),
            system_prompt="You are a helpful assistant.",
            service=self.service,
        ) as agent:
            _ = await agent.invoke([HumanMessage(content="hi, my name is Chris")])

            result = await agent.invoke([HumanMessage(content="What is my name?")])

            response = result.final_message.content

            assert "Chris" not in response, "Agent remembered the name"

    @pytest.mark.asyncio
    async def test_agent_remembers_state(self) -> None:
        pytest.importorskip("langchain_openai")

        model_middleware_called = False
        agent_middleware_called = False
        after_first_call = False

        @model_middleware
        async def _model_middleware(
            request: ModelRequest,
            handler: ModelMiddlewareHandler,
        ) -> ModelResponse:
            nonlocal model_middleware_called
            model_middleware_called = True

            if after_first_call:
                # Previous messages included.
                assert len(request.state.response.messages) == 3
            else:
                assert len(request.state.response.messages) == 1
            return await handler(request)

        @agent_middleware
        async def _agent_middleware(
            request: AgentRequest,
            handler: AgentMiddlewareHandler,
        ) -> AgentResponse:
            nonlocal agent_middleware_called
            agent_middleware_called = True

            assert len(request.messages) == 1
            resp = await handler(request)
            if after_first_call:
                # Previous messages included.
                assert len(resp.messages) == 4
            else:
                assert len(resp.messages) == 2
            return resp

        async with Agent(
            model=(await self.model()),
            system_prompt="You are a helpful assistant.",
            service=self.service,
            middleware=[_model_middleware, _agent_middleware],
            conversation_store=InMemoryStore(),
        ) as agent:
            _ = await agent.invoke([HumanMessage(content="hi, my name is Chris")])

            after_first_call = True

            result = await agent.invoke([HumanMessage(content="What is my name?")])

            response = result.final_message.content

            assert "Chris" in response, "Agent did not remember the name"

        assert model_middleware_called
        assert agent_middleware_called

    @pytest.mark.asyncio
    async def test_remembers_result_of_agent_middleware(self) -> None:
        pytest.importorskip("langchain_openai")

        agent_middleware_called = False
        after_first_call = False

        @agent_middleware
        async def _agent_middleware(
            request: AgentRequest,
            handler: AgentMiddlewareHandler,
        ) -> AgentResponse:
            nonlocal agent_middleware_called
            agent_middleware_called = True

            if not after_first_call:
                return AgentResponse(
                    messages=[
                        HumanMessage("My name is Mike"),
                        AIMessage(content="Hi Mike!", calls=[]),
                    ],
                    structured_output=None,
                )
            return await handler(request)

        async with Agent(
            model=(await self.model()),
            system_prompt="You are a helpful assistant.",
            service=self.service,
            middleware=[_agent_middleware],
            conversation_store=InMemoryStore(),
        ) as agent:
            _ = await agent.invoke([HumanMessage(content="hi, my name is Chris")])

            after_first_call = True

            result = await agent.invoke([HumanMessage(content="What is my name?")])

            response = result.final_message.content

            assert "Mike" in response, "Agent did not remember the name"

        assert agent_middleware_called

    @pytest.mark.asyncio
    async def test_invoke_thread_id(self) -> None:
        pytest.importorskip("langchain_openai")

        model_middleware_called = False

        @model_middleware
        async def _model_middleware(
            request: ModelRequest,
            handler: ModelMiddlewareHandler,
        ) -> ModelResponse:
            nonlocal model_middleware_called
            model_middleware_called = True

            assert len(request.state.response.messages) == 1
            return await handler(request)

        async with Agent(
            model=(await self.model()),
            system_prompt="You are a helpful assistant.",
            service=self.service,
            middleware=[_model_middleware],
            conversation_store=InMemoryStore(),
        ) as agent:
            _ = await agent.invoke(
                [HumanMessage(content="Hi, my name is Chris")],
                thread_id="1",
            )

            result = await agent.invoke(
                [HumanMessage(content="What is my name?")],
                thread_id="2",
            )
            response = result.final_message.content
            assert "Mike" not in response, (
                "Agent remembered the name from a different thread_id"
            )

        assert model_middleware_called

    @pytest.mark.asyncio
    async def test_thread_id_in_constructor(self) -> None:
        pytest.importorskip("langchain_openai")

        conversation_store = InMemoryStore()

        async with Agent(
            model=(await self.model()),
            system_prompt="You are a helpful assistant.",
            service=self.service,
            conversation_store=conversation_store,
            thread_id="2",
        ) as agent:
            _ = await agent.invoke(
                [HumanMessage(content="Hi, my name is Chris")],
                thread_id="1",
            )

            _ = await agent.invoke(
                [HumanMessage(content="Hi, my name is Mike")],
                thread_id="2",
            )

            result = await agent.invoke(
                [HumanMessage(content="What is my name?")],
                thread_id="2",
            )
            response = result.final_message.content
            assert "Mike" in response, "Agent did not remember the name"

            # When thread_id not specified the one from the agent constructor is used.
            result = await agent.invoke(
                [HumanMessage(content="What is my name?")],
            )
            response = result.final_message.content
            assert "Mike" in response, "Agent did not remember the name"

        # Now use the same conversation_store in a different agent with same thread_ids.

        async with Agent(
            model=(await self.model()),
            system_prompt="You are a helpful assistant.",
            service=self.service,
            conversation_store=conversation_store,
            thread_id="2",
        ) as agent:
            result = await agent.invoke(
                [HumanMessage(content="What is my name?")],
                thread_id="1",
            )
            response = result.final_message.content
            assert "Chris" in response, "Agent did not remember the name"

            result = await agent.invoke(
                [HumanMessage(content="What is my name?")],
                thread_id="2",
            )
            response = result.final_message.content
            assert "Mike" in response, "Agent did not remember the name"

            # When thread_id not specified the one from the agent constructor is used.
            result = await agent.invoke(
                [HumanMessage(content="What is my name?")],
            )
            response = result.final_message.content
            assert "Mike" in response, "Agent did not remember the name"

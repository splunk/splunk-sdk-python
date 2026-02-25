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

import time
from typing import final, override

import pytest
from pydantic import BaseModel, Field

from splunklib.ai import Agent
from splunklib.ai.hooks import (
    AgentHook,
    AgentState,
    StepsLimitExceededException,
    TimeoutExceededException,
    TokenLimitExceededException,
    after_agent,
    after_model,
    before_agent,
    before_model,
    step_limit,
    timeout_limit,
    token_limit,
)
from splunklib.ai.messages import HumanMessage
from tests.ai_testlib import AITestCase


class TestHook(AITestCase):
    @pytest.mark.asyncio
    async def test_agent_hook(self):
        pytest.importorskip("langchain_openai")

        hook_calls = 0

        @final
        class TestHook(AgentHook):
            type = "before_model"

            @override
            def __call__(self, state: AgentState) -> None:
                nonlocal hook_calls
                hook_calls += 1
                assert len(state.response.messages) == 1

        @final
        class TestAsyncHook(AgentHook):
            type = "before_model"

            @override
            async def __call__(self, state: AgentState) -> None:
                nonlocal hook_calls
                hook_calls += 1
                assert len(state.response.messages) == 1

        async with Agent(
            model=(await self.model()),
            system_prompt="Your name is stefan",
            service=self.service,
            hooks=[TestHook(), TestAsyncHook()],
        ) as agent:
            result = await agent.invoke(
                [
                    HumanMessage(
                        content="What is your name? Answer in one word",
                    )
                ]
            )

            response = result.messages[-1].content.strip().lower().replace(".", "")
            assert "stefan" == response
            assert hook_calls == 2

    @pytest.mark.asyncio
    async def test_agent_hook_decorator(self):
        pytest.importorskip("langchain_openai")

        hook_calls = 0

        @before_model
        def test_hook_before(state: AgentState) -> None:
            nonlocal hook_calls
            hook_calls += 1

            assert len(state.response.messages) == 1

        @before_model
        async def test_async_hook_before(state: AgentState) -> None:
            nonlocal hook_calls
            hook_calls += 1

            assert len(state.response.messages) == 1

        @after_model
        def test_hook_after(state: AgentState) -> None:
            nonlocal hook_calls
            hook_calls += 1

            assert len(state.response.messages) == 2

        @after_model
        async def test_async_hook_after(state: AgentState) -> None:
            nonlocal hook_calls
            hook_calls += 1

            assert len(state.response.messages) == 2

        async with Agent(
            model=(await self.model()),
            system_prompt="Your name is stefan",
            service=self.service,
            hooks=[
                test_hook_before,
                test_async_hook_before,
                test_hook_after,
                test_async_hook_after,
            ],
        ) as agent:
            result = await agent.invoke(
                [
                    HumanMessage(
                        content="What is your name? Answer in one word",
                    )
                ]
            )

            response = result.messages[-1].content.strip().lower().replace(".", "")
            assert "stefan" == response
            assert hook_calls == 4

    @pytest.mark.asyncio
    async def test_agent_hook_agent(self):
        pytest.importorskip("langchain_openai")

        class Person(BaseModel):
            name: str = Field(description="The person's name", min_length=4)

        hook_calls = 0

        @before_agent
        def before_agent_hook(state: AgentState) -> None:
            nonlocal hook_calls
            hook_calls += 1

            assert len(state.response.messages) == 1

        @before_agent
        async def before_async_agent_hook(state: AgentState) -> None:
            nonlocal hook_calls
            hook_calls += 1

            assert len(state.response.messages) == 1

        @after_agent
        async def after_agent_hook(state: AgentState) -> None:
            nonlocal hook_calls
            hook_calls += 1

            person = state.response.structured_output
            assert person.name.lower() == "stefan"
            assert len(state.response.messages) == 2

        @after_agent
        async def after_async_agent_hook(state: AgentState) -> None:
            nonlocal hook_calls
            hook_calls += 1

            person = state.response.structured_output
            assert person.name.lower() == "stefan"
            assert len(state.response.messages) == 2

        async with Agent(
            model=(await self.model()),
            system_prompt="Your name is stefan",
            service=self.service,
            hooks=[
                before_agent_hook,
                before_async_agent_hook,
                after_agent_hook,
                after_async_agent_hook,
            ],
            output_schema=Person,
        ) as agent:
            result = await agent.invoke(
                [
                    HumanMessage(
                        content="What is your name?",
                    )
                ]
            )

            response = result.messages[-1].content.strip().lower().replace(".", "")
            assert '{"name":"stefan"}' == response
            assert hook_calls == 4

    @pytest.mark.asyncio
    async def test_agent_loop_stop_conditions_token_limit(self):
        pytest.importorskip("langchain_openai")

        async with Agent(
            model=(await self.model()),
            system_prompt="You are a helpful assistant that responds in structured data.",
            service=self.service,
            hooks=[token_limit(5)],
        ) as agent:
            with pytest.raises(
                TokenLimitExceededException, match="Token limit of 5 exceeded"
            ):
                _ = await agent.invoke(
                    [
                        HumanMessage(
                            content="hi, my name is Chris",
                        )
                    ]
                )

    @pytest.mark.asyncio
    async def test_agent_loop_stop_conditions_conversation_limit(self):
        pytest.importorskip("langchain_openai")

        async with Agent(
            model=(await self.model()),
            system_prompt="You are a helpful assistant that responds in structured data.",
            service=self.service,
            hooks=[step_limit(2)],
        ) as agent:
            _ = await agent.invoke(
                [
                    HumanMessage(
                        content="hi, my name is Chris",
                    )
                ]
            )

            with pytest.raises(
                StepsLimitExceededException, match="Steps limit of 2 exceeded"
            ):
                _ = await agent.invoke(
                    [
                        HumanMessage(
                            content="What is my name?",
                        )
                    ]
                )

    @pytest.mark.asyncio
    async def test_agent_loop_stop_conditions_timeout(self):
        pytest.importorskip("langchain_openai")

        async with Agent(
            model=(await self.model()),
            system_prompt="You are a helpful assistant that responds in structured data.",
            service=self.service,
            hooks=[timeout_limit(0.5)],
        ) as agent:
            _ = await agent.invoke(
                [
                    HumanMessage(
                        content="hi, my name is Chris",
                    )
                ]
            )

            time.sleep(1)  # wait to exceed timeout

            with pytest.raises(
                TimeoutExceededException, match="Timed out after 0.5 seconds."
            ):
                _ = await agent.invoke(
                    [
                        HumanMessage(
                            content="What is my name?",
                        )
                    ]
                )

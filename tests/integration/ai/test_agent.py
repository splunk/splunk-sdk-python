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
from pydantic import BaseModel, Field

from splunklib.ai import Agent
from splunklib.ai.messages import HumanMessage, SubagentMessage
from tests.ai_testlib import AITestCase

OPENAI_BASE_URL = "http://localhost:11434/v1"
OPENAI_API_KEY = "ollama"


class TestAgent(AITestCase):
    @pytest.mark.asyncio
    async def test_agent_with_openai_round_trip(self):
        pytest.importorskip("langchain_openai")

        async with Agent(
            model=(await self.model()),
            system_prompt="Your name is stefan",
            service=self.service,
        ) as agent:
            result = await agent.invoke(
                [
                    HumanMessage(
                        content="What is your name? Answer in one word",
                    )
                ]
            )

            response = result.messages[-1].content.strip().lower().replace(".", "")
            assert result.structured_output is None, (
                "The structured output should not be populated"
            )
            assert "stefan" in response

    @pytest.mark.asyncio
    async def test_agent_use_without_async_with(self):
        pytest.importorskip("langchain_openai")

        agent = Agent(
            model=(await self.model()),
            system_prompt="Your name is stefan",
            service=self.service,
        )

        with pytest.raises(Exception, match="Agent must be used inside 'async with'"):
            _ = await agent.invoke(
                [
                    HumanMessage(
                        content="What is your name? Answer in one word",
                    )
                ]
            )

    @pytest.mark.asyncio
    async def test_agent_use_outside_async_with(self):
        pytest.importorskip("langchain_openai")

        agent = Agent(
            model=(await self.model()),
            system_prompt="Your name is stefan",
            service=self.service,
        )

        async with agent:
            pass

        with pytest.raises(Exception, match="Agent must be used inside 'async with'"):
            _ = await agent.invoke(
                [
                    HumanMessage(
                        content="What is your name? Answer in one word",
                    )
                ]
            )

    @pytest.mark.asyncio
    async def test_agent_multiple_async_with(self):
        pytest.importorskip("langchain_openai")

        agent = Agent(
            model=(await self.model()),
            system_prompt="Your name is stefan",
            service=self.service,
        )

        async with agent:
            with pytest.raises(
                Exception, match="Agent is already in `async with` context"
            ):
                async with agent:
                    pass

    @pytest.mark.asyncio
    async def test_agent_with_structured_output(self):
        pytest.importorskip("langchain_openai")

        class Person(BaseModel):
            name: str = Field(description="The person's full name", min_length=1)
            age: int = Field(description="The person's age in years", ge=0, le=150)

        async with Agent(
            model=(await self.model()),
            system_prompt="Respond with structured data",
            output_schema=Person,
            service=self.service,
        ) as agent:
            result = await agent.invoke(
                [
                    HumanMessage(
                        content="fill in the details for Person model",
                    )
                ]
            )

            response = result.structured_output

            last_message = result.messages[-1].content

            assert type(response) == Person, "Response is not of type Person"
            assert response.name != "", "Name field is empty"
            assert 0 <= response.age <= 150, "Age field is out of bounds"

            # check if the last message contains the response in natural language
            assert response.name in last_message, "Name field not found in the message"
            assert str(response.age) in last_message, (
                "Age field not found in the message"
            )

    @pytest.mark.asyncio
    async def test_agent_remembers_state(self):
        pytest.importorskip("langchain_openai")

        async with Agent(
            model=(await self.model()),
            system_prompt="You are a helpful assistant that responds in structured data.",
            service=self.service,
        ) as agent:
            _ = await agent.invoke(
                [
                    HumanMessage(
                        content="hi, my name is Chris",
                    )
                ]
            )

            result = await agent.invoke(
                [
                    HumanMessage(
                        content="What is my name?",
                    )
                ]
            )

            response = result.messages[-1].content

            assert "Chris" in response, "Agent did not remember the name"

    @pytest.mark.asyncio
    async def test_agent_uses_subagent(self):
        pytest.importorskip("langchain_openai")

        class NicknameGeneratorInput(BaseModel):
            name: str = Field(description="The person's full name", min_length=1)

        async with (
            Agent(
                model=(await self.model()),
                system_prompt=(
                    "You are a helpful assistant that generates nicknames"
                    "If prompted for nickname you MUST append '-zilla' to provided name to create nickname."
                    "Remember the dash and lowercase zilla. Example: Stefan -> Stefan-zilla"
                ),
                service=self.service,
                name="NicknameGeneratorAgent",
                description="Generates nicknames for people. Pass a name and get a nickname",
                input_schema=NicknameGeneratorInput,
            ) as subagent,
            Agent(
                model=(await self.model()),
                system_prompt="You are a supervisor agent that MUST use other agents",
                agents=[subagent],
                service=self.service,
            ) as supervisor,
        ):
            result = await supervisor.invoke(
                [
                    HumanMessage(
                        content="hi, my name is Chris. Generate a nickname for me",
                    )
                ]
            )

            response = result.messages[-1].content

            subagent_message = next(
                filter(lambda m: m.role == "subagent", result.messages), None
            )
            assert isinstance(subagent_message, SubagentMessage), (
                "Invalid subagent message"
            )
            assert subagent_message, "No subagent message found in response"
            assert "Chris-zilla" in response, "Agent did generate valid nickname"

    @pytest.mark.asyncio
    async def test_subagent_without_input_schema(self):
        pytest.importorskip("langchain_openai")

        async with (
            Agent(
                model=(await self.model()),
                system_prompt=(
                    "You are a helpful assistant that generates nicknames"
                    "If prompted for nickname you MUST append '-zilla' to provided name to create nickname."
                    "Remember the dash and lowercase zilla. Example: Stefan -> Stefan-zilla"
                ),
                service=self.service,
                name="NicknameGeneratorAgent",
                description="Generates nicknames for people. Pass a name and get a nickname",
            ) as subagent,
            Agent(
                model=(await self.model()),
                system_prompt="You are a supervisor agent that MUST use other agents",
                agents=[subagent],
                service=self.service,
            ) as supervisor,
        ):
            result = await supervisor.invoke(
                [
                    HumanMessage(
                        content="hi, my name is Chris. Generate a nickname for me",
                    )
                ]
            )

            response = result.messages[-1].content
            assert "Chris-zilla" in response, "Agent did generate valid nickname"

    @pytest.mark.asyncio
    async def test_subagent_without_input_schema_with_output_schema(self) -> None:
        pytest.importorskip("langchain_openai")

        # Regrssion test - make sure that agents work without output schema
        # when input schema is not provided.

        class Person(BaseModel):
            nickname: str = Field(description="The person's nickname", min_length=1)

        async with (
            Agent(
                model=(await self.model()),
                system_prompt=(
                    "You are a helpful assistant that generates nicknames"
                    "If prompted for nickname you MUST append '-zilla' to provided name to create nickname."
                    "Remember the dash and lowercase zilla. Example: Stefan -> Stefan-zilla"
                ),
                service=self.service,
                name="NicknameGeneratorAgent",
                description="Generates nicknames for people. Pass a name and get a nickname",
                output_schema=Person,
            ) as subagent,
            Agent(
                model=(await self.model()),
                system_prompt="You are a supervisor agent that MUST use other agents",
                agents=[subagent],
                service=self.service,
            ) as supervisor,
        ):
            result = await supervisor.invoke(
                [
                    HumanMessage(
                        content="hi, my name is Chris. Generate a nickname for me",
                    )
                ]
            )

            response = result.messages[-1].content
            assert "Chris-zilla" in response, "Agent did generate valid nickname"

    @pytest.mark.asyncio
    async def test_agent_understands_other_agents(self):
        pytest.importorskip("langchain_openai")

        class SubagentInput(BaseModel):
            person_name: str = Field(description="The person's full name", min_length=1)
            age: int = Field(description="The person's age in years", ge=0, le=150)
            hobbies: list[str] = Field(
                description="List of person's hobbies",
                min_length=1,
                max_length=5,
            )

        class SubagentOutput(BaseModel):
            person_description: str = Field(
                description="A short description of the person", min_length=10
            )

        async with Agent(
            model=(await self.model()),
            system_prompt="You are a helpful assistant that describes a person based on their details.",
            service=self.service,
            name="PersonDescriberAgent",
            description="Describes a person based on their details.",
            input_schema=SubagentInput,
            output_schema=SubagentOutput,
        ) as subagent:

            class SupervisorOutput(BaseModel):
                team_name: str = Field(description="The name of the team", min_length=1)
                member_descriptions: list[SubagentOutput] = Field(
                    description="List of member descriptions",
                    min_length=1,
                    max_length=10,
                )

            async with Agent(
                model=(await self.model()),
                agents=[subagent],
                system_prompt=(
                    "You are a supervisor agent that manages other agents to describe multiple people."
                    "Make sure you return the structured output data that matches the response format provided to you."
                    "If you're unable to get the data from the sub-agent, return an appropriate message indicating the failure."
                ),
                output_schema=SupervisorOutput,
                service=self.service,
            ) as supervisor_agent:
                result = await supervisor_agent.invoke(
                    [
                        HumanMessage(
                            content="give me descriptions for three people. Use describer agent to generate descriptions. Provide it with all the data it needs.",
                        )
                    ]
                )

                response = result.structured_output
                assert type(response) == SupervisorOutput, (
                    "Response is not of type Team"
                )
                assert len(response.member_descriptions) == 3, (
                    "Team does not have 3 members"
                )

    @pytest.mark.asyncio
    async def test_duplicated_subagent_name(self) -> None:
        pytest.importorskip("langchain_openai")

        async with (
            Agent(
                model=(await self.model()),
                system_prompt="",
                service=self.service,
                name="subagent_name",
            ) as subagent1,
            Agent(
                model=(await self.model()),
                system_prompt="",
                service=self.service,
                name="subagent_name",
            ) as subagent2,
            Agent(
                model=(await self.model()),
                system_prompt="",
                service=self.service,
                name="",
            ) as subagent1_empty_name,
            Agent(
                model=(await self.model()),
                system_prompt="",
                service=self.service,
                name="",
            ) as subagent2_empty_name,
        ):
            with pytest.raises(
                AssertionError, match="Subagents share the same name: subagent_name"
            ):
                async with Agent(
                    model=(await self.model()),
                    system_prompt="",
                    service=self.service,
                    agents=[subagent1, subagent2],
                ):
                    pass

            # Also make sure, that because of this check we have, we will not
            # mistakenly accept same subagent (since they also share the same name).
            with pytest.raises(
                AssertionError, match="Subagents share the same name: subagent_name"
            ):
                async with Agent(
                    model=(await self.model()),
                    system_prompt="",
                    service=self.service,
                    agents=[subagent1, subagent1],
                ):
                    pass

            # Make sure that the subagent is validated before the name uniqueness check.
            with pytest.raises(
                AssertionError,
                match="Agent must have a name to be used by other Agents",
            ):
                async with Agent(
                    model=(await self.model()),
                    system_prompt="",
                    service=self.service,
                    agents=[subagent1_empty_name, subagent2_empty_name],
                ):
                    pass

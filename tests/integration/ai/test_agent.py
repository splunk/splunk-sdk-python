#
# Copyright © 2011-2025 Splunk, Inc.
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

from splunklib.ai import Agent, Message, OllamaModel
from pydantic import BaseModel, Field


def test_agent_with_ollama_round_trip():
    # Skip if the langchain_ollama package is not installed
    pytest.importorskip("langchain_ollama")

    model = OllamaModel(model="llama3.2:3b")

    agent = Agent(model=model, system_prompt="Your name is stefan")

    result = agent.invoke(
        [
            Message(
                role="user",
                content="What is your name? Answer in one word",
            )
        ]
    )

    response = result.messages[-1].content.strip().lower().replace(".", "")
    assert result.structured_output is None, (
        "The structured output should not be populated"
    )
    assert "stefan" in response


def test_agent_with_structured_output():
    pytest.importorskip("langchain_ollama")
    model = OllamaModel(model="llama3.2:3b")

    class Person(BaseModel):
        name: str = Field(description="The person's full name", min_length=1)
        age: int = Field(description="The person's age in years", ge=0, le=150)

    agent = Agent(
        model=model,
        system_prompt="Respond with structured data",
        output_schema=Person,
    )

    result = agent.invoke(
        [
            Message(
                role="user",
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
    assert str(response.age) in last_message, "Age field not found in the message"


def test_agent_remembers_state():
    pytest.importorskip("langchain_ollama")
    model = OllamaModel(model="llama3.2:3b")

    agent = Agent(
        model=model,
        system_prompt="You are a helpful assistant that responds in structured data.",
    )

    _ = agent.invoke(
        [
            Message(
                role="user",
                content="hi, my name is Chris",
            )
        ]
    )

    result = agent.invoke(
        [
            Message(
                role="user",
                content="What is my name?",
            )
        ]
    )

    response = result.messages[-1].content

    assert "Chris" in response, "Agent did not remember the name"


def test_agent_understands_other_agents():
    pytest.importorskip("langchain_ollama")
    model = OllamaModel(
        model="devstral-small-2:24b",
        base_url="http://localhost:11435",
    )

    class SubagentInput(BaseModel):
        person_name: str = Field(description="The person's full name", min_length=1)
        age: int = Field(description="The person's age in years", ge=0, le=150)
        hobbies: list[str] = Field(
            description="List of person's hobbies", min_items=1, max_items=5
        )

    class SubagentOutput(BaseModel):
        person_description: str = Field(
            description="A short description of the person", min_length=10
        )

    subagent = Agent(
        model=model,
        system_prompt="You are a helpful assistant that describes a person based on their details.",
        name="PersonDescriberAgent",
        description="Describes a person based on their details.",
        input_schema=SubagentInput,
        output_schema=SubagentOutput,
    )

    class SupervisorOutput(BaseModel):
        team_name: str = Field(description="The name of the team", min_length=1)
        member_descriptions: list[SubagentOutput] = Field(
            description="List of member descriptions", min_items=1, max_items=10
        )

    supervisor_agent = Agent(
        model=model,
        agents=[subagent],
        system_prompt="""You are a supervisor agent that manages other agents to describe multiple people.
        Make sure you return the structured output data that matches the response format provided to you.
        If you're unable to get the data from the sub-agent, return an appropriate message indicating the failure.
        """,
        output_schema=SupervisorOutput,
    )

    result = supervisor_agent.invoke(
        [
            Message(
                role="user",
                content="give me descriptions for three people. Use describer agent to generate descriptions. Provide it with all the data it needs.",
            )
        ]
    )

    response = result.structured_output
    assert type(response) == SupervisorOutput, "Response is not of type Team"
    assert len(response.member_descriptions) == 3, "Team does not have 3 members"

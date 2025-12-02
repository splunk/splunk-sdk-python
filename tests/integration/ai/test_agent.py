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

from splunklib.ai import Agent, Message, OllamaModel, tool
from threading import Event


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

    response = result[-1].content.strip().lower().replace(".", "")
    assert "stefan" in response


def test_agent_with_tool_usage():
    # Skip if the langchain_ollama package is not installed
    pytest.importorskip("langchain_ollama")

    adder_event = Event()
    multiplier_event = Event()

    @tool
    def adder_tool(a: int, b: int) -> int:
        "this tool adds two numbers together"
        adder_event.set()

        return a + b

    @tool
    def multiplier_tool(a: int, b: int) -> int:
        "this tool multiplies two numbers together"
        multiplier_event.set()

        return a * b

    model = OllamaModel(model="llama3.2:3b")

    agent = Agent(
        model=model,
        system_prompt="You can use the available tools to perform math.",
        tools=[adder_tool, multiplier_tool],
    )

    result = agent.invoke(
        [
            Message(
                role="user",
                content="What is 7 + 5? Then multiply the result with 5. Give me the final answer",
            )
        ]
    )
    response = result[-1].content.strip()

    assert "60" in response, "Agent returned wrong response"
    assert adder_event.is_set(), "The adder tool was not used"
    assert multiplier_event.is_set(), "The multiplier tool was not used"

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

from splunklib.ai import Agent, AnthropicModel
from splunklib.ai.messages import HumanMessage
from tests.ai_testlib import AITestCase, ai_snapshot_test

# Ollama exposes an Anthropic-compatible API -
# point AnthropicModel at the Ollama base URL
# to test locally without real Anthropic credentials.
ANTHROPIC_BASE_URL = "http://localhost:11434"
ANTHROPIC_API_KEY = "ollama"
ANTHROPIC_MODEL = "llama3.2:3b"


class TestAnthropicAgent(AITestCase):
    @pytest.mark.asyncio
    @pytest.mark.skip("Manual Test")
    @ai_snapshot_test()
    async def test_agent_with_anthropic_round_trip(self):
        """Basic round-trip using AnthropicModel pointed at local Ollama."""
        model = AnthropicModel(
            model=ANTHROPIC_MODEL,
            api_key=ANTHROPIC_API_KEY,
            base_url=ANTHROPIC_BASE_URL,
            temperature=0.0,
        )

        async with Agent(
            model=model,
            system_prompt="Your name is stefan",
            service=self.service,
        ) as agent:
            result = await agent.invoke(
                [HumanMessage(content="What is your name? Answer in one word")]
            )

            response = (
                self.parse_content(result.final_message)
                .strip()
                .lower()
                .replace(".", "")
            )
            assert result.structured_output is None
            assert "stefan" in response

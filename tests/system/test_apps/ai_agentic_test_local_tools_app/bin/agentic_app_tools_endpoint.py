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
import sys

sys.path.insert(0, "/splunklib-deps")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "lib"))


from typing import override

from splunklib.ai.agent import Agent
from splunklib.ai.messages import (
    AIMessage,
    ContentBlock,
    HumanMessage,
    SubagentTextResult,
    TextBlock,
)
from splunklib.ai.tool_settings import ToolSettings
from tests.cre_testlib import CRETestHandler

OPENAI_BASE_URL = "http://host.docker.internal:11434/v1"
OPENAI_API_KEY = "ollama"

# BUG: For some reason the CRE process is started with a overridden trust store path, that
# does not exist on the filesystem. As a workaround in such case if it does not exist,
# remove the env, this causes the default CAs to be used instead.
CA_TRUST_STORE = "/opt/splunk/openssl/cert.pem"
if os.environ.get("SSL_CERT_FILE") == CA_TRUST_STORE and not os.path.exists(
    CA_TRUST_STORE
):
    os.environ["SSL_CERT_FILE"] = ""


class WeatherHandler(CRETestHandler):
    @override
    async def run(self) -> None:
        async with Agent(
            model=(await self.model()),
            system_prompt="You must use the available tools to perform requested operations",
            service=self.service,
            tool_settings=ToolSettings(local=True, remote=None),
        ) as agent:
            result = await agent.invoke(
                [
                    HumanMessage(
                        content=(
                            "What is the weather like today in Krakow? Use the provided tools to check the temperature. "
                            + "Return a short response, containing the tool response."
                        ),
                    )
                ]
            )

            response = result.final_message.content
            self.response.write(response)


class AgentNameHandler(CRETestHandler):
    @override
    async def run(self) -> None:
        async with Agent(
            model=(await self.model()),
            system_prompt="Your name is Stefan",
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
            self.response.write(response)

    def _parse_content_block(self, block: str | ContentBlock) -> str | None:
        match block:
            case TextBlock():
                return block.text
            case str():
                return block
            case _:
                return None

    def parse_content(self, message: AIMessage | SubagentTextResult) -> str:
        """Parses the content from AIMessage and builds a single string our of it"""
        if isinstance(message.content, str):
            return message.content

        return " ".join(
            parsed_block
            for block in message.content
            if (parsed_block := self._parse_content_block(block))
        )

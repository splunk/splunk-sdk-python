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

from pydantic import BaseModel, Field

from splunklib.ai.agent import Agent
from splunklib.ai.messages import HumanMessage
from splunklib.ai.tool_filtering import ToolFilters
from tests.cre_testlib import CRETestHandler

# BUG: For some reason the CRE process is started with a overridden trust store path, that
# does not exist on the filesystem. As a workaround in such case if it does not exist,
# remove the env, this causes the default CAs to be used instead.
CA_TRUST_STORE = "/opt/splunk/openssl/cert.pem"
if os.environ.get("SSL_CERT_FILE") == CA_TRUST_STORE and not os.path.exists(
    CA_TRUST_STORE
):
    os.environ["SSL_CERT_FILE"] = ""

# This app uses the splunk_get_indexes remote tool (from Splunk MCP Server App).
# Requires that the MCP Server App is installed.


class IndexesHandler(CRETestHandler):
    @override
    async def run(self) -> None:
        class Output(BaseModel):
            indexes: list[str] = Field(description="list of index names")

        async with Agent(
            model=(await self.model()),
            system_prompt="You are a helpful Splunk assistant",
            use_mcp_tools=True,
            service=self.service,
            tool_filters=ToolFilters(
                allowed_names=["splunk_get_indexes"], allowed_tags=[]
            ),
            output_schema=Output,
        ) as agent:
            assert len(agent.tools) == 1, "Invalid tool count"
            assert (
                len([tool for tool in agent.tools if tool.name == "splunk_get_indexes"])
                == 1
            ), "splunk_get_indexes not present"

            result = await agent.invoke(
                [
                    HumanMessage(
                        content="List all indexes available on the splunk instance.",
                    )
                ]
            )

            self.response.write(result.structured_output.model_dump_json())

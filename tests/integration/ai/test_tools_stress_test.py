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

import asyncio
import os
from unittest.mock import patch

import pytest

from splunklib.ai import Agent
from splunklib.ai.tool_settings import ToolSettings
from tests.ai_testlib import AITestCase


# Test that makes sure our logic in the tool registry and tool calling
# is safe for concurrent use.
class TestToolStressTest(AITestCase):
    @patch(
        "splunklib.ai.agent._testing_local_tools_path",
        os.path.join(os.path.dirname(__file__), "testdata", "counter.py"),
    )
    @patch("splunklib.ai.agent._testing_app_id", "app_id")
    @pytest.mark.asyncio
    async def test_tool_call_stress_test(self) -> None:
        async with Agent(
            model=(await self.model()),
            system_prompt="",
            service=self.service,
            tool_settings=ToolSettings(local=True, remote=None),
        ) as agent:
            assert len(agent.tools) == 1
            tool = agent.tools[0]
            assert tool.name == "counter"

            async def call_tool() -> int:
                result = await tool.func()
                assert result.structured_content is not None
                result = result.structured_content["result"]
                assert isinstance(result, int)
                return result

            tasks: list[asyncio.Task[int]] = []
            for _ in range(5000):
                task = asyncio.create_task(call_tool())
                tasks.append(task)

                # yield control to the runtime, for more random ordering
                await asyncio.sleep(0)

            # Make sure we have all the results. In case of an race in the tool registry
            # or mcp client logic, this will hopefully fail.
            assert (await asyncio.gather(*tasks)) == list(range(1, 5001))

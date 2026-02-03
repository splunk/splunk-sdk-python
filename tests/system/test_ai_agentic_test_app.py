#!/usr/bin/env python
#
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

from tests.ai_testlib import AITestCase


class TestAgenticApp(AITestCase):
    def test_agetic_app(self) -> None:
        pytest.importorskip("langchain_openai")
        self.skip_splunk_10_2()

        resp = self.service.post(
            "agentic_app/agent-name",
            body=self.test_llm_settings.model_dump_json(),
        )
        assert resp.status == 200
        assert "stefan" in str(resp.body)

    def test_agentic_app_with_tools_weather(self) -> None:
        pytest.importorskip("langchain_openai")
        self.skip_splunk_10_2()

        resp = self.service.post(
            "agentic_app_with_local_tools/weather",
            body=self.test_llm_settings.model_dump_json(),
        )
        assert resp.status == 200
        assert "31.5" in str(resp.body)

    def test_agentic_app_with_tools_agent_name(self) -> None:
        pytest.importorskip("langchain_openai")
        self.skip_splunk_10_2()

        resp = self.service.post(
            "agentic_app_with_local_tools/agent-name",
            body=self.test_llm_settings.model_dump_json(),
        )
        assert resp.status == 200
        assert "stefan" in str(resp.body)

    # TODO: Would be nice to test remote tool execution, such test would need to install the
    # MCP Server App and define a custom tool (tools.conf). For now we only test remote tools ececution
    # with a mock mcp server, outside of Splunk environment, see ../integration/ai/test_agent_mcp_tools.py.

    def skip_splunk_10_2(self) -> None:
        if self.service.splunk_version[0] < 10 or self.service.splunk_version[1] < 2:
            self.skipTest("Python 3.13 not available on splunk < 10.2")

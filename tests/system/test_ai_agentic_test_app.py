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

from splunklib.binding import HTTPError
from tests.ai_testlib import AITestCase


class TestAgenticApp(AITestCase):
    def test_agentic_app(self) -> None:
        pytest.importorskip("langchain_openai")
        self.requires_splunk_10_2()

        resp = self.service.post(
            "agentic_app/agent-name",
            body=self.test_llm_settings.model_dump_json(),
        )
        assert resp.status == 200
        assert "stefan" in str(resp.body)  # pyright: ignore[reportUnknownArgumentType]

    def test_agentic_app_with_tools_weather(self) -> None:
        pytest.importorskip("langchain_openai")
        self.requires_splunk_10_2()

        resp = self.service.post(
            "agentic_app_with_local_tools/weather",
            body=self.test_llm_settings.model_dump_json(),
        )
        assert resp.status == 200
        assert "31.5" in str(resp.body)  # pyright: ignore[reportUnknownArgumentType]

    def test_agentic_app_with_tools_agent_name(self) -> None:
        pytest.importorskip("langchain_openai")
        self.requires_splunk_10_2()

        resp = self.service.post(
            "agentic_app_with_local_tools/agent-name",
            body=self.test_llm_settings.model_dump_json(),
        )
        assert resp.status == 200
        assert "stefan" in str(resp.body)  # pyright: ignore[reportUnknownArgumentType]

    # To execute this test locally, download the Splunk MCP Server App tarball from
    # https://splunkbase.splunk.com/app/7931 and place it in a file named
    # splunk-mcp-server.tgz at the root of this repo (i.e. ../../splunk-mcp-server.tgz).
    #
    # Note: that the downloaded file could have a: .spl, .tar, .tar.gz or .tgz extension,
    # if it is not .tgz, then you must change it to .tgz.
    #
    # Our CI does this automatically.
    def test_agentic_app_with_remote_tools(self) -> None:
        pytest.importorskip("langchain_openai")
        self.requires_splunk_10_2()

        INDEX_NAME = "needle-index"

        # Delete the index if already exists.
        for index in self.service.indexes:  # pyright: ignore[reportUnknownVariableType]
            if index.name == INDEX_NAME:
                index.delete()

        # Skip test in case the instance does not have a /splunk-mcp-server.tgz file.
        # We do so, not to require app download for local development of the SDK.
        # Note that: our CI always has this file available.
        #
        # We check that through a separate endpoint call, since we want to have tests
        # that don't assume that our CI splunk instance is a docker container.
        try:
            resp = self.service.get("agentic_app/has_mcp_app_file")
            assert resp.status == 200
        except HTTPError as e:
            if e.status == 404:
                pytest.skip("Splunk MCP Server App file not found on Splunk instance")
            raise

        # AITestCase already removes the Splunk MCP Server App in case it is already
        # installed, so here we will always end up installing it, thus having a fresh
        # version of the app.

        # Install the Splunk MCP Server App.
        app = self.service.apps.create(name="/splunk-mcp-server.tgz", filename=True)  # pyright: ignore[reportUnknownVariableType]

        index = self.service.indexes.create(name=INDEX_NAME)  # pyright: ignore[reportUnknownVariableType]

        resp = self.service.post(
            "agentic_app/indexes",
            body=self.test_llm_settings.model_dump_json(),
        )

        assert resp.status == 200
        assert INDEX_NAME in str(resp.body)  # pyright: ignore[reportUnknownArgumentType]

        index.delete()
        app.delete()
        self.restart_splunk()  # app removal requires a restart

    def requires_splunk_10_2(self) -> None:
        if self.service.splunk_version[0] < 10 or self.service.splunk_version[1] < 2:
            pytest.skip("Python 3.13 not available on splunk < 10.2")

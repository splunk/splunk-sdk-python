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
from typing import override
from uuid import uuid4

sys.path.insert(0, "/splunklib-deps")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "lib"))


from splunklib.ai.agent import (
    _get_splunk_username,  # pyright: ignore[reportPrivateUsage]
)
from splunklib.ai.tools import (
    _list_all_tools,  # pyright: ignore[reportPrivateUsage]
    connect_remote_mcp,
)
from tests.cre_testlib import CRETestHandler

# BUG: For some reason the CRE process is started with a overridden trust store path, that
# does not exist on the filesystem. As a workaround in such case if it does not exist,
# remove the env, this causes the default CAs to be used instead.
CA_TRUST_STORE = "/opt/splunk/openssl/cert.pem"
if os.environ.get("SSL_CERT_FILE") == CA_TRUST_STORE and not os.path.exists(
    CA_TRUST_STORE
):
    os.environ["SSL_CERT_FILE"] = ""

# This handler connects directly to the Splunk MCP Server App and logs the raw
# MCP tool list response, verifying that tool metadata includes tags.


class ToolTagsHandler(CRETestHandler):
    @override
    async def run(self) -> None:
        import asyncio

        splunk_username = await asyncio.to_thread(
            lambda: _get_splunk_username(self.service)
        )

        async with connect_remote_mcp(
            service=self.service,
            app_id="ai_agentic_test_app",
            trace_id=str(uuid4()),
            splunk_username=splunk_username,
        ) as session:
            assert session is not None, "MCP Server App not available"
            raw_tools = await _list_all_tools(session)
        self.response.write(f"[{','.join(rt.model_dump_json() for rt in raw_tools)}]")

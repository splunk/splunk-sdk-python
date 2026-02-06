#!/usr/bin/env python
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

import json
import os
import sys
import unittest
from contextlib import asynccontextmanager

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.types import TextContent

from tests import testlib


class TestRegistryTestCase(testlib.SDKTestCase):
    def get_splunk_token(self) -> str:
        res = self.service.post(
            path_segment="authorization/tokens",
            name="admin",
            audience="test",
            type="ephemeral",
            output_mode="json",
        )
        token = json.loads(str(res.body))["entry"][0]["content"]["token"]
        return token

    @property
    def splunk_url(self) -> str:
        return f"{self.service.scheme}://{self.service.host}:{self.service.port}"

    @asynccontextmanager
    async def connect(self, name: str):
        server_params = StdioServerParameters(
            command=sys.executable,
            args=[os.path.join(os.path.dirname(__file__), "testdata", name)],
        )
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                yield session


class TestToolContextRegistry(TestRegistryTestCase):
    async def test_startup_time(self):
        async with self.connect("tool_context.py") as session:
            res = await session.call_tool(
                "startup_time",
                arguments={},
                meta={
                    "splunk": {
                        "management_token": self.get_splunk_token(),
                        "management_url": self.splunk_url,
                    }
                },
            )
            self.assertEqual(res.isError, False)
            self.assertEqual(res.content, [])
            self.assertEqual(
                res.structuredContent, {"result": f"{self.service.info.startup_time}"}
            )

    async def test_startup_time_and_str(self):
        async with self.connect("tool_context.py") as session:
            res = await session.call_tool(
                "startup_time_and_str",
                arguments={"val": "some value"},
                meta={
                    "splunk": {
                        "management_token": self.get_splunk_token(),
                        "management_url": self.splunk_url,
                    }
                },
            )
            self.assertEqual(res.isError, False)
            self.assertEqual(res.content, [])
            self.assertEqual(
                res.structuredContent,
                {"result": f"some value {self.service.info.startup_time}"},
            )

    async def test_missing_meta_params(self):
        async with self.connect("tool_context.py") as session:
            res = await session.call_tool(
                "startup_time",
                arguments={},
            )
            self.assertEqual(res.isError, True)
            self.assertEqual(
                res.content,
                [
                    TextContent(
                        type="text",
                        text="Invalid tool invocation, missing management_url and/or management_token",
                    )
                ],
            )
            self.assertEqual(res.structuredContent, None)


class TestAsyncToolRegistry(TestRegistryTestCase):
    async def test_tool_hello(self):
        async with self.connect("async_tool.py") as session:
            res = await session.call_tool(
                "hello",
                arguments={"name": "Stefan"},
                meta={
                    "splunk": {
                        "management_token": self.get_splunk_token(),
                        "management_url": self.splunk_url,
                    }
                },
            )
            self.assertEqual(res.isError, False)
            self.assertEqual(res.content, [])
            self.assertEqual(res.structuredContent, {"result": "Hello Stefan"})


if __name__ == "__main__":
    import unittest

    unittest.main()

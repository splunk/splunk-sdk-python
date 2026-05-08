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

import json
import os
import sys
import unittest
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import override

from mcp import ClientSession, LoggingLevel, StdioServerParameters
from mcp.client.session import LoggingFnT
from mcp.client.stdio import stdio_client
from mcp.types import LoggingMessageNotificationParams, TextContent

from splunklib.ai.registry import LogData
from splunklib.ai.serialized_service import SerializedService
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
    def serialized_service(self) -> SerializedService:
        return SerializedService.from_service(self.service)

    @asynccontextmanager
    async def connect(self, name: str, logger: LoggingFnT | None = None):
        server_params = StdioServerParameters(
            command=sys.executable,
            args=[os.path.join(os.path.dirname(__file__), "testdata", name)],
        )
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write, logging_callback=logger) as session:
                await session.initialize()
                yield session


class TestToolContextRegistry(TestRegistryTestCase):
    async def test_startup_time(self):
        async with self.connect("tool_context.py") as session:
            res = await session.call_tool(
                "startup_time",
                arguments={},
                meta={"splunk": {"service": self.serialized_service.model_dump()}},
            )
            self.assertEqual(res.isError, False)
            self.assertEqual(res.content, [])
            self.assertEqual(res.structuredContent, {"result": f"{self.service.info.startup_time}"})

    async def test_startup_time_and_str(self):
        async with self.connect("tool_context.py") as session:
            res = await session.call_tool(
                "startup_time_and_str",
                arguments={"val": "some value"},
                meta={"splunk": {"service": self.serialized_service.model_dump()}},
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
                        text="Invalid tool invocation, missing serialized service details",
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
                meta={"splunk": {"service": self.serialized_service.model_dump()}},
            )
            self.assertEqual(res.isError, False)
            self.assertEqual(res.content, [])
            self.assertEqual(res.structuredContent, {"result": "Hello Stefan"})


class TestTemperatureAsDictRegistry(TestRegistryTestCase):
    async def test_tool_temperature_returning_dict(self):
        async with self.connect("temperature_as_dict.py") as session:
            res = await session.call_tool(
                "temperature",
                arguments={"city": "Krakow"},
                meta={"splunk": {"service": self.serialized_service.model_dump()}},
            )
            self.assertEqual(res.isError, False)
            self.assertEqual(res.content, [])
            self.assertEqual(res.structuredContent, {"city": "Krakow", "temperature": 22})


@dataclass
class Log:
    level: LoggingLevel
    msg: str


class FakeLoggingHandler(LoggingFnT):
    def __init__(self) -> None:
        self._logs: list[Log] = []

    @property
    def logs(self) -> list[Log]:
        # Log might not be ordered, see registry.py.
        # Such that we never depend on the ordering, we sort it.
        return sorted(
            self._logs,
            key=lambda log: (log.level, log.msg),
        )

    @override
    async def __call__(
        self,
        params: LoggingMessageNotificationParams,
    ) -> None:
        record = LogData(**params.data)
        self._logs.append(Log(params.level, record.message))


class TestLoggingToolRegistry(TestRegistryTestCase):
    async def test_logs(self) -> None:
        handler = FakeLoggingHandler()

        async with self.connect(
            "logger.py",
            logger=handler,
        ) as session:
            _ = await session.set_logging_level("debug")

            res = await session.call_tool(
                "hello",
                arguments={"name": "Stefan"},
                meta={"splunk": {"service": self.serialized_service.model_dump()}},
            )

            assert not res.isError

            assert Log("debug", "debug log") in handler.logs
            assert Log("info", "info log") in handler.logs
            assert Log("warning", "warning log") in handler.logs
            assert Log("error", "error log") in handler.logs
            assert Log("critical", "critical log") in handler.logs

            assert Log("debug", "debug-1 log") in handler.logs
            assert Log("debug", "info-1 log") in handler.logs
            assert Log("info", "warn-1 log") in handler.logs
            assert Log("warning", "error-1 log") in handler.logs
            assert Log("error", "critical-1 log") in handler.logs

            assert Log("debug", "notset+1 log") in handler.logs
            assert Log("debug", "debug+1 log") in handler.logs
            assert Log("info", "info+1 log") in handler.logs
            assert Log("warning", "warn+1 log") in handler.logs
            assert Log("error", "error+1 log") in handler.logs
            assert Log("critical", "critical+1 log") in handler.logs

            assert len(handler.logs) == 16

    async def test_set_logging_level(self) -> None:
        handler = FakeLoggingHandler()

        async with self.connect(
            "logger.py",
            logger=handler,
        ) as session:
            _ = await session.set_logging_level("error")

            res = await session.call_tool(
                "hello",
                arguments={"name": "Stefan"},
                meta={"splunk": {"service": self.serialized_service.model_dump()}},
            )

            assert not res.isError

            assert Log("error", "error log") in handler.logs
            assert Log("critical", "critical log") in handler.logs

            assert Log("error", "critical-1 log") in handler.logs

            assert Log("error", "error+1 log") in handler.logs
            assert Log("critical", "critical+1 log") in handler.logs

            assert len(handler.logs) == 5


if __name__ == "__main__":
    import unittest

    unittest.main()

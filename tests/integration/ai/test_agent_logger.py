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

import logging
import os
from dataclasses import dataclass
from typing import override
from unittest.mock import patch

import pytest

from splunklib.ai import Agent
from splunklib.ai.messages import HumanMessage
from splunklib.ai.tool_settings import ToolSettings
from tests.ai_testlib import AITestCase


@dataclass
class Log:
    level: str
    msg: str


class FakeLoggingHandler(logging.Handler):
    _logs: list[Log]

    def __init__(self) -> None:
        super().__init__()
        self._logs = []

    @property
    def logs(self) -> list[Log]:
        # Log might not be ordered, see registry.py.
        # Such that we never depend on the ordering, we sort it.
        return sorted(
            self._logs,
            key=lambda log: (log.level, log.msg),
        )

    @override
    def emit(self, record: logging.LogRecord) -> None:
        self._logs.append(Log(record.levelname, record.msg))
        pass


class TestAgentLogger(AITestCase):
    @patch(
        "splunklib.ai.agent._testing_local_tools_path",
        os.path.join(os.path.dirname(__file__), "testdata", "weather_with_logs.py"),
    )
    @patch("splunklib.ai.agent._testing_app_id", "app_id")
    @pytest.mark.asyncio
    async def test_local_tool_logger(self) -> None:
        pytest.importorskip("langchain_openai")

        handler = FakeLoggingHandler()

        logger = logging.Logger("test logger")
        logger.setLevel(logging.DEBUG)
        logger.addHandler(handler)

        async with Agent(
            model=(await self.model()),
            system_prompt="You must use the available tools to perform requested operations",
            service=self.service,
            logger=logger,
            tool_settings=ToolSettings(local=True, remote=None),
        ) as agent:
            _ = await agent.invoke(
                [
                    HumanMessage(
                        content=(
                            "What is the weather like today in Krakow? Use the provided tools to check the temperature."
                            + "Return a short response, containing the tool response."
                        ),
                    )
                ]
            )

        assert Log("DEBUG", "tool: temperature: debug log") in handler.logs
        assert Log("INFO", "tool: temperature: info log") in handler.logs
        assert Log("WARNING", "tool: temperature: warning log") in handler.logs
        assert Log("ERROR", "tool: temperature: error log") in handler.logs
        assert Log("CRITICAL", "tool: temperature: critical log") in handler.logs
        assert len([h for h in handler.logs if h.msg.startswith("tool:")]) == 5

    @patch(
        "splunklib.ai.agent._testing_local_tools_path",
        os.path.join(os.path.dirname(__file__), "testdata", "weather_with_logs.py"),
    )
    @patch("splunklib.ai.agent._testing_app_id", "app_id")
    @pytest.mark.asyncio
    async def test_local_tool_logger_logging_level(self) -> None:
        pytest.importorskip("langchain_openai")

        handler = FakeLoggingHandler()

        logger = logging.Logger("test logger")
        logger.setLevel(logging.ERROR)
        logger.addHandler(handler)

        async with Agent(
            model=(await self.model()),
            system_prompt="You must use the available tools to perform requested operations",
            service=self.service,
            tool_settings=ToolSettings(local=True, remote=None),
            logger=logger,
        ) as agent:
            _ = await agent.invoke(
                [
                    HumanMessage(
                        content=(
                            "What is the weather like today in Krakow? Use the provided tools to check the temperature."
                            + "Return a short response, containing the tool response."
                        ),
                    )
                ]
            )

        assert Log("ERROR", "tool: temperature: error log") in handler.logs
        assert Log("CRITICAL", "tool: temperature: critical log") in handler.logs
        assert len([h for h in handler.logs if h.msg.startswith("tool:")]) == 2

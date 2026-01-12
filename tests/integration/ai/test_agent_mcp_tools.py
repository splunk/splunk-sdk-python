import os
from unittest.mock import patch

import pytest

from splunklib.ai import Agent, Message, OllamaModel
from splunklib.ai.tools import (
    _get_splunk_token_for_mcp,
    _get_splunk_username,
    locate_tools_path_by_sdk_location,
)
from splunklib.client import connect
from tests import testlib


class TestTools(testlib.SDKTestCase):
    @patch(
        "splunklib.ai.agent._testing_local_tools_path",
        os.path.join(
            os.path.dirname(__file__),
            "testdata",
            "weather.py",
        ),
    )
    async def test_tool_execution_structured_output(self) -> None:
        # Skip if the langchain_ollama package is not installed
        pytest.importorskip("langchain_ollama")

        model = OllamaModel(model="llama3.2:3b")

        async with Agent(
            model=model,
            system_prompt="You must use the available tools to perform requested operations",
            service=self.service,
            use_mcp_tools=True,
        ) as agent:
            result = await agent.invoke(
                [
                    Message(
                        role="user",
                        content="""
                        What is the weather like today in Krakow? Use the provided tools to check the temperature.
                        Return a short response, containing the tool response.
                        """,
                    )
                ]
            )

            response = result.messages[-1].content
            assert response.count("31.5") > 0, "Invalid LLM response"

    @patch(
        "splunklib.ai.agent._testing_local_tools_path",
        os.path.join(
            os.path.dirname(__file__),
            "testdata",
            "tool_context.py",
        ),
    )
    async def test_tool_execution_service_access(self) -> None:
        # Skip if the langchain_ollama package is not installed
        pytest.importorskip("langchain_ollama")

        model = OllamaModel(model="llama3.2:3b")

        async with Agent(
            model=model,
            system_prompt="You must use the available tools to perform requested operations",
            service=self.service,
            use_mcp_tools=True,
        ) as agent:
            result = await agent.invoke(
                [
                    Message(
                        role="user",
                        content="""
                        Using available tools, please check the startup time of the splunk instance.
                        Return a short response, containing the tool response.
                        """,
                    )
                ]
            )

            want_startup_time = f"{self.service.info.startup_time}"

            response = result.messages[-1].content
            assert response.count(want_startup_time) > 0, "Invalid LLM response"


class TestSplunkToken(testlib.SDKTestCase):
    def test_get_splunk_username(self) -> None:
        self.assertTrue(
            self.service.username is not None and self.service.username != ""
        )  # our CI logs-in with username and password.

        self.assertEqual(_get_splunk_username(self.service), self.service.username)

        token = _get_splunk_token_for_mcp(self.service)

        service = connect(
            scheme=self.service.scheme,
            host=self.service.host,
            port=self.service.port,
            token=token,
        )

        self.assertEqual(_get_splunk_username(service), self.service.username)


class TestToolsPathInference:
    def test_infer_tools_path(self) -> None:
        path = os.path.join(os.path.dirname(__file__), "testdata", "app-inference")
        got = locate_tools_path_by_sdk_location(
            splunk_home=path,
            sdk_location_path=os.path.join(
                path, "etc", "apps", "appname", "bin", "lib", "somefile.py"
            ),
        )
        assert got == os.path.join(path, "etc", "apps", "appname", "bin", "tools.py")

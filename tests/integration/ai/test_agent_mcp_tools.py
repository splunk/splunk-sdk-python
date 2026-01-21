import asyncio
import contextlib
import os
import socket
from unittest.mock import patch

import pytest
import uvicorn
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Mount, Route

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
            assert "31.5" in response, "Invalid LLM response"

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
            assert want_startup_time in response, "Invalid LLM response"


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


AUTH_TOKEN = "foobarbaz"


async def tokens_handler(request: Request) -> Response:
    class Content(BaseModel):
        token: str

    class Entry(BaseModel):
        content: Content

    class ResponseBody(BaseModel):
        entry: list[Entry]

    body = ResponseBody(
        entry=[
            Entry(content=Content(token=AUTH_TOKEN)),
        ]
    )

    return JSONResponse(
        content=body.model_dump(),
        status_code=200,
    )


@patch(
    "splunklib.ai.agent._testing_local_tools_path",
    os.path.join(
        os.path.dirname(__file__),
        "testdata",
        "non_existent.py",
    ),
)
@pytest.mark.asyncio
async def test_remote_tools():
    pytest.importorskip("langchain_ollama")

    mcp = FastMCP("MCP Server", streamable_http_path="/")

    @mcp.tool(description="Returns the current temperature in the city")
    def temperature(city: str) -> str:
        if city == "Krakow":
            return "31.5C"
        else:
            return "22.1C"

    @contextlib.asynccontextmanager
    async def lifespan(app: Starlette):
        async with mcp.session_manager.run():
            yield

    async with run_http_server(
        Starlette(
            routes=[
                Mount("/services/mcp", app=mcp.streamable_http_app()),
                Route(
                    "/services/authorization/tokens", tokens_handler, methods=["POST"]
                ),
            ],
            lifespan=lifespan,
        )
    ) as (host, port):
        service = await asyncio.to_thread(
            lambda: connect(
                scheme="http",
                host=host,
                port=port,
                splunkToken=AUTH_TOKEN,
                autologin=True,
                username="admin",  # not required, but set to avoid mocking the authentication/current-context endpoint
            ),
        )

        model = OllamaModel(model="llama3.2:3b")

        async with Agent(
            model=model,
            system_prompt="You must use the available tools to perform requested operations",
            service=service,
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
            assert "31.5" in response, "Invalid LLM response"


@patch(
    "splunklib.ai.agent._testing_local_tools_path",
    os.path.join(
        os.path.dirname(__file__),
        "testdata",
        "non_existent.py",
    ),
)
@pytest.mark.asyncio
async def test_remote_tools_mcp_app_unavail():
    pytest.importorskip("langchain_ollama")

    async with run_http_server(
        Starlette(
            routes=[
                Route(
                    "/services/authorization/tokens", tokens_handler, methods=["POST"]
                ),
            ],
        )
    ) as (host, port):
        service = await asyncio.to_thread(
            lambda: connect(
                scheme="http",
                host=host,
                port=port,
                splunkToken=AUTH_TOKEN,
                autologin=True,
                username="admin",  # not required, but set to avoid mocking the authentication/current-context endpoint
            ),
        )

        model = OllamaModel(model="llama3.2:3b")

        # Make sure that we are able to run the agent, with a service provided in case
        # the MCP Server App is not installed on the instance.
        async with Agent(
            model=model, service=service, system_prompt="Your name is stefan"
        ) as agent:
            result = await agent.invoke(
                [
                    Message(
                        role="user",
                        content="What is your name? Answer in one word",
                    )
                ]
            )

            response = result.messages[-1].content.strip().lower().replace(".", "")
            assert "stefan" in response


@patch(
    "splunklib.ai.agent._testing_local_tools_path",
    os.path.join(
        os.path.dirname(__file__),
        "testdata",
        "non_existent.py",
    ),
)
@pytest.mark.asyncio
async def test_remote_tools_failure():
    pytest.importorskip("langchain_ollama")

    mcp = FastMCP("MCP Server", streamable_http_path="/")

    @mcp.tool(description="Returns the current temperature in the city")
    def temperature(city: str) -> str:
        # simulate the tool guiding the llm for proper input
        if city == "Cracow":
            raise Exception("Use Polish name of the city")
        if city == "Kraków":
            return "31.5C"
        raise Exception("No such city in DB")

    @contextlib.asynccontextmanager
    async def lifespan(app: Starlette):
        async with mcp.session_manager.run():
            yield

    async with run_http_server(
        Starlette(
            routes=[
                Mount("/services/mcp", app=mcp.streamable_http_app()),
                Route(
                    "/services/authorization/tokens", tokens_handler, methods=["POST"]
                ),
            ],
            lifespan=lifespan,
        )
    ) as (host, port):
        service = await asyncio.to_thread(
            lambda: connect(
                scheme="http",
                host=host,
                port=port,
                splunkToken=AUTH_TOKEN,
                autologin=True,
                username="admin",  # not required, but set to avoid mocking the authentication/current-context endpoint
            ),
        )

        model = OllamaModel(model="ministral-3:8b")

        async with Agent(
            model=model,
            system_prompt="You must use the available tools to perform requested operations. You MUST Retry tool calls until you receive a valid response, that's not an error",
            service=service,
            use_mcp_tools=True,
        ) as agent:
            result = await agent.invoke(
                [
                    Message(
                        role="user",
                        content="""
                        What is the weather like today in Cracow? Use the provided tools to check the temperature.
                        """,
                    )
                ]
            )
            response = result.messages[-1].content

            assert "31.5" in response, "Invalid LLM response"


@contextlib.asynccontextmanager
async def run_http_server(app: Starlette):
    # Create a socket with port 0, this will cause a creation of a socket with
    # a free port that is avail on the system, such that we do not have to hardcode a port, or
    # re-try until we find a free one.
    # Additionally this avoid a race, since the port is up and running here, rather started by
    # server.serve, which happens concurrently.
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    sock.listen(128)
    host, port = sock.getsockname()

    config = uvicorn.Config(app, log_level="warning")
    server = uvicorn.Server(config)
    task = asyncio.create_task(server.serve(sockets=[sock]))

    yield (host, port)

    await server.shutdown(sockets=[sock])
    sock.close()
    task.cancel()

    with contextlib.suppress(asyncio.CancelledError):
        await task

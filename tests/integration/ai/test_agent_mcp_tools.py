import asyncio
import contextlib
import json
import logging
import os
import socket
from collections.abc import AsyncGenerator
from dataclasses import asdict, dataclass
from typing import Annotated, Any
from unittest.mock import patch

import pytest
import uvicorn
from mcp.server.fastmcp import Context, FastMCP
from mcp.types import CallToolResult, TextContent
from pydantic import BaseModel, Field
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Mount, Route

from splunklib.ai import Agent
from splunklib.ai.engines.langchain import LOCAL_TOOL_PREFIX
from splunklib.ai.messages import HumanMessage, ToolMessage
from splunklib.ai.tool_filtering import ToolFilters
from splunklib.ai.tools import (
    _get_splunk_username,  # pyright: ignore[reportPrivateUsage]
    locate_app,
)
from splunklib.client import connect
from tests import testlib
from tests.ai_testlib import AITestCase

OPENAI_BASE_URL = "http://localhost:11434/v1"
OPENAI_API_KEY = "ollama"


class TestTools(AITestCase):
    @patch(
        "splunklib.ai.agent._testing_local_tools_path",
        os.path.join(
            os.path.dirname(__file__),
            "testdata",
            "weather.py",
        ),
    )
    @patch("splunklib.ai.agent._testing_app_id", "app_id")
    async def test_tool_execution_structured_output(self) -> None:
        # Skip if the langchain_openai package is not installed
        pytest.importorskip("langchain_openai")

        async with Agent(
            model=(await self.model()),
            system_prompt="You must use the available tools to perform requested operations",
            service=self.service,
            use_mcp_tools=True,
        ) as agent:
            result = await agent.invoke(
                [
                    HumanMessage(
                        content=(
                            "What is the weather like today in Krakow? Use the provided tools to check the temperature."
                            "Return a short response, containing the tool response."
                        ),
                    )
                ]
            )

            tool_message = next(
                filter(lambda m: m.role == "tool", result.messages), None
            )
            assert isinstance(tool_message, ToolMessage), "Invalid tool message"
            assert tool_message, "No tool message found in response"
            assert tool_message.name == "temperature", "Invalid tool name"

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
    @patch("splunklib.ai.agent._testing_app_id", "app_id")
    async def test_tool_execution_service_access(self) -> None:
        # Skip if the langchain_openai package is not installed
        pytest.importorskip("langchain_openai")

        async with Agent(
            model=(await self.model()),
            system_prompt="You must use the available tools to perform requested operations",
            service=self.service,
            use_mcp_tools=True,
        ) as agent:
            result = await agent.invoke(
                [
                    HumanMessage(
                        content=(
                            "Using available tools, please check the startup time of the splunk instance."
                            "Return a short response, containing the tool response."
                        ),
                    )
                ]
            )

            want_startup_time = f"{self.service.info.startup_time}"

            tool_message = next(
                filter(lambda m: m.role == "tool", result.messages), None
            )
            assert isinstance(tool_message, ToolMessage), "Invalid tool message"
            assert tool_message, "No tool message found in response"
            assert tool_message.name == "startup_time", "Invalid tool name"

            response = result.messages[-1].content
            assert want_startup_time in response, "Invalid LLM response"

    @patch(
        "splunklib.ai.agent._testing_local_tools_path",
        os.path.join(os.path.dirname(__file__), "testdata", "tool_filtering.py"),
    )
    @patch("splunklib.ai.agent._testing_app_id", "app_id")
    @pytest.mark.asyncio
    async def test_agent_filtering_tools(self) -> None:
        pytest.importorskip("langchain_openai")

        async with Agent(
            model=(await self.model()),
            system_prompt="",
            service=self.service,
            use_mcp_tools=True,
            tool_filters=ToolFilters(
                allowed_names=["test_tool_1"], allowed_tags=["test_tag_2"]
            ),
        ) as agent:
            tool_names = [t.name for t in agent.tools]
            assert tool_names == ["test_tool_1", "test_tool_2", "test_tool_4"]

    @patch(
        "splunklib.ai.agent._testing_local_tools_path",
        os.path.join(
            os.path.dirname(__file__),
            "testdata",
            "multi_city_weather.py",
        ),
    )
    @patch("splunklib.ai.agent._testing_app_id", "app_id")
    async def test_multiple_and_concurrent_tool_calls(self) -> None:
        # Skip if the langchain_openai package is not installed
        pytest.importorskip("langchain_openai")

        async with Agent(
            model=(await self.model()),
            system_prompt="You must use the available tools to perform requested operations",
            service=self.service,
            use_mcp_tools=True,
        ) as agent:
            call_count_tool = next(
                (t for t in agent.tools if t.name == "backdoor_tool_call_count"), None
            )
            assert call_count_tool is not None

            # This will cause 3 tools to be called concurrently.
            result = await agent.invoke(
                [
                    HumanMessage(
                        content=(
                            "What is the weather like today in Krakow, Warsaw and Gdansk?"
                            "Use the provided tools to check the temperature."
                            "Return a short response, containing all of tool responses."
                        ),
                    )
                ]
            )

            response = result.messages[-1].content
            assert "31.5" in response, "Invalid LLM response"
            assert "30.0" in response, "Invalid LLM response"
            assert "25.5" in response, "Invalid LLM response"

            # Call additional tool, to make sure that MCP is shared across an agent, not invoke.
            result = await agent.invoke(
                [
                    HumanMessage(
                        content=(
                            "What is the weather like today in Poznan?"
                            "Use the provided tools to check the temperature."
                            "Return a short response, containing all of tool responses."
                        ),
                    )
                ]
            )
            response = result.messages[-1].content
            assert "28.5" in response, "Invalid LLM response"

            # Make sure MCP was alive during entire Agent lifetime.
            tool_result = await call_count_tool.func()
            assert tool_result.structured_content is not None
            result = tool_result.structured_content["result"]
            assert isinstance(result, int)
            assert result == 4


class TestSplunkGetUsername(testlib.SDKTestCase):
    def get_splunk_bearer_token(self) -> str:
        res = self.service.post(
            path_segment="authorization/tokens",
            name=self.service.username,
            audience="test",
            type="ephemeral",
            output_mode="json",
        )
        token = json.loads(str(res.body))["entry"][0]["content"]["token"]
        return token

    def test_get_splunk_username(self) -> None:
        self.assertTrue(
            self.service.username and self.service.password
        )  # our CI logs-in with username and password.

        self.assertEqual(_get_splunk_username(self.service), self.service.username)

        service = connect(
            scheme=self.service.scheme,
            host=self.service.host,
            port=self.service.port,
            token=self.get_splunk_bearer_token(),
        )

        self.assertEqual(_get_splunk_username(service), self.service.username)


class TestAppLocate:
    def test_locate_app(self) -> None:
        path = os.path.join(os.path.dirname(__file__), "testdata", "app-inference")
        app_id, app_dir = locate_app(
            splunk_home=path,
            sdk_location_path=os.path.join(
                path, "etc", "apps", "appname", "bin", "lib", "somefile.py"
            ),
        )
        assert app_id == "appname"
        assert app_dir == os.path.join(path, "etc", "apps", "appname")


AUTH_TOKEN = "foobarbaz"


async def mcp_token_handler(_: Request) -> Response:
    return JSONResponse(
        content={"token": AUTH_TOKEN},
        status_code=200,
    )


class TestRemoteTools(AITestCase):
    @patch(
        "splunklib.ai.agent._testing_local_tools_path",
        os.path.join(
            os.path.dirname(__file__),
            "testdata",
            "non_existent.py",
        ),
    )
    @patch("splunklib.ai.agent._testing_app_id", "fancyapp")
    @pytest.mark.asyncio
    async def test_remote_tools(self):
        pytest.importorskip("langchain_openai")

        mcp = FastMCP("MCP Server", streamable_http_path="/")

        trace_id: str | None = None
        app_id: str | None = None

        @mcp.tool(description="Returns the current temperature in the city")
        def temperature(ctx: Context, city: str) -> str:
            nonlocal trace_id, app_id
            assert trace_id is None and app_id is None
            assert ctx.request_context.meta is not None
            meta = ctx.request_context.meta.model_dump()
            splunk = meta.get("splunk", {})
            trace_id = splunk.get("trace_id")
            app_id = splunk.get("app_id")

            if city == "Krakow":
                return "31.5C"
            else:
                return "22.1C"

        @contextlib.asynccontextmanager
        async def lifespan(app: Starlette):
            async with mcp.session_manager.run():
                yield

        http_trace_id: str | None = None
        http_app_id: str | None = None
        middleware_called = False

        class MCPMiddleware(BaseHTTPMiddleware):
            async def dispatch(self, request: Request, call_next):
                if request.url.path.startswith("/services/mcp/"):
                    nonlocal http_trace_id, http_app_id, middleware_called

                    trace_id = request.headers.get("x-splunk-trace-id")
                    app_id = request.headers.get("x-splunk-app-id")

                    # Make sure header values do not change over time.
                    if middleware_called:
                        assert http_trace_id == trace_id
                        assert http_app_id == app_id

                    middleware_called = True
                    http_trace_id = trace_id
                    http_app_id = app_id

                return await call_next(request)

        async with run_http_server(
            Starlette(
                routes=[
                    Mount("/services/mcp", app=mcp.streamable_http_app()),
                    Route(
                        "/services/mcp_token",
                        mcp_token_handler,
                        methods=["GET"],
                    ),
                ],
                lifespan=lifespan,
                middleware=[Middleware(MCPMiddleware)],
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

            async with Agent(
                model=(await self.model()),
                system_prompt="You must use the available tools to perform requested operations",
                service=service,
                use_mcp_tools=True,
            ) as agent:
                result = await agent.invoke(
                    [
                        HumanMessage(
                            content=(
                                "What is the weather like today in Krakow? Use the provided tools to check the temperature."
                                "Return a short response, containing the tool response."
                            ),
                        )
                    ]
                )

                tool_message = next(
                    filter(lambda m: m.role == "tool", result.messages), None
                )
                assert isinstance(tool_message, ToolMessage), "Invalid tool message"
                assert tool_message, "No tool message found in response"
                assert tool_message.name == "temperature", "Invalid tool name"

                response = result.messages[-1].content
                assert "31.5" in response, "Invalid LLM response"

                assert trace_id == agent.trace_id
                assert app_id == "fancyapp"
                assert http_trace_id == agent.trace_id
                assert http_app_id == "fancyapp"

    @patch(
        "splunklib.ai.agent._testing_local_tools_path",
        os.path.join(
            os.path.dirname(__file__),
            "testdata",
            "non_existent.py",
        ),
    )
    @patch("splunklib.ai.agent._testing_app_id", "app_id")
    @pytest.mark.asyncio
    async def test_remote_tools_mcp_app_unavail(self):
        pytest.importorskip("langchain_openai")

        async with run_http_server(
            Starlette(
                routes=[],
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

            # Make sure that we are able to run the agent, with a service provided in case
            # the MCP Server App is not installed on the instance.
            async with Agent(
                model=(await self.model()),
                service=service,
                system_prompt="Your name is stefan",
            ) as agent:
                result = await agent.invoke(
                    [
                        HumanMessage(
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
    @patch("splunklib.ai.agent._testing_app_id", "app_id")
    @pytest.mark.asyncio
    async def test_remote_tools_failure(self):
        pytest.importorskip("langchain_openai")

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
                        "/services/mcp_token",
                        mcp_token_handler,
                        methods=["GET"],
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

            async with Agent(
                model=(await self.model()),
                system_prompt="You must use the available tools to perform requested operations. You MUST Retry tool calls until you receive a valid response, that's not an error",
                service=service,
                use_mcp_tools=True,
            ) as agent:
                result = await agent.invoke(
                    [
                        HumanMessage(
                            content="What is the weather like today in Cracow? Use the provided tools to check the temperature."
                        )
                    ]
                )
                tool_messages = list(
                    filter(lambda m: m.role == "tool", result.messages)
                )
                assert len(tool_messages) == 2, (
                    "Expected multiple tool calls due to retries"
                )
                assert tool_messages[0].status == "error", (
                    "First tool call should be invalid"
                )
                assert tool_messages[1].status == "success", (
                    "Second tool call should be ok"
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
    @patch("splunklib.ai.agent._testing_app_id", "app_id")
    @pytest.mark.asyncio
    async def test_tool_call_text_content_with_structured_output(self) -> None:
        pytest.importorskip("langchain_openai")

        mcp = FastMCP("MCP Server", streamable_http_path="/")

        @dataclass
        class Result:
            celsius_degrees: str

        @mcp.tool(description="Returns the current temperature in the city")
        def temperature(city: str) -> Annotated[CallToolResult, Result]:
            if city == "Krakow":
                temperature = "31.5C"
            else:
                temperature = "22.1C"

            # The Splunk MCP Server App returns a succeeded message in the content
            # and a proper output in the structured_content field.
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"Tool call succeeded, temperature in {city} found",
                    )
                ],
                structuredContent=asdict(Result(temperature)),
            )

        @contextlib.asynccontextmanager
        async def lifespan(app: Starlette):
            async with mcp.session_manager.run():
                yield

        async with run_http_server(
            Starlette(
                routes=[
                    Mount("/services/mcp", app=mcp.streamable_http_app()),
                    Route(
                        "/services/mcp_token",
                        mcp_token_handler,
                        methods=["GET"],
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

            async with Agent(
                model=(await self.model()),
                system_prompt="You must use the available tools to perform requested operations",
                service=service,
                use_mcp_tools=True,
            ) as agent:
                result = await agent.invoke(
                    [
                        HumanMessage(
                            content=(
                                "What is the weather like today in Krakow? Use the provided tools to check the temperature."
                                "Return a short response, containing the tool response."
                            ),
                        )
                    ]
                )

                found_tool_message = False
                for msg in result.messages:
                    if isinstance(msg, ToolMessage):
                        found_tool_message = True
                        # Both text content and structured_content should be in the
                        # content of a tool response.
                        assert (
                            "Tool call succeeded, temperature in Krakow found"
                            in msg.content
                        )
                        assert '"celsius_degrees": "31.5C"' in msg.content
                assert found_tool_message, "missing ToolMessage in agent response"

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
    @patch("splunklib.ai.agent._testing_app_id", "app_id")
    @pytest.mark.asyncio
    async def test_splunk_mcp_server_app(self) -> None:
        # Skip if the langchain_openai package is not installed
        pytest.importorskip("langchain_openai")

        # TODO: Remove this test once we have an E2E with Splunk MCP Server app.

        self.skipTest("manual test")

        logger = logging.getLogger("test")
        logger.setLevel(logging.DEBUG)

        service = connect(
            port=8090,
            host="localhost",
            username="admin",
            password="",
            autologin=True,
        )

        async with Agent(
            model=(await self.model()),
            system_prompt="You must use the available tools to perform requested operations",
            service=service,
            use_mcp_tools=True,
            logger=logger,
        ) as agent:
            for tool in agent.tools:
                if tool.name == "splunk_get_indexes":
                    result = await tool.func()
                    assert len(result.structured_content["results"]) != 0
                    return

            assert False, "Tool splunk_get_indexes not found"


class TestHandlingToolNameCollision(AITestCase):
    @patch(
        "splunklib.ai.agent._testing_local_tools_path",
        os.path.join(os.path.dirname(__file__), "testdata", "tool_collision.py"),
    )
    @patch("splunklib.ai.agent._testing_app_id", "app_id")
    @pytest.mark.asyncio
    async def test_tool_collision(self) -> None:
        pytest.importorskip("langchain_openai")

        local_tool_name = f"{LOCAL_TOOL_PREFIX}temperature"
        remote_tool_name = "temperature"

        mcp = FastMCP("MCP Server", streamable_http_path="/")
        mcp.add_tool(
            name=remote_tool_name,
            description="Remote temperature tool",
            fn=lambda: "31.5C",
        )

        @contextlib.asynccontextmanager
        async def lifespan(_app: Starlette) -> AsyncGenerator[None, Any]:
            async with mcp.session_manager.run():
                yield

        async with run_http_server(
            Starlette(
                routes=[
                    Mount("/services/mcp", app=mcp.streamable_http_app()),
                    Route("/services/mcp_token", mcp_token_handler, methods=["GET"]),
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
                    # To avoid mocking `authentication/current-context` endpoint
                    username="admin",
                ),
            )

            class ToolResults(BaseModel):
                local_temperature: str = Field(
                    description=f"Result from {local_tool_name=}"
                )
                remote_temperature: str = Field(
                    description=f"Result from {remote_tool_name=}"
                )

            async with Agent(
                model=await self.model(),
                system_prompt="Return only JSON, no additional text.",
                service=service,
                use_mcp_tools=True,
                output_schema=ToolResults,
            ) as agent:
                assert len(agent.tools) == 2

                content = "Call tools to populate output."
                response = await agent.invoke([HumanMessage("user", content)])
                print(response.structured_output)
                assert response.structured_output.remote_temperature == "31.5C"
                assert response.structured_output.local_temperature == "22.1C"


@contextlib.asynccontextmanager
async def run_http_server(
    app: Starlette,
) -> AsyncGenerator[tuple[str, int], Any]:
    # Create a socket with port 0, this will cause a creation of a socket with
    # a free port that is avail on the system, such that we do not have to
    # hardcode a port, or re-try until we find a free one.
    # Additionally this avoid a race, since the port is up and running here,
    # rather started by server.serve, which happens concurrently.
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

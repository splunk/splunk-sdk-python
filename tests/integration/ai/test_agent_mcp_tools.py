import asyncio
import contextlib
import os
import socket
from unittest.mock import patch

import pytest
from starlette.middleware import Middleware
import uvicorn
from mcp.server.fastmcp import Context, FastMCP
from pydantic import BaseModel
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Mount, Route
from starlette.middleware.base import BaseHTTPMiddleware

from splunklib.ai import Agent
from splunklib.ai.messages import HumanMessage, ToolMessage
from splunklib.ai.tool_filtering import ToolFilters
from splunklib.ai.tools import (
    _get_splunk_token_for_mcp,
    _get_splunk_username,
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
                        "/services/authorization/tokens",
                        tokens_handler,
                        methods=["POST"],
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
                routes=[
                    Route(
                        "/services/authorization/tokens",
                        tokens_handler,
                        methods=["POST"],
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
                        "/services/authorization/tokens",
                        tokens_handler,
                        methods=["POST"],
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

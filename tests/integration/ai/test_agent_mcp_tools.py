# pyright: reportUnusedFunction=false, reportUnusedParameter=false

import asyncio
import contextlib
import json
import os
import socket
from collections.abc import AsyncGenerator
from dataclasses import asdict, dataclass
from typing import Annotated, Any, override
from unittest.mock import patch

import pytest
import uvicorn
from mcp.server.fastmcp import Context, FastMCP
from mcp.types import CallToolResult, TextContent
from pydantic import BaseModel, Field
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Mount, Route

from splunklib.ai import Agent
from splunklib.ai.engines.langchain import LOCAL_TOOL_PREFIX
from splunklib.ai.messages import (
    AIMessage,
    HumanMessage,
    ToolCall,
    ToolFailureResult,
    ToolMessage,
    ToolResult,
)
from splunklib.ai.middleware import (
    ModelMiddlewareHandler,
    ModelRequest,
    ModelResponse,
    model_middleware,
)
from splunklib.ai.tool_settings import (
    LocalToolSettings,
    RemoteToolSettings,
    ToolAllowlist,
    ToolSettings,
)
from splunklib.ai.tools import (
    ToolType,
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
        os.path.join(os.path.dirname(__file__), "testdata", "weather.py"),
    )
    @patch("splunklib.ai.agent._testing_app_id", "app_id")
    async def test_tool_execution_structured_output(self) -> None:
        # Skip if the langchain_openai package is not installed
        pytest.importorskip("langchain_openai")

        async with Agent(
            model=(await self.model()),
            system_prompt="You must use the available tools to perform requested operations",
            service=self.service,
            tool_settings=ToolSettings(local=True, remote=None),
        ) as agent:
            result = await agent.invoke(
                [
                    HumanMessage(
                        content=(
                            "What is the weather like today in Krakow? Use the provided tools to check the temperature."
                            + "Return a short response, containing the tool response."
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

            response = result.final_message.content
            assert "31.5" in response, "Invalid LLM response"

    @patch(
        "splunklib.ai.agent._testing_local_tools_path",
        os.path.join(os.path.dirname(__file__), "testdata", "tool_context.py"),
    )
    @patch("splunklib.ai.agent._testing_app_id", "app_id")
    async def test_tool_execution_service_access(self) -> None:
        # Skip if the langchain_openai package is not installed
        pytest.importorskip("langchain_openai")

        async with Agent(
            model=(await self.model()),
            system_prompt="You must use the available tools to perform requested operations",
            service=self.service,
            tool_settings=ToolSettings(local=True, remote=None),
        ) as agent:
            result = await agent.invoke(
                [
                    HumanMessage(
                        content=(
                            "Using available tools, please check the startup time of the splunk instance."
                            + "Return a short response, containing the tool response."
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

            response = result.final_message.content
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
            tool_settings=ToolSettings(
                local=LocalToolSettings(
                    allowlist=ToolAllowlist(names=["test_tool_1"], tags=["test_tag_2"])
                ),
                remote=None,
            ),
        ) as agent:
            tool_names = [t.name for t in agent.tools]
            assert tool_names == ["test_tool_1", "test_tool_2", "test_tool_4"]

    @patch(
        "splunklib.ai.agent._testing_local_tools_path",
        os.path.join(os.path.dirname(__file__), "testdata", "multi_city_weather.py"),
    )
    @patch("splunklib.ai.agent._testing_app_id", "app_id")
    async def test_multiple_and_concurrent_tool_calls(self) -> None:
        # Skip if the langchain_openai package is not installed
        pytest.importorskip("langchain_openai")

        async with Agent(
            model=(await self.model()),
            system_prompt="You must use the available tools to perform requested operations",
            service=self.service,
            tool_settings=ToolSettings(local=True, remote=None),
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
                            + "Use the provided tools to check the temperature."
                            + "Return a short response, containing all of tool responses."
                        ),
                    )
                ]
            )

            response = result.final_message.content
            assert "31.5" in response, "Invalid LLM response"
            assert "30.0" in response, "Invalid LLM response"
            assert "25.5" in response, "Invalid LLM response"

            # Call additional tool, to make sure that MCP is shared across an agent, not invoke.
            result = await agent.invoke(
                [
                    HumanMessage(
                        content=(
                            "What is the weather like today in Poznan?"
                            + "Use the provided tools to check the temperature."
                            + "Return a short response, containing all of tool responses."
                        ),
                    )
                ]
            )
            response = result.final_message.content
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
            name=self.service.username,  # pyright: ignore[reportUnknownArgumentType]
            audience="test",
            type="ephemeral",
            output_mode="json",
        )
        token = json.loads(str(res.body))["entry"][0]["content"]["token"]  # pyright: ignore[reportUnknownArgumentType]
        return token

    def test_get_splunk_username(self) -> None:
        # Our CI logs-in with username and password.
        assert self.service.username
        assert self.service.password

        assert _get_splunk_username(self.service) == self.service.username

        service = connect(
            scheme=self.service.scheme,  # pyright: ignore[reportUnknownArgumentType]
            host=self.service.host,  # pyright: ignore[reportUnknownArgumentType]
            port=self.service.port,
            token=self.get_splunk_bearer_token(),
        )

        assert _get_splunk_username(service) == self.service.username


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
    return JSONResponse(content={"token": AUTH_TOKEN}, status_code=200)


class TestRemoteTools(AITestCase):
    @patch(
        "splunklib.ai.agent._testing_local_tools_path",
        os.path.join(os.path.dirname(__file__), "testdata", "non_existent.py"),
    )
    @patch("splunklib.ai.agent._testing_app_id", "fancyapp")
    @pytest.mark.asyncio
    async def test_remote_tools(self) -> None:
        pytest.importorskip("langchain_openai")

        mcp = FastMCP("MCP Server", streamable_http_path="/")

        trace_id: str | None = None
        app_id: str | None = None

        @mcp.tool(description="Returns the current temperature in the city")
        def temperature(ctx: Context[Any, Any], city: str) -> str:
            nonlocal trace_id, app_id
            assert trace_id is None
            assert app_id is None
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
        async def lifespan(app: Starlette) -> AsyncGenerator[None, Any]:
            async with mcp.session_manager.run():
                yield

        http_trace_id: str | None = None
        http_app_id: str | None = None
        middleware_called = False

        class MCPMiddleware(BaseHTTPMiddleware):
            @override
            async def dispatch(
                self, request: Request, call_next: RequestResponseEndpoint
            ) -> Response:
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
                    Route("/services/mcp_token", mcp_token_handler, methods=["GET"]),
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
                tool_settings=ToolSettings(
                    local=False,
                    remote=RemoteToolSettings(
                        allowlist=ToolAllowlist(names=["temperature"])
                    ),
                ),
            ) as agent:
                result = await agent.invoke(
                    [
                        HumanMessage(
                            content=(
                                "What is the weather like today in Krakow? Use the provided tools to check the temperature."
                                + "Return a short response, containing the tool response."
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

                response = result.final_message.content
                assert "31.5" in response, "Invalid LLM response"

                assert trace_id == agent.trace_id
                assert app_id == "fancyapp"
                assert http_trace_id == agent.trace_id  # pyright: ignore[reportUnreachable]
                assert http_app_id == "fancyapp"

    @patch(
        "splunklib.ai.agent._testing_local_tools_path",
        os.path.join(os.path.dirname(__file__), "testdata", "non_existent.py"),
    )
    @patch("splunklib.ai.agent._testing_app_id", "app_id")
    @pytest.mark.asyncio
    async def test_remote_tools_mcp_app_unavailable(self) -> None:
        pytest.importorskip("langchain_openai")

        async with run_http_server(Starlette(routes=[])) as (host, port):
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
                    [HumanMessage(content="What is your name? Answer in one word")]
                )

                response = result.final_message.content.strip().lower().replace(".", "")
                assert "stefan" in response

    @patch(
        "splunklib.ai.agent._testing_local_tools_path",
        os.path.join(os.path.dirname(__file__), "testdata", "non_existent.py"),
    )
    @patch("splunklib.ai.agent._testing_app_id", "app_id")
    @pytest.mark.asyncio
    async def test_remote_tools_failure(self) -> None:
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
        async def lifespan(app: Starlette) -> AsyncGenerator[None, Any]:
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
                    username="admin",  # not required, but set to avoid mocking the authentication/current-context endpoint
                ),
            )

            async with Agent(
                model=(await self.model()),
                system_prompt="You must use the available tools to perform requested operations. "
                + "You MUST Retry tool calls until you receive a valid response, that's not an error",
                service=service,
                tool_settings=ToolSettings(
                    local=False,
                    remote=RemoteToolSettings(
                        allowlist=ToolAllowlist(names=["temperature"])
                    ),
                ),
            ) as agent:
                result = await agent.invoke(
                    [
                        HumanMessage(
                            content="What is the weather like today in Cracow? "
                            + "Use the provided tools to check the temperature."
                        )
                    ]
                )
                tool_messages = [
                    tm for tm in result.messages if isinstance(tm, ToolMessage)
                ]
                assert len(tool_messages) == 2, "Expected 2 tool calls due to retries"
                assert type(tool_messages[0].result) is ToolFailureResult
                assert type(tool_messages[1].result) is ToolResult

                response = result.final_message.content
                assert "31.5" in response, "Invalid LLM response"

    @patch(
        "splunklib.ai.agent._testing_local_tools_path",
        os.path.join(os.path.dirname(__file__), "testdata", "non_existent.py"),
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
        async def lifespan(app: Starlette) -> AsyncGenerator[None, Any]:
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
                    username="admin",  # not required, but set to avoid mocking the authentication/current-context endpoint
                ),
            )

            async with Agent(
                model=(await self.model()),
                system_prompt="You must use the available tools to perform requested operations",
                service=service,
                tool_settings=ToolSettings(
                    local=False,
                    remote=RemoteToolSettings(
                        allowlist=ToolAllowlist(names=["temperature"])
                    ),
                ),
            ) as agent:
                result = await agent.invoke(
                    [
                        HumanMessage(
                            content=(
                                "What is the weather like today in Krakow? "
                                + "Use the provided tools to check the temperature. "
                                + "Return a short response, containing the tool response."
                            ),
                        )
                    ]
                )

                found_tool_message = False
                for msg in result.messages:
                    if isinstance(msg, ToolMessage):
                        found_tool_message = True
                        # Both text content and structured_content should be in the
                        # result of a tool response.
                        tool_result = msg.result
                        assert isinstance(tool_result, ToolResult)
                        assert (
                            "Tool call succeeded, temperature in Krakow found"
                            in tool_result.content
                        )
                        assert tool_result.structured_content is not None
                        assert (
                            tool_result.structured_content["celsius_degrees"] == "31.5C"
                        )
                assert found_tool_message, "missing ToolMessage in agent response"

                response = result.final_message.content
                assert "31.5" in response, "Invalid LLM response"

    @patch(
        "splunklib.ai.agent._testing_local_tools_path",
        os.path.join(os.path.dirname(__file__), "testdata", "temperature_as_dict.py"),
    )
    @patch("splunklib.ai.agent._testing_app_id", "app_id")
    @pytest.mark.asyncio
    async def test_supports_plain_dicts_as_tool_outputs(self) -> None:
        """Regression test for DVPL-13022"""
        pytest.importorskip("langchain_openai")

        messages: list[AIMessage] = [
            AIMessage(
                content="",
                calls=[
                    ToolCall(
                        name="temperature",
                        args={"city": "Krakow"},
                        id="call_hSdIJSuUZOh2IiBsqfrzhA7d",
                        type=ToolType.LOCAL,
                    )
                ],
            ),
            AIMessage(content="The temperature in Krakow is 22°C.", calls=[]),
        ]

        responses = (m for m in messages)

        @model_middleware
        async def middleware(
            req: ModelRequest, handler: ModelMiddlewareHandler
        ) -> ModelResponse:
            return ModelResponse(message=next(responses))

        async with Agent(
            model=(await self.model()),
            system_prompt="You must use the available tools to perform requested operations",
            service=self.service,
            tool_settings=ToolSettings(local=True, remote=None),
            middleware=[middleware],
        ) as agent:
            result = await agent.invoke(
                [
                    HumanMessage(
                        content=(
                            "What is the weather like today in Krakow? Use the provided tools to check the temperature."
                            + "Return a short response, containing the tool response."
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

            response = result.final_message.content
            assert "22" in response, "Invalid LLM response"


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
                tool_settings=ToolSettings(
                    local=True,
                    remote=RemoteToolSettings(
                        allowlist=ToolAllowlist(custom_predicate=lambda _: True)
                    ),
                ),
                output_schema=ToolResults,
            ) as agent:
                assert len(agent.tools) == 2

                content = "Call tools to populate output."
                response = await agent.invoke([HumanMessage(content)])
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

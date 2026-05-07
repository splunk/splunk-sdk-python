import asyncio
import logging
import os
import sys
from collections.abc import AsyncGenerator, Awaitable, Callable, Generator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from enum import Enum
from typing import Any, final, override

import httpx
from anyio import Path
from httpx import Auth, Request, Response
from mcp import ClientSession, LoggingLevel, StdioServerParameters, stdio_client
from mcp.client.session import LoggingFnT
from mcp.client.streamable_http import streamable_http_client
from mcp.types import (
    CallToolResult,
    LoggingMessageNotificationParams,
    PaginatedRequestParams,
    TextContent,
    Tool as MCPTool,
)
from pydantic import BaseModel

from splunklib.ai.registry import (
    LogData,
    _map_logger_to_mcp_logging_level,  # pyright: ignore[reportPrivateUsage]
)
from splunklib.ai.serialized_service import SerializedService
from splunklib.binding import HTTPError
from splunklib.client import Service

TOOLS_FILENAME = "tools.py"


class ToolException(Exception):
    """Custom exception to indicate tool execution errors."""


@dataclass(frozen=True, kw_only=True)
class ToolResult:
    content: str
    structured_content: dict[str, Any] | None


class ToolType(Enum):
    LOCAL = "local"
    REMOTE = "remote"


@dataclass(frozen=True, kw_only=True)
class ToolMetadata:
    name: str
    description: str
    input_schema: dict[str, Any]
    type: ToolType
    tags: list[str]


@dataclass(frozen=True, kw_only=True)
class Tool(ToolMetadata):
    func: Callable[..., Awaitable[ToolResult]]


def _splunk_home() -> str:
    splunk_home = os.environ.get("SPLUNK_HOME", "/opt/splunk")
    if not splunk_home.startswith("/"):
        raise RuntimeError("SPLUNK_HOME is not absolute")
    return splunk_home


def locate_app(
    splunk_home: str | None = None, sdk_location_path: str = __file__
) -> tuple[str, str]:
    """
    This function returns the path to the tools file of the app, assumes that the SDK
    is vendored into the app.

    The path might not exist on the filesystem.
    """

    if splunk_home is None:
        splunk_home = _splunk_home()

    apps_path = os.path.join(splunk_home, "etc", "apps") + os.path.sep

    if not sdk_location_path.startswith(apps_path):
        raise RuntimeError(f"Failed to locate app: Script not located in {apps_path}<app-id>")

    parts = Path(sdk_location_path).relative_to(apps_path).parts
    if len(parts) == 0:
        raise RuntimeError(f"Failed to locate app: Script not located in {apps_path}<app-id>")

    assert parts[0] != "."
    assert parts[1] != ".."

    app_id = parts[0]
    return (app_id, os.path.join(splunk_home, "etc", "apps", app_id))


def build_local_tools_path(dir: str) -> str:
    return os.path.join(dir, "bin", TOOLS_FILENAME)


def _map_logging_level(level: LoggingLevel) -> int:
    match level:
        case "debug":
            return logging.DEBUG
        case "info":
            return logging.INFO
        case "notice":
            return logging.INFO
        case "warning":
            return logging.WARN
        case "error":
            return logging.ERROR
        case "critical":
            return logging.CRITICAL
        case "alert":
            return logging.CRITICAL
        case "emergency":
            return logging.CRITICAL


@dataclass
class _MCPLoggingHandler(LoggingFnT):
    _logger: logging.Logger

    @property
    def level(self) -> LoggingLevel:
        return _map_logger_to_mcp_logging_level(self._logger.level)

    @override
    async def __call__(
        self,
        params: LoggingMessageNotificationParams,
    ) -> None:
        # TODO: Add call_id.
        record = LogData(**params.data)
        self._logger.log(
            _map_logging_level(params.level),
            msg=f"tool: {record.tool_name}: {record.message}",
        )


@final
class _MCPAuth(Auth):
    def __init__(self, authorization: str) -> None:
        self._authorization = authorization

    @override
    def auth_flow(self, request: Request) -> Generator[Request, Response]:
        request.headers["Authorization"] = self._authorization
        yield request


async def _list_all_tools(session: ClientSession) -> list[MCPTool]:
    cursor: str | None = None
    tools: list[MCPTool] = []
    while True:
        result = await session.list_tools(params=PaginatedRequestParams(cursor=cursor))
        tools.extend(result.tools)
        if not result.nextCursor:
            break
        cursor = result.nextCursor
    return tools


def _convert_mcp_tool(
    session: ClientSession,
    type: ToolType,
    app_id: str,
    trace_id: str,
    tool: MCPTool,
    service: Service,
) -> Tool:
    # Trust model: SerializedService (containing Splunk credentials) is only passed to
    # LOCAL MCP tools, which run in the same trust boundary as modular inputs and custom
    # search commands. REMOTE tools (Splunk MCP Server App) receive only trace_id and
    # app_id - they authenticate independently via a separate MCP token.

    async def call_tool(**arguments: dict[str, Any]) -> ToolResult:
        meta: dict[str, Any] | None = None
        match type:
            case ToolType.LOCAL:
                meta = {
                    "splunk": {
                        # Provide access to the splunk instance in local tools.
                        # No need to do anything special for remote tools, since
                        # these tools are already authenticated with the token.
                        "service": SerializedService.from_service(service),
                        # Currently we don't need to send the trace_id and app_id to
                        # local tools, since that is only really needed to correlate
                        # logs, but for local tools we know that logs coming from the
                        # local tool registry are already reloaded to this agent.
                    }
                }
            case ToolType.REMOTE:
                meta = {
                    "splunk": {"trace_id": trace_id, "app_id": app_id},
                }

        call_tool_result = await session.call_tool(
            name=tool.name,
            arguments=arguments,
            meta=meta,
        )
        return _convert_tool_result(call_tool_result)

    splunk_meta: dict[str, Any] = (tool.meta or {}).get("splunk") or {}
    tags = splunk_meta.get("tags", [])

    return Tool(
        name=tool.name,
        description=tool.description or "",
        input_schema=tool.inputSchema,
        func=call_tool,
        tags=tags,
        type=type,
    )


def _convert_tool_result(
    result: CallToolResult,
) -> ToolResult:
    # By convention, when isError is set, the first TextContent contains the error description.
    if result.isError:
        error_message = "Tool execution failed without any concrete error message"
        for content in result.content:
            if isinstance(content, TextContent):
                error_message = content.text
                break
        raise ToolException(error_message)

    text_contents: list[str] = []
    for content in result.content:
        if isinstance(content, TextContent):
            text_contents.append(content.text)

    return ToolResult(content="\n".join(text_contents), structured_content=result.structuredContent)


def _get_mcp_token(splunk_username: str, service: Service) -> str | None:
    try:
        res = service.get(
            path_segment="mcp_token",
            username=splunk_username,
            output_mode="json",
        )
    except HTTPError as e:
        if e.status == 404:
            return None
        raise

    class ResponseBody(BaseModel):
        token: str

    return ResponseBody.model_validate_json(str(res.body)).token


@asynccontextmanager
async def connect_local_mcp(
    local_tools_path: str,
    logger: logging.Logger,
) -> AsyncGenerator[ClientSession]:
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[local_tools_path],
        env=dict(os.environ),
    )

    async with stdio_client(server_params) as (read, write):
        logging_handler = _MCPLoggingHandler(logger)
        async with ClientSession(read, write, logging_callback=logging_handler) as session:
            await session.initialize()

            _ = await session.set_logging_level(logging_handler.level)

            yield session


# Based on streamable_http_client defaults, when http_client is unset.
_MCP_DEFAULT_TIMEOUT = 30.0  # General operations (seconds)
_MCP_DEFAULT_SSE_READ_TIMEOUT = 300.0  # SSE streams - 5 minutes (seconds)


@asynccontextmanager
async def connect_remote_mcp(
    service: Service,
    app_id: str,
    trace_id: str,
    splunk_username: str,
) -> AsyncGenerator[ClientSession | None]:
    management_url = f"{service.scheme}://{service.host}:{service.port}"
    mcp_url = f"{management_url}/services/mcp"
    mcp_token = await asyncio.to_thread(lambda: _get_mcp_token(splunk_username, service))
    if mcp_token is not None:
        async with streamable_http_client(
            url=mcp_url,
            http_client=httpx.AsyncClient(
                headers={
                    "x-splunk-trace-id": trace_id,
                    "x-splunk-app-id": app_id,
                },
                auth=_MCPAuth(f"Bearer {mcp_token}"),
                verify=False,
                follow_redirects=True,
                timeout=httpx.Timeout(_MCP_DEFAULT_TIMEOUT, read=_MCP_DEFAULT_SSE_READ_TIMEOUT),
            ),
        ) as (read, write, _):
            async with ClientSession(read, write) as session:
                await session.initialize()
                yield session
    else:
        yield None


async def load_mcp_tools(
    session: ClientSession,
    type: ToolType,
    app_id: str,
    trace_id: str,
    service: Service,
) -> list[Tool]:
    tools = await _list_all_tools(session)
    return [_convert_mcp_tool(session, type, app_id, trace_id, tool, service) for tool in tools]

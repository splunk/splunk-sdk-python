import asyncio
import collections.abc
import json
import os
import sys
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any, override

import httpx
from anyio import Path
from httpx import Auth, Request, Response
from mcp import ClientSession, StdioServerParameters, stdio_client
from mcp.client.streamable_http import streamable_http_client
from mcp.types import CallToolResult, PaginatedRequestParams, TextContent
from mcp.types import Tool as MCPTool
from pydantic import BaseModel

from splunklib.ai.types import Tool, ToolResult, ToolException
from splunklib.client import Service

TOOLS_FILENAME = "tools.py"


def _splunk_home() -> str:
    splunk_home = os.environ.get("SPLUNK_HOME", "/opt/splunk")
    if not splunk_home.startswith("/"):
        raise RuntimeError("SPLUNK_HOME is not absolute")
    return splunk_home


def locate_tools_path_by_sdk_location(
    splunk_home: str | None = None, sdk_location_path: str = __file__
) -> str:
    """
    This function returns the path to the tools file of the app, assumes that the SDK
    is vendored into the app.

    The path might not exist on the filesystem.
    """

    if splunk_home is None:
        splunk_home = _splunk_home()

    apps_path = os.path.join(splunk_home, "etc", "apps") + os.path.sep

    if not sdk_location_path.startswith(apps_path):
        raise RuntimeError(
            f"Failed to locate app: Script not located in {apps_path}<app-id>"
        )

    parts = Path(sdk_location_path).relative_to(apps_path).parts
    if len(parts) == 0:
        raise RuntimeError(
            f"Failed to locate app: Script not located in {apps_path}<app-id>"
        )

    assert parts[0] != "." and parts[1] != ".."

    app_id = parts[0]
    return os.path.join(splunk_home, "etc", "apps", app_id, "bin", TOOLS_FILENAME)


@dataclass
class LocalCfg:
    tools_path: str
    management_url: str
    token: str


@dataclass
class RemoteCfg:
    mcp_url: str
    token: str


@asynccontextmanager
async def _connect_local_mcp(cfg: LocalCfg):
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[cfg.tools_path],
    )

    # Splunk starts processes with a custom LD_LIBRARY_PATH env var, the mcp lib
    # does not forward all env, but few restricted ones by default. If we don't do
    # so then the shared object that python loads would fail to succeed.
    # TODO: If needed we might in future pass all env vars, but we would have to investigate why
    # the mcp lib did that filtering in the first place. For now we only allow additionally
    # the LD_LIBRARY_PATH.
    ld = os.environ.get("LD_LIBRARY_PATH")
    if ld is not None:
        server_params.env = {"LD_LIBRARY_PATH": ld}

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            yield session


@asynccontextmanager
async def _connect_remote_mcp(cfg: RemoteCfg):
    async with streamable_http_client(
        url=cfg.mcp_url,
        http_client=httpx.AsyncClient(
            auth=_MCPAuth(f"Bearer {cfg.token}"),
            verify=False,
            follow_redirects=True,
        ),
    ) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            yield session


class _MCPAuth(Auth):
    def __init__(self, authorization: str) -> None:
        self._authorization = authorization

    @override
    def auth_flow(
        self, request: Request
    ) -> collections.abc.Generator[Request, Response, None]:
        request.headers["Authorization"] = self._authorization
        yield request


@asynccontextmanager
async def _connect(cfg: LocalCfg | RemoteCfg):
    if isinstance(cfg, RemoteCfg):
        async with _connect_remote_mcp(cfg) as remote_mcp:
            yield remote_mcp
    else:
        async with _connect_local_mcp(cfg) as local_mcp:
            yield local_mcp


async def _list_all_tools(cfg: LocalCfg | RemoteCfg) -> list[MCPTool]:
    async with _connect(cfg) as session:
        cursor: str | None = None
        tools: list[MCPTool] = []
        while True:
            result = await session.list_tools(
                params=PaginatedRequestParams(cursor=cursor)
            )
            tools.extend(result.tools)
            if not result.nextCursor:
                break
            cursor = result.nextCursor
        return tools


def _convert_mcp_tool(
    cfg: LocalCfg | RemoteCfg,
    tool: MCPTool,
) -> Tool:
    async def call_tool(
        **arguments: dict[str, Any],
    ) -> ToolResult:
        # Provide access to the splunk instance in local tools.
        # No need to do anything special for remote tools, since
        # these tools are already authenticated with the token.
        meta: dict[str, Any] | None = None
        if isinstance(cfg, LocalCfg):
            meta = {
                "splunk": {
                    "management_url": cfg.management_url,
                    "management_token": cfg.token,
                }
            }

        async with _connect(cfg) as session:
            call_tool_result = await session.call_tool(
                name=tool.name,
                arguments=arguments,
                meta=meta,
            )
        return _convert_tool_result(call_tool_result)

    return Tool(
        name=tool.name,
        description=tool.description or "",
        input_schema=tool.inputSchema,
        func=call_tool,
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

    # If there is no text content, use the structuredContent as text content.
    if len(text_contents) == 0:
        text_contents.append(json.dumps(result.structuredContent))

    return ToolResult(
        content=text_contents, structured_content=result.structuredContent
    )


def _get_splunk_username(service: Service) -> str:
    if service.username:
        return service.username

    class Content(BaseModel):
        username: str

    class Entry(BaseModel):
        content: Content

    class ResponseBody(BaseModel):
        entry: list[Entry]

    # In case service.username is unavailable, query Splunk API for the username.
    # This can happen when a service is created with a token, without username/password.
    res = service.get(
        path_segment="authentication/current-context",
        output_mode="json",
    )

    body = ResponseBody.model_validate_json(str(res.body))
    if len(body.entry) == 0:
        return ""
    return body.entry[0].content.username


def _get_splunk_token_for_mcp(service: Service) -> str:
    res = service.post(
        path_segment="authorization/tokens",
        name=_get_splunk_username(service),
        audience="mcp",
        type="ephemeral",
        output_mode="json",
    )

    class Content(BaseModel):
        token: str

    class Entry(BaseModel):
        content: Content

    class ResponseBody(BaseModel):
        entry: list[Entry]

    body = ResponseBody.model_validate_json(str(res.body))
    if len(body.entry) == 0:
        return ""
    return body.entry[0].content.token


async def _load_tools(cfg: LocalCfg | RemoteCfg) -> list[Tool]:
    tools = await _list_all_tools(cfg)
    return [_convert_mcp_tool(cfg, tool) for tool in tools]


async def load_mcp_tools(
    service: Service | None = None,
    local_tools_path: str | None = None,
) -> list[Tool]:
    if service is None:
        raise Exception("Service is required to use MCP tools")

    tools: list[Tool] = []

    # TODO: tool name collision between local/remote.

    management_url = f"{service.scheme}://{service.host}:{service.port}"
    mcp_url = f"{management_url}/services/mcp"
    token = await asyncio.to_thread(lambda: _get_splunk_token_for_mcp(service))

    # Load remote MCP tools, only if the MCP server App is available.
    client = httpx.AsyncClient(auth=_MCPAuth(f"Bearer {token}"), verify=False)
    res = await client.get(mcp_url)
    if res.status_code != 404:
        remote_tools = await _load_tools(RemoteCfg(mcp_url=mcp_url, token=token))
        tools.extend(remote_tools)

    # Load local tools.
    if local_tools_path is not None:
        local_tools = await _load_tools(
            LocalCfg(
                tools_path=local_tools_path,
                management_url=management_url,
                # TODO: Is this right? I think we should do this differentlly and either serialize
                # the Service auth fields and send them or generate a separate token, that does not have
                # the "mcp" audience set.
                token=token,
            )
        )
        tools.extend(local_tools)

    return tools

from dataclasses import field
from typing import Any, Literal

from fastmcp.client import Client
from fastmcp.server.dependencies import get_context
from fastmcp.tools import Tool as FastMCPTool
from fastmcp.tools.tool import ToolResult
from mcp.types import Tool as MCPTool
from pydantic.main import BaseModel
from typing_extensions import override


class SplunkMeta(BaseModel):
    permissions: list[str] = field(default=[])
    tool_type: str = field(default="")
    schema_version: str = field(default="")
    execution_mode: str = field(default="")
    execution_endpoint: str = field(default="")


class McpInputOutputSchema(BaseModel):
    type: Literal["object"] = "object"
    properties: dict[str, Any] = field(default_factory=lambda: {})  # pyright: ignore[reportExplicitAny]
    required: list[str] = field(default_factory=lambda: [])


class AddTool(BaseModel):
    script_path: str
    spec: MCPTool


class AddToolsRequest(BaseModel):
    tools: list[AddTool]


class DeleteToolsRequest(BaseModel):
    tools: list[str]


class ProxiedTool(FastMCPTool):
    script: str

    @override
    async def run(self, arguments: dict[str, Any]) -> ToolResult:  # pyright: ignore[reportExplicitAny]
        async def progress_handler(
            progress: float, total: float | None, message: str | None
        ) -> None:
            await get_context().report_progress(progress, total, message)

        c = Client(transport=self.script)

        async with c:
            res = await c.call_tool(
                self.name, arguments, progress_handler=progress_handler
            )

            # TODO: we are missing some fields ....
            # res.is_error
            # res.data
            return ToolResult(
                content=res.content, structured_content=res.structured_content
            )

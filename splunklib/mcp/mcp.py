import httpx
from mcp.types import Tool as MCPTool

from splunklib.mcp.tools.models import AddTool, AddToolsRequest


async def send_mcp_registrations(
    endpoint_url: str,
    tool_registrations: list[MCPTool],
    server_file_path: str,
):
    async with httpx.AsyncClient() as client:
        add_req = AddToolsRequest(
            tools=[
                AddTool(script_path=server_file_path, spec=tool)
                for tool in tool_registrations
            ]
        )

        res = await client.post(endpoint_url, json=add_req.model_dump())
        print(res.status_code)
        print(res.text)


async def execute_tool(endpoint_url: str):
    async with httpx.AsyncClient() as client:
        res = await client.post(endpoint_url)
        print(res.text)

import asyncio
import os

from splunklib.mcp.mcp import send_mcp_registrations
from splunklib.mcp.tools import registrations


async def post_install(server_file_path: str, endpoint_url: str) -> None:
    tool_registrations = await registrations.get_mcp_tools(server_file_path)

    await send_mcp_registrations(
        endpoint_url,
        tool_registrations,
        server_file_path,
    )


if __name__ == "__main__":
    asyncio.run(
        post_install(
            f"{os.getcwd()}/tests/system/test_apps/mcp_enabled_app/bin/mcp_tools.py",
            "http://0.0.0.0:8090/tools",
        )
    )

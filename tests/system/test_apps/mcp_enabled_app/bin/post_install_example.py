import asyncio
import os

from splunklib.mcp.tools.registrations import register_tools_to_mcp_server


async def post_install(server_file_path: str, endpoint_url: str) -> None:
    await register_tools_to_mcp_server(server_file_path, endpoint_url)


if __name__ == "__main__":
    asyncio.run(
        post_install(
            f"{os.getcwd()}/tests/system/test_apps/mcp_enabled_app/bin/mcp_tools.py",
            "http://0.0.0.0:8090/tools",
        )
    )

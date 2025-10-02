import asyncio
import json
from dataclasses import asdict

from fastmcp import FastMCP

from splunklib import client
from splunklib.mcp.tools import SplunkMeta
from splunklib.results import JSONResultsReader

MCP_SERVER_HOST: str = "0.0.0.0"
MCP_SERVER_PORT: int = 2137

MCP_SERVER_NAME: str = "GeneratingCSC PoC Server"
app_mcp_server = FastMCP(MCP_SERVER_NAME)


@app_mcp_server.tool(
    description="""
    The `generatingcsc` command generates a specific number of records.
    
    Example:
    ``| generatingcsc count=4``
    Returns a 4 records having text 'Test Event'.
    """,
    meta=asdict(
        SplunkMeta(
            permissions=["role:search_admin", "role:aws_analyst"],
            tool_type="search",
            schema_version="1.0",
            execution_endpoint="",
            execution_mode="",
        )
    ),
    enabled=True,
)
def generating_csc(count: int = 10) -> list[str]:
    service = client.connect(
        scheme="https",
        host="localhost",
        port="8089",
        username="admin",
        password="changed!",
        autologin=True,
    )
    stream = service.jobs.oneshot(f"| generatingcsc count={count}", output_mode="json")
    results = JSONResultsReader(stream)

    quuuuuux = [json.dumps(r) for r in list(results)]
    print(quuuuuux)
    return quuuuuux


if __name__ == "__main__":
    asyncio.run(
        # app_mcp_server.run_streamable_http_async(MCP_SERVER_HOST, port=MCP_SERVER_PORT)
        app_mcp_server.run_stdio_async(False)
    )

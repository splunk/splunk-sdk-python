import asyncio
import json
import time

from fastmcp import Context, FastMCP

from splunklib import client
from splunklib.mcp.tools.models import SplunkMeta
from splunklib.results import JSONResultsReader

app_mcp_server = FastMCP("GeneratingCSC PoC Server")


@app_mcp_server.tool(
    description="""
    The `generatingcsc` command generates a specific number of records.
    
    Example:
    ``| generatingcsc count=4``
    Returns a 4 records having text 'Test Event'.
    """,
    meta=SplunkMeta(
        permissions=["role:search_admin", "role:aws_analyst"],
        tool_type="search",
        schema_version="1.0",
        execution_endpoint="",
        execution_mode="",
    ).model_dump(),
    enabled=True,
)
async def generating_csc(count: int, ctx: Context) -> list[str]:
    service = client.connect(
        scheme="https",
        host="localhost",
        port="8089",
        username="admin",
        password="changed!",
        autologin=True,
    )
    stream = service.jobs.oneshot(
        f"| generatingcsc count={abs(count)}", output_mode="json"
    )
    results: JSONResultsReader = JSONResultsReader(stream)
    for progress in range(0, 5):
        await ctx.report_progress((progress + 1) * 2, 100, "Addition in progress")
        time.sleep(0.25)

    quuuuuux = [json.dumps(r) for r in list(results)]
    print(quuuuuux)
    return quuuuuux


if __name__ == "__main__":
    MCP_SERVER_HOST: str = "0.0.0.0"
    MCP_SERVER_PORT: int = 2137

    app_mcp_server.run("stdio", show_banner=False)
    # asyncio.run(
    #     app_mcp_server.run_async(
    #         show_banner=False,
    #         # host=MCP_SERVER_HOST,
    #         # port=MCP_SERVER_PORT
    #     )
    # )

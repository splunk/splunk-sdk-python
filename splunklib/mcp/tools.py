import configparser
import os
from dataclasses import asdict, dataclass, field
from typing import Any, Literal

from fastmcp.client import Client
from fastmcp.client.transports import PythonStdioTransport
from mcp.types import Tool


@dataclass
class SplunkMeta:
    permissions: list[str] = field()
    tool_type: str = field(default="")
    schema_version: str = field(default="")
    execution_mode: str = field(default="")
    execution_endpoint: str = field(default="")


@dataclass
class McpInputOutputSchema:
    type: Literal["object"] = "object"
    properties: dict[str, Any] = field(default_factory=lambda: {})  # pyright: ignore[reportExplicitAny]
    required: list[str] = field(default_factory=lambda: [])


tool_reg_prefix = "app:mcp_tool"


def filter_sections(section_name: str) -> bool:
    return section_name.startswith(tool_reg_prefix)


def match_input_schema(input: Literal["query_string"] | Literal["other"]):
    """Gets super messy :("""
    match input:
        case "query_string":
            return {
                "type": "object",
                "properties": {
                    "query_string": {
                        "type": "string",
                        "description": "SPL2 query string",
                    }
                },
            }
        case _:
            raise NotImplementedError("We don't know what to put here lol")


def parse_ai_conf(file_path: str) -> list[Tool]:
    config = configparser.ConfigParser()
    all_sections_len = config.read(file_path)
    if len(all_sections_len) == 0:
        return []

    tool_reg_sections: list[str] = list(filter(filter_sections, config.sections()))
    if len(tool_reg_sections) == 0:
        return []

    ini_tools: list[Tool] = []
    for reg_section in tool_reg_sections:
        reg_section_data = config[reg_section]

        name: str = reg_section.split(":")[2]
        description = reg_section_data["description"]
        # https://modelcontextprotocol.io/specification/2025-06-18/schema#tool
        inputSchema = McpInputOutputSchema(properties={}, required=[])
        outputSchema = McpInputOutputSchema(properties={}, required=[])
        meta = SplunkMeta(
            permissions=[
                perm.strip()
                for perm in reg_section_data["permissions"].strip().split(",")
            ],
            tool_type="search",
            schema_version=reg_section_data["schema_version"].strip(),
        )

        ini_tool = Tool(
            name=name,
            description=description,
            inputSchema=asdict(inputSchema),
            outputSchema=asdict(outputSchema),
            _meta=asdict(meta),
        )
        ini_tools.append(ini_tool)

    return ini_tools


async def get_tools(server_path: str):
    mcp_client = Client(server_path)

    tools = []
    async with mcp_client:
        tools = await mcp_client.list_tools()

        # TODO: Get registrations from ai.conf
        # curr_path = os.path.join(os.getcwd(), "..", "default", "app.conf")
        # yaml_tool_registrations: list[Tool] = parse_ai_conf(curr_path)

    return tools


async def register_tools_from(file_paths: list[str]) -> None:
    """TODO
    1. `POST /tools` with MCP payload
    2.
    """
    print(file_paths)

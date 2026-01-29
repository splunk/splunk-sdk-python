from collections.abc import Sequence
from dataclasses import dataclass

from splunklib.ai.tools import Tool


@dataclass(frozen=True)
class ToolFilters:
    allowed_names: Sequence[str]
    allowed_tags: Sequence[str]


def filter_tools(tools: Sequence[Tool], filters: ToolFilters) -> list[Tool]:
    """Filters all tools by allowlists provided by user to the Agent

    TODO: What happens when local and remote tools share names?
    Does local overwrite remote (or vice versa)? Do we allow choice between overwriting,
    prefixing both or raising exceptions? See tools.py:load_mcp_tools()
    """

    def _predicate(tool: Tool) -> bool:
        return (
            tool.name in filters.allowed_names
            or len(set(filters.allowed_tags).intersection(tool.tags or [])) > 0
        )

    filtered_tools = list(filter(_predicate, tools))
    return filtered_tools

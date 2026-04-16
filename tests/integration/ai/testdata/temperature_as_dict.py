from typing import Any

from splunklib.ai.registry import ToolContext, ToolRegistry

registry = ToolRegistry()


@registry.tool(name="temperature", tags=["read"])
def temperature(city: str, _ctx: ToolContext) -> dict[str, Any]:
    """A simple tool that returns a temperature for the city."""

    return {"city": city, "temperature": 22}


registry.run()

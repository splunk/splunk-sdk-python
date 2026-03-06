from splunklib.ai.registry import ToolRegistry

registry = ToolRegistry()


@registry.tool()
def temperature() -> str:
    """Local temperature tool"""
    return "22.1C"


registry.run()

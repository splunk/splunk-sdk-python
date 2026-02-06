from splunklib.ai.registry import ToolRegistry

registry = ToolRegistry()


@registry.tool()
async def hello(name: str) -> str:
    return f"Hello {name}"


registry.run()

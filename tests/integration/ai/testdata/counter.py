from splunklib.ai.registry import ToolRegistry

registry = ToolRegistry()

i = 0


@registry.tool()
async def counter() -> int:
    global i
    i += 1
    return i


registry.run()

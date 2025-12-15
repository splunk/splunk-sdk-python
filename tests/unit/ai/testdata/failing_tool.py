from splunklib.ai.registry import ToolRegistry

registry = ToolRegistry()


@registry.tool()
def failing_tool() -> str:
    raise Exception("Some tool failure error")


registry.run()

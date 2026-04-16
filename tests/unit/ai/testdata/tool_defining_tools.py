from splunklib.ai.registry import ToolRegistry

registry = ToolRegistry()


@registry.tool()
def add_tool() -> None:
    @registry.tool()
    def tool() -> None:
        pass


registry.run()

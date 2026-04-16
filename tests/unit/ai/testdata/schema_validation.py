from splunklib.ai.registry import ToolRegistry

registry = ToolRegistry()


@registry.tool()
def input(foo: int) -> None:
    pass


registry.run()

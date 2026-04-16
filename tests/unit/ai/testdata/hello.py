from splunklib.ai.registry import ToolRegistry

registry = ToolRegistry()


@registry.tool()
def hello(name: str) -> str:
    """Hello returns a hello message"""
    return f"Hello {name}!"


registry.run()

from splunklib.ai.registry import ToolRegistry

registry = ToolRegistry()


@registry.tool(tags=["test_tag_1"])
def test_tool_1() -> None:
    return None


@registry.tool(tags=["test_tag_2"])
def test_tool_2() -> None:
    return None


@registry.tool(tags=["test_tag_1"])
def test_tool_3() -> None:
    return None


@registry.tool(tags=["test_tag_2"])
def test_tool_4() -> None:
    return None


registry.run()

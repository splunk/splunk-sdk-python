from collections.abc import Sequence

import pytest

from splunklib.ai.tool_filtering import ToolFilters, filter_tools
from splunklib.ai.tools import Tool, ToolResult, ToolType


async def no_op() -> ToolResult:
    return ToolResult(content=[], structured_content={})


TEST_TOOL_1 = Tool(
    name="test_tool_1",
    description="test_tool_1",
    func=no_op,
    tags=["test_tag_1"],
    input_schema={},
    type=ToolType.LOCAL,
)
TEST_TOOL_2 = Tool(
    name="test_tool_2",
    description="test_tool_2",
    func=no_op,
    tags=["test_tag_2"],
    input_schema={},
    type=ToolType.LOCAL,
)
TEST_TOOL_3 = Tool(
    name="test_tool_3",
    description="test_tool_3",
    func=no_op,
    tags=["test_tag_1"],
    input_schema={},
    type=ToolType.LOCAL,
)
TEST_TOOL_4 = Tool(
    name="test_tool_4",
    description="test_tool_4",
    func=no_op,
    tags=["test_tag_2"],
    input_schema={},
    type=ToolType.LOCAL,
)

TEST_TOOLS = [TEST_TOOL_1, TEST_TOOL_2, TEST_TOOL_3, TEST_TOOL_4]


@pytest.mark.parametrize(
    ("allowed_names", "allowed_tags", "initial_tools", "expected_tools"),
    [
        (["test_tool_1"], [], TEST_TOOLS, [TEST_TOOL_1]),
        ([], ["test_tag_2"], TEST_TOOLS, [TEST_TOOL_2, TEST_TOOL_4]),
        (
            ["test_tool_1"],
            ["test_tag_2"],
            TEST_TOOLS,
            [TEST_TOOL_1, TEST_TOOL_2, TEST_TOOL_4],
        ),
        (["test_tool_1"], ["test_tag_2"], [], []),
    ],
)
def test_filtering(
    allowed_names: Sequence[str],
    allowed_tags: Sequence[str],
    initial_tools: Sequence[Tool],
    expected_tools: Sequence[Tool],
) -> None:
    filters = ToolFilters(allowed_names, allowed_tags)
    filtered_tools = filter_tools(initial_tools, filters)

    assert filtered_tools == expected_tools

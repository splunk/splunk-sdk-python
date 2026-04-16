from collections.abc import Sequence

import pytest

from splunklib.ai.tool_settings import ToolAllowlist
from splunklib.ai.tools import Tool, ToolResult, ToolType


async def no_op() -> ToolResult:
    return ToolResult(content="", structured_content={})


LOCAL_TOOL_1 = Tool(
    name="test_tool_1",
    description="test_tool_1",
    func=no_op,
    tags=["test_tag_1"],
    input_schema={},
    type=ToolType.LOCAL,
)
LOCAL_TOOL_2 = Tool(
    name="test_tool_2",
    description="test_tool_2",
    func=no_op,
    tags=["test_tag_2"],
    input_schema={},
    type=ToolType.LOCAL,
)
LOCAL_TOOL_3 = Tool(
    name="test_tool_3",
    description="test_tool_3",
    func=no_op,
    tags=["test_tag_1"],
    input_schema={},
    type=ToolType.LOCAL,
)
LOCAL_TOOL_4 = Tool(
    name="test_tool_4",
    description="test_tool_4",
    func=no_op,
    tags=["test_tag_2"],
    input_schema={},
    type=ToolType.LOCAL,
)

LOCAL_TOOLS = [LOCAL_TOOL_1, LOCAL_TOOL_2, LOCAL_TOOL_3, LOCAL_TOOL_4]


@pytest.mark.parametrize(
    ("allowed_names", "allowed_tags", "initial_tools", "expected_tools"),
    [
        ([], [], [], []),
        (["test_tool_1"], [], LOCAL_TOOLS, [LOCAL_TOOL_1]),
        ([], ["test_tag_2"], LOCAL_TOOLS, [LOCAL_TOOL_2, LOCAL_TOOL_4]),
        (
            ["test_tool_1"],
            ["test_tag_2"],
            LOCAL_TOOLS,
            [LOCAL_TOOL_1, LOCAL_TOOL_2, LOCAL_TOOL_4],
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
    filters = ToolAllowlist(allowed_names, allowed_tags)
    filtered_tools = [t for t in initial_tools if filters.is_allowed(t)]

    assert filtered_tools == expected_tools


def test_filtering_custom_predicate_does_not_override_name_and_tag() -> None:
    allow_all = ToolAllowlist(custom_predicate=lambda _: True)
    assert [t for t in LOCAL_TOOLS if allow_all.is_allowed(t)] == LOCAL_TOOLS

    deny_all = ToolAllowlist(names=["test_tool_1"], custom_predicate=lambda _: False)
    assert [t for t in LOCAL_TOOLS if deny_all.is_allowed(t)] == [LOCAL_TOOL_1]


def test_filtering_empty_allowlist_blocks_everything() -> None:
    empty = ToolAllowlist()
    assert [t for t in LOCAL_TOOLS if empty.is_allowed(t)] == []

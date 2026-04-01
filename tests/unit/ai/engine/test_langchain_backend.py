# Copyright © 2011-2026 Splunk, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"): you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

# pyright: reportPrivateUsage=false

import unittest

import pytest
from langchain.messages import (
    AIMessage as LC_AIMessage,
    HumanMessage as LC_HumanMessage,
    SystemMessage as LC_SystemMessage,
    ToolCall as LC_ToolCall,
    ToolMessage as LC_ToolMessage,
)

from splunklib.ai.core.backend import InvalidMessageTypeError, InvalidModelError
from splunklib.ai.engines import langchain as lc
from splunklib.ai.messages import (
    AIMessage,
    HumanMessage,
    SubagentCall,
    SubagentFailureResult,
    SubagentMessage,
    SystemMessage,
    ToolCall,
    ToolFailureResult,
    ToolMessage,
    ToolResult,
)
from splunklib.ai.model import AnthropicModel, OpenAIModel, PredefinedModel
from splunklib.ai.tools import ToolType


class TestMapMessageFromLangchain(unittest.TestCase):
    def test_map_message_from_langchain_ai_with_tool_calls(self) -> None:
        tool_call = LC_ToolCall(name="lookup", args={"q": "test"}, id="tc-1")
        message = LC_AIMessage(content="done", tool_calls=[tool_call])

        mapped = lc._map_message_from_langchain(message)

        assert isinstance(mapped, AIMessage)
        assert mapped.content == "done"
        assert mapped.calls == [
            ToolCall(name="lookup", args={"q": "test"}, id="tc-1", type=ToolType.REMOTE)
        ]

    def test_map_message_from_langchain_ai_with_agent_call(self) -> None:
        tool_call = LC_ToolCall(
            name=f"{lc.AGENT_PREFIX}assistant", args={"args": {"q": "test"}}, id="tc-2"
        )
        message = LC_AIMessage(content="done", tool_calls=[tool_call])
        mapped = lc._map_message_from_langchain(message)

        assert isinstance(mapped, AIMessage)
        assert mapped.calls == [
            SubagentCall(
                name="assistant",
                args={"q": "test"},
                id="tc-2",
            )
        ]

    def test_map_message_from_langchain_ai_with_mixed_calls(self) -> None:
        tool_call = LC_ToolCall(name="lookup", args={"q": "test"}, id="tc-1")
        agent_call = LC_ToolCall(
            name=f"{lc.AGENT_PREFIX}assistant", args={"args": {"q": "test"}}, id="tc-2"
        )
        message = LC_AIMessage(content="done", tool_calls=[tool_call, agent_call])

        mapped = lc._map_message_from_langchain(message)

        assert isinstance(mapped, AIMessage)
        assert mapped.calls == [
            ToolCall(
                name="lookup", args={"q": "test"}, id="tc-1", type=ToolType.REMOTE
            ),
            SubagentCall(name="assistant", args={"q": "test"}, id="tc-2"),
        ]

    def test_map_message_from_langchain_human(self) -> None:
        message = LC_HumanMessage(content="hello")
        mapped = lc._map_message_from_langchain(message)

        assert isinstance(mapped, HumanMessage)
        assert mapped.content == "hello"

    def test_map_message_from_langchain_system(self) -> None:
        message = LC_SystemMessage(content="be helpful")
        mapped = lc._map_message_from_langchain(message)

        assert isinstance(mapped, SystemMessage)
        assert mapped.content == "be helpful"

    def test_map_message_from_langchain_tool(self) -> None:
        message = LC_ToolMessage(
            name="lookup",
            content="result",
            tool_call_id="call-1",
            status="error",
            artifact=ToolFailureResult("result"),
        )
        mapped = lc._map_message_from_langchain(message)

        assert isinstance(mapped, ToolMessage)
        assert mapped.name == "lookup"
        assert mapped.call_id == "call-1"
        assert isinstance(mapped.result, ToolFailureResult)
        assert mapped.result.error_message == "result"

    def test_map_message_from_langchain_subagent(self) -> None:
        message = LC_ToolMessage(
            name=f"{lc.AGENT_PREFIX}assistant",
            content="subagent output",
            tool_call_id="call-2",
            status="error",
            artifact=SubagentFailureResult("subagent output"),
        )
        mapped = lc._map_message_from_langchain(message)

        assert isinstance(mapped, SubagentMessage)
        assert mapped.name == "assistant"
        assert mapped.call_id == "call-2"
        assert isinstance(mapped.result, SubagentFailureResult)
        assert mapped.result.error_message == "subagent output"

    def test_map_message_from_langchain_invalid_raises(self) -> None:
        with pytest.raises(InvalidMessageTypeError):
            lc._map_message_from_langchain(object())  # pyright: ignore[reportArgumentType]


class MapMessageToLangchainTests(unittest.TestCase):
    def test_map_message_to_langchain_ai(self) -> None:
        message = AIMessage(
            content="hi",
            calls=[ToolCall(name="lookup", args={}, id="tc-1", type=ToolType.REMOTE)],
        )
        mapped = lc._map_message_to_langchain(message)

        assert isinstance(mapped, LC_AIMessage)
        assert mapped.content == "hi"
        assert mapped.tool_calls == [LC_ToolCall(name="lookup", args={}, id="tc-1")]

    def test_map_message_to_langchain_ai_with_agent_call(self) -> None:
        message = AIMessage(
            content="hi",
            calls=[
                SubagentCall(
                    name="assistant",
                    args={"q": "test"},
                    id="tc-2",
                )
            ],
        )
        mapped = lc._map_message_to_langchain(message)

        assert isinstance(mapped, LC_AIMessage)
        assert mapped.tool_calls == [
            LC_ToolCall(
                name=f"{lc.AGENT_PREFIX}assistant",
                args={"args": {"q": "test"}},
                id="tc-2",
            )
        ]

    def test_map_message_to_langchain_human(self) -> None:
        message = HumanMessage(content="hello")
        mapped = lc._map_message_to_langchain(message)

        assert isinstance(mapped, LC_HumanMessage)
        assert mapped.content == "hello"

    def test_map_message_to_langchain_tool_call_with_reserved_prefix(self) -> None:
        message = lc._map_message_to_langchain(
            AIMessage(
                content="hi",
                calls=[
                    ToolCall(
                        name=f"{lc.AGENT_PREFIX}bad-tool",
                        args={},
                        id="tc-1",
                        type=ToolType.REMOTE,
                    )
                ],
            )
        )
        assert isinstance(message, LC_AIMessage)
        assert message.tool_calls == [
            LC_ToolCall(name="__tool-__agent-bad-tool", args={}, id="tc-1")
        ]

        message = lc._map_message_to_langchain(
            AIMessage(
                content="hi",
                calls=[
                    ToolCall(
                        name="__bad-tool", args={}, id="tc-2", type=ToolType.REMOTE
                    )
                ],
            )
        )
        assert isinstance(message, LC_AIMessage)
        assert message.tool_calls == [
            LC_ToolCall(name="__tool-__bad-tool", args={}, id="tc-2")
        ]

        message = lc._map_message_to_langchain(
            ToolMessage(
                call_id="foo",
                name="__bad-tool",
                type=ToolType.REMOTE,
                result=ToolResult(content="foo", structured_content=None),
            )
        )
        assert isinstance(message, LC_ToolMessage)
        assert message.name == "__tool-__bad-tool"

    def test_map_message_from_langchain_tool_call_with_reserved_prefix(
        self,
    ) -> None:
        message = lc._map_message_from_langchain(
            LC_AIMessage(
                content="hi",
                tool_calls=[
                    LC_ToolCall(
                        name="__tool-__bad-tool",
                        args={},
                        id="tc-1",
                    )
                ],
            )
        )
        assert isinstance(message, AIMessage)
        assert len(message.calls) > 0
        assert message.calls[0].name == "__bad-tool"

        message = lc._map_message_from_langchain(
            message=LC_ToolMessage(
                name="__tool-__bad-tool",
                content="result",
                tool_call_id="call-1",
                status="success",
                artifact=ToolResult(content="result", structured_content=None),
            )
        )
        assert isinstance(message, ToolMessage)
        assert message.name == "__bad-tool"

    def test_map_message_to_langchain_agent_call_with_agent_prefix_raises(
        self,
    ) -> None:
        message = lc._map_message_to_langchain(
            AIMessage(
                content="hi",
                calls=[
                    SubagentCall(
                        name=f"{lc.AGENT_PREFIX}bad-agent",
                        args={},
                        id="tc-1",
                    )
                ],
            )
        )

        # Fine, but in practice a unnecessary prefix.
        assert isinstance(message, LC_AIMessage)
        assert message.tool_calls == [
            LC_ToolCall(name="__agent-__agent-bad-agent", args={"args": {}}, id="tc-1")
        ]

    def test_map_message_to_langchain_system(self) -> None:
        message = SystemMessage(content="be helpful")
        mapped = lc._map_message_to_langchain(message)

        assert isinstance(mapped, LC_SystemMessage)
        assert mapped.content == "be helpful"

    def test_map_message_to_langchain_tool(self) -> None:
        message = ToolMessage(
            name="lookup",
            call_id="call-1",
            type=ToolType.REMOTE,
            result=ToolFailureResult("result"),
        )
        mapped = lc._map_message_to_langchain(message)

        assert isinstance(mapped, LC_ToolMessage)
        assert mapped.content == "result"
        assert mapped.name == "lookup"
        assert mapped.tool_call_id == "call-1"
        assert mapped.status == "error"

    def test_map_message_to_langchain_subagent(self) -> None:
        message = SubagentMessage(
            name="My Agent", call_id="call-2", result=SubagentFailureResult("ping")
        )
        mapped = lc._map_message_to_langchain(message)

        assert isinstance(mapped, LC_ToolMessage)
        assert mapped.content == "ping"
        assert mapped.name == f"{lc.AGENT_PREFIX}My Agent"
        assert mapped.tool_call_id == "call-2"
        assert mapped.status == "error"

    def test_map_message_to_langchain_invalid_raises(self) -> None:
        with pytest.raises(InvalidMessageTypeError):
            lc._map_message_to_langchain(object())  # pyright: ignore[reportArgumentType]


class CreateLangchainModelTests(unittest.TestCase):
    def test_create_langchain_model_invalid_raises(self) -> None:
        with pytest.raises(InvalidModelError):
            lc._create_langchain_model(PredefinedModel(model="unknown"))

    def test_create_langchain_model_openai(self) -> None:
        pytest.importorskip("langchain_openai")
        import langchain_openai

        model = OpenAIModel(
            model="gpt-test",
            base_url="https://example.com",
            api_key="test-key",
            temperature=0.3,
        )
        result = lc._create_langchain_model(model)

        assert isinstance(result, langchain_openai.ChatOpenAI)
        assert result.model_name == model.model
        assert result.openai_api_base == model.base_url
        assert result.temperature == model.temperature

    def test_create_langchain_model_anthropic(self) -> None:
        pytest.importorskip("langchain_anthropic")
        import langchain_anthropic

        model = AnthropicModel(
            model="claude-3-5-sonnet-20241022",
            api_key="test-key",
            base_url="https://api.anthropic.com",
            temperature=0.3,
        )
        result = lc._create_langchain_model(model)

        assert isinstance(result, langchain_anthropic.ChatAnthropic)
        assert result.model == model.model
        assert result.temperature == model.temperature

    def test_create_langchain_model_anthropic_with_base_url(self) -> None:
        pytest.importorskip("langchain_anthropic")
        import langchain_anthropic

        model = AnthropicModel(
            model="claude-3-5-sonnet-20241022",
            api_key="test-key",
            base_url="http://localhost:11434",
            temperature=0.5,
        )
        result = lc._create_langchain_model(model)

        assert isinstance(result, langchain_anthropic.ChatAnthropic)
        assert result.model == model.model
        assert result.temperature == model.temperature
        # ChatAnthropic stores base_url in anthropic_api_url
        assert result.anthropic_api_url == model.base_url


@pytest.mark.parametrize(
    ("name", "tool_type", "expected_name"),
    [
        (
            f"{lc.RESERVED_LC_TOOL_PREFIX}test_tool",
            ToolType.REMOTE,
            f"{lc.CONFLICTING_TOOL_PREFIX}__test_tool",
        ),
        ("test_tool", ToolType.LOCAL, f"{lc.LOCAL_TOOL_PREFIX}test_tool"),
        (
            f"{lc.RESERVED_LC_TOOL_PREFIX}test_tool",
            ToolType.LOCAL,
            f"{lc.LOCAL_TOOL_PREFIX}{lc.RESERVED_LC_TOOL_PREFIX}test_tool",
        ),
    ],
)
def test_normalize_tool_name(
    name: str, tool_type: ToolType, expected_name: str
) -> None:
    got_name = lc._normalize_tool_name(name, tool_type)

    assert got_name == expected_name

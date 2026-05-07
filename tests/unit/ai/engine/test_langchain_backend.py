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
    OpaqueBlock,
    SubagentCall,
    SubagentFailureResult,
    SubagentMessage,
    SystemMessage,
    TextBlock,
    ToolCall,
    ToolFailureResult,
    ToolMessage,
    ToolResult,
)
from splunklib.ai.model import AnthropicModel, GoogleModel, OpenAIModel, PredefinedModel
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

    def test_map_message_from_langchain_ai_with_text_content_block(self) -> None:
        extras = (
            {
                # simulate gemini model returning thought signature in extra field of text content block
                "signature": "EjQKMgEMOdbHDmsQ+BTM6duYJ43i5npxkpn28Ir0VjD1p6w4fUqIdYszIcWx+XcqAW1a8E+Q"
            },
        )

        text_block = {
            "type": "text",
            "text": "test-content-block",
            "id": "some-id",
            "extras": extras,
        }
        message = LC_AIMessage(content=[text_block], tool_calls=[])

        mapped = lc._map_message_from_langchain(message)

        assert isinstance(mapped, AIMessage)
        assert isinstance(mapped.content[0], TextBlock)
        assert mapped.content[0].text == "test-content-block"
        assert mapped.content[0].id == "some-id"
        assert mapped.content[0].extras == extras

    def test_map_message_from_langchain_ai_with_text_content_block_without_id(
        self,
    ) -> None:
        extras = (
            {
                # simulate gemini model returning thought signature in extra field of text content block
                "signature": "EjQKMgEMOdbHDmsQ+BTM6duYJ43i5npxkpn28Ir0VjD1p6w4fUqIdYszIcWx+XcqAW1a8E+Q"
            },
        )

        text_block = {
            "type": "text",
            "text": "test-content-block",
            "extras": extras,
        }
        message = LC_AIMessage(content=[text_block], tool_calls=[])

        mapped = lc._map_message_from_langchain(message)

        assert isinstance(mapped, AIMessage)
        assert isinstance(mapped.content[0], TextBlock)
        assert mapped.content[0].text == "test-content-block"
        assert mapped.content[0].id is None
        assert mapped.content[0].extras == extras

    def test_map_message_from_langchain_ai_with_list_of_str(self) -> None:
        message = LC_AIMessage(content=["one", "two"], tool_calls=[])

        mapped = lc._map_message_from_langchain(message)

        assert isinstance(mapped, AIMessage)
        assert mapped.content == ["one", "two"]

    def test_map_message_from_langchain_ai_with_other_content_block(self) -> None:
        content_block = {
            "type": "image",
        }
        message = LC_AIMessage(content=[content_block], tool_calls=[])

        mapped = lc._map_message_from_langchain(message)

        assert isinstance(mapped, AIMessage)
        assert isinstance(mapped.content[0], OpaqueBlock)
        assert mapped.content[0]._data == content_block

    def test_map_message_from_langchain_ai_with_mixed_content(self) -> None:
        content_block = {
            "type": "image",
        }
        text_block = {
            "type": "text",
            "text": "test",
        }
        message = LC_AIMessage(content=[content_block, text_block, "test"], tool_calls=[])

        mapped = lc._map_message_from_langchain(message)

        assert isinstance(mapped, AIMessage)
        assert isinstance(mapped.content[0], OpaqueBlock)
        assert mapped.content[0]._data == content_block
        assert isinstance(mapped.content[1], TextBlock)
        assert mapped.content[1].text == "test"
        assert mapped.content[2] == "test"

    def test_map_message_from_langchain_ai_tool_call_with_additional_kwargs(
        self,
    ) -> None:
        tool_call = LC_ToolCall(
            name=f"__local-startup_time",
            args={"q": "test"},
            id="tc-2",
        )
        # simulate gemini models returning thought signature in additional kwargs
        # when calling tools.
        additional_kwargs = {
            "function_call": {"name": "__local-startup_time", "arguments": "{}"},
            "__gemini_function_call_thought_signatures__": {
                "28e28045-9846-4c9c-ab46-97f33bff5a9c": "EjQKMgEMOdbHH9gTl8BkX2uMM52753GCboanCcnUp9XB896IdThnG42GB8lRSkqGGxVbv5JY"
            },
        }
        message = LC_AIMessage(
            content="done", tool_calls=[tool_call], additional_kwargs=additional_kwargs
        )
        mapped = lc._map_message_from_langchain(message)
        assert isinstance(mapped, AIMessage)
        assert mapped.calls == [
            ToolCall(
                name="startup_time",
                args={"q": "test"},
                id="tc-2",
                type=ToolType.LOCAL,
            )
        ]
        assert mapped.extras == additional_kwargs

    def test_map_message_from_langchain_ai_with_agent_call(self) -> None:
        tool_call = LC_ToolCall(
            name=f"{lc.AGENT_PREFIX}assistant",
            args={"args": {"q": "test"}, "thread_id": None},
            id="tc-2",
            type="tool_call",
        )
        message = LC_AIMessage(content="done", tool_calls=[tool_call])
        mapped = lc._map_message_from_langchain(message)

        assert isinstance(mapped, AIMessage)
        assert mapped.calls == [
            SubagentCall(
                name="assistant",
                args={"q": "test"},
                id="tc-2",
                thread_id=None,
            )
        ]

    def test_map_message_from_langchain_ai_with_mixed_calls(self) -> None:
        tool_call = LC_ToolCall(name="lookup", args={"q": "test"}, id="tc-1", type="tool_call")
        agent_call = LC_ToolCall(
            name=f"{lc.AGENT_PREFIX}assistant",
            args={"args": {"q": "test"}, "thread_id": None},
            id="tc-2",
            type="tool_call",
        )
        message = LC_AIMessage(content="done", tool_calls=[tool_call, agent_call])

        mapped = lc._map_message_from_langchain(message)

        assert isinstance(mapped, AIMessage)
        assert mapped.calls == [
            ToolCall(name="lookup", args={"q": "test"}, id="tc-1", type=ToolType.REMOTE),
            SubagentCall(name="assistant", args={"q": "test"}, id="tc-2", thread_id=None),
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
            artifact=ToolFailureResult(error_message="result"),
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
            artifact=SubagentFailureResult(error_message="subagent output"),
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
        assert mapped.tool_calls == [
            LC_ToolCall(name="lookup", args={}, id="tc-1", type="tool_call")
        ]

    def test_map_message_to_langchain_ai_with_text_content_block(self) -> None:
        extras = {
            "signature": "EjQKMgEMOdbHDmsQ+BTM6duYJ43i5npxkpn28Ir0VjD1p6w4fUqIdYszIcWx+XcqAW1a8E+Q"
        }
        message = AIMessage(
            content=[
                TextBlock(
                    text="test-content-block",
                    extras=extras,
                    id="some-id",
                )
            ],
            calls=[],
        )
        mapped = lc._map_message_to_langchain(message)

        assert isinstance(mapped, LC_AIMessage)
        assert isinstance(mapped.content[0], dict)
        assert mapped.content[0]["type"] == "text"
        assert mapped.content[0]["text"] == "test-content-block"
        assert mapped.content[0]["id"] == "some-id"
        assert mapped.content[0]["extras"] == extras

    def test_map_message_to_langchain_ai_with_text_content_block_no_id(self) -> None:
        extras = {
            "signature": "EjQKMgEMOdbHDmsQ+BTM6duYJ43i5npxkpn28Ir0VjD1p6w4fUqIdYszIcWx+XcqAW1a8E+Q"
        }
        message = AIMessage(
            content=[
                TextBlock(
                    text="test-content-block",
                    extras=extras,
                )
            ],
            calls=[],
        )
        mapped = lc._map_message_to_langchain(message)

        assert isinstance(mapped, LC_AIMessage)
        assert isinstance(mapped.content[0], dict)
        assert mapped.content[0]["type"] == "text"
        assert mapped.content[0]["text"] == "test-content-block"
        assert mapped.content[0]["id"] is None
        assert mapped.content[0]["extras"] == extras

    def test_map_message_to_langchain_ai_with_list_of_str(self) -> None:
        message = AIMessage(
            content=["one", "two"],
            calls=[],
        )
        mapped = lc._map_message_to_langchain(message)

        assert isinstance(mapped, LC_AIMessage)
        assert mapped.content == ["one", "two"]

    def test_map_message_to_langchain_ai_with_opaque_content_block(self) -> None:
        some_data = {"type": "unsupported"}
        message = AIMessage(
            content=[OpaqueBlock(_data=some_data)],
            calls=[],
        )
        mapped = lc._map_message_to_langchain(message)

        assert isinstance(mapped, LC_AIMessage)
        assert isinstance(mapped.content[0], dict)
        assert mapped.content[0]["type"] == "unsupported"

    def test_map_message_to_langchain_ai_with_mixed_content_block(self) -> None:
        some_data = {"type": "unsupported"}
        message = AIMessage(
            content=[
                OpaqueBlock(_data=some_data),
                TextBlock(text="test-content-block"),
                "test",
            ],
            calls=[],
        )
        mapped = lc._map_message_to_langchain(message)

        assert isinstance(mapped, LC_AIMessage)
        assert isinstance(mapped.content[0], dict)
        assert mapped.content[0]["type"] == "unsupported"
        assert isinstance(mapped.content[1], dict)
        assert mapped.content[1]["type"] == "text"
        assert mapped.content[1]["text"] == "test-content-block"
        assert mapped.content[2] == "test"

    def test_map_message_to_langchain_ai_with_agent_call(self) -> None:
        message = AIMessage(
            content="hi",
            calls=[
                SubagentCall(
                    name="assistant",
                    args={"q": "test"},
                    id="tc-2",
                    thread_id=None,
                )
            ],
        )
        mapped = lc._map_message_to_langchain(message)

        assert isinstance(mapped, LC_AIMessage)
        assert mapped.tool_calls == [
            LC_ToolCall(
                name=f"{lc.AGENT_PREFIX}assistant",
                args={"args": {"q": "test"}, "thread_id": None},
                id="tc-2",
                type="tool_call",
            )
        ]

    def test_map_message_to_langchain_ai_with_tool_call_with_thought_signature(
        self,
    ) -> None:
        extras = {
            "function_call": {
                "name": "__local-startup_time",
                "arguments": '{"q": "test"}',
            },
            "__gemini_function_call_thought_signatures__": {
                "28e28045-9846-4c9c-ab46-97f33bff5a9c": "EjQKMgEMOdbHH9gTl8BkX2uMM52753GCboanCcnUp9XB896IdThnG42GB8lRSkqGGxVbv5JY"
            },
        }
        message = AIMessage(
            content="hi",
            calls=[
                ToolCall(
                    name="startup_time",
                    args={"q": "test"},
                    id="tc-2",
                    type=ToolType.LOCAL,
                )
            ],
            extras=extras,
        )
        mapped = lc._map_message_to_langchain(message)

        assert isinstance(mapped, LC_AIMessage)
        assert mapped.tool_calls == [
            LC_ToolCall(
                name=f"__local-startup_time",
                args={"q": "test"},
                id="tc-2",
                type="tool_call",
            )
        ]
        assert mapped.additional_kwargs == extras

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
            LC_ToolCall(name="__tool-__agent-bad-tool", args={}, id="tc-1", type="tool_call")
        ]

        message = lc._map_message_to_langchain(
            AIMessage(
                content="hi",
                calls=[ToolCall(name="__bad-tool", args={}, id="tc-2", type=ToolType.REMOTE)],
            )
        )
        assert isinstance(message, LC_AIMessage)
        assert message.tool_calls == [
            LC_ToolCall(name="__tool-__bad-tool", args={}, id="tc-2", type="tool_call")
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
                        thread_id=None,
                    )
                ],
            )
        )

        # Fine, but in practice a unnecessary prefix.
        assert isinstance(message, LC_AIMessage)
        assert message.tool_calls == [
            LC_ToolCall(
                name="__agent-__agent-bad-agent",
                args={"args": {}, "thread_id": None},
                id="tc-1",
                type="tool_call",
            )
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
            result=ToolFailureResult(error_message="result"),
        )
        mapped = lc._map_message_to_langchain(message)

        assert isinstance(mapped, LC_ToolMessage)
        assert mapped.content == "result"
        assert mapped.name == "lookup"
        assert mapped.tool_call_id == "call-1"
        assert mapped.status == "error"

    def test_map_message_to_langchain_subagent(self) -> None:
        message = SubagentMessage(
            name="My Agent",
            call_id="call-2",
            result=SubagentFailureResult(error_message="ping"),
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

    def test_create_langchain_model_google_gemini_api(self) -> None:
        pytest.importorskip("langchain_google_genai")
        import langchain_google_genai

        model = GoogleModel(model="gemini-2.0-flash", api_key="test-key")
        result = lc._create_langchain_model(model)

        assert isinstance(result, langchain_google_genai.ChatGoogleGenerativeAI)
        assert result.model == model.model
        assert result._use_vertexai is False  # pyright: ignore[reportAttributeAccessIssue]

    def test_create_langchain_model_google_vertex_ai_via_project(self) -> None:
        pytest.importorskip("langchain_google_genai")
        import langchain_google_genai

        model = GoogleModel(
            model="gemini-2.0-flash",
            api_key="test-key",
            project="my-project",
        )
        result = lc._create_langchain_model(model)

        assert isinstance(result, langchain_google_genai.ChatGoogleGenerativeAI)
        assert result.project == model.project
        assert result._use_vertexai is True  # pyright: ignore[reportAttributeAccessIssue]

    def test_create_langchain_model_google_vertex_ai_explicit_flag(self) -> None:
        pytest.importorskip("langchain_google_genai")
        import langchain_google_genai

        model = GoogleModel(
            model="gemini-2.0-flash",
            api_key="test-key",
            vertexai=True,
        )
        result = lc._create_langchain_model(model)

        assert isinstance(result, langchain_google_genai.ChatGoogleGenerativeAI)
        assert result._use_vertexai is True  # pyright: ignore[reportAttributeAccessIssue]

    def test_create_langchain_model_google_temperature(self) -> None:
        pytest.importorskip("langchain_google_genai")
        import langchain_google_genai

        model = GoogleModel(model="gemini-2.0-flash", api_key="test-key", temperature=0.5)
        result = lc._create_langchain_model(model)

        assert isinstance(result, langchain_google_genai.ChatGoogleGenerativeAI)
        assert result.temperature == model.temperature


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
def test_normalize_tool_name(name: str, tool_type: ToolType, expected_name: str) -> None:
    got_name = lc._normalize_tool_name(name, tool_type)

    assert got_name == expected_name

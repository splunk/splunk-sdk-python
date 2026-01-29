#
# Copyright © 2011-2025 Splunk, Inc.
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

import unittest

import pytest

from langchain.messages import (
    AIMessage as LC_AIMessage,
    HumanMessage as LC_HumanMessage,
    SystemMessage as LC_SystemMessage,
    ToolCall as LC_ToolCall,
    ToolMessage as LC_ToolMessage,
)

from splunklib.ai.core.backend import (
    InvalidMessageTypeError,
    InvalidModelError,
    InvalidToolNameError,
)
from splunklib.ai.engines import langchain as lc
from splunklib.ai.messages import (
    AIMessage,
    AgentCall,
    HumanMessage,
    SubagentMessage,
    SystemMessage,
    ToolCall,
    ToolMessage,
)
from splunklib.ai.model import OpenAIModel, PredefinedModel


class TestMapMessageFromLangchain(unittest.TestCase):
    def test_map_message_from_langchain_ai_with_tool_calls(self) -> None:
        tool_call = LC_ToolCall(name="lookup", args={"q": "test"}, id="tc-1")
        message = LC_AIMessage(content="done", tool_calls=[tool_call])

        mapped = lc._map_message_from_langchain(message)

        assert isinstance(mapped, AIMessage)
        assert mapped.content == "done"
        assert mapped.calls == [ToolCall(name="lookup", args={"q": "test"}, id="tc-1")]

    def test_map_message_from_langchain_ai_with_agent_call(self) -> None:
        tool_call = LC_ToolCall(
            name=f"{lc.AGENT_PREFIX}assistant", args={"q": "test"}, id="tc-2"
        )
        message = LC_AIMessage(content="done", tool_calls=[tool_call])

        mapped = lc._map_message_from_langchain(message)

        assert mapped.calls == [
            AgentCall(
                name="assistant",
                args={"q": "test"},
                id="tc-2",
            )
        ]

    def test_map_message_from_langchain_ai_with_mixed_calls(self) -> None:
        tool_call = LC_ToolCall(name="lookup", args={"q": "test"}, id="tc-1")
        agent_call = LC_ToolCall(
            name=f"{lc.AGENT_PREFIX}assistant", args={"q": "test"}, id="tc-2"
        )
        message = LC_AIMessage(content="done", tool_calls=[tool_call, agent_call])

        mapped = lc._map_message_from_langchain(message)

        assert mapped.calls == [
            ToolCall(name="lookup", args={"q": "test"}, id="tc-1"),
            AgentCall(
                name="assistant",
                args={"q": "test"},
                id="tc-2",
            ),
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
            name="lookup", content="result", tool_call_id="call-1", status="error"
        )
        mapped = lc._map_message_from_langchain(message)

        assert isinstance(mapped, ToolMessage)
        assert mapped.name == "lookup"
        assert mapped.content == "result"
        assert mapped.call_id == "call-1"
        assert mapped.status == "error"

    def test_map_message_from_langchain_subagent(self) -> None:
        message = LC_ToolMessage(
            name=f"{lc.AGENT_PREFIX}assistant",
            content="subagent output",
            tool_call_id="call-2",
            status="error",
        )
        mapped = lc._map_message_from_langchain(message)

        assert isinstance(mapped, SubagentMessage)
        assert mapped.name == "assistant"
        assert mapped.content == "subagent output"
        assert mapped.call_id == "call-2"
        assert mapped.status == "error"

    def test_map_message_from_langchain_invalid_raises(self) -> None:
        with pytest.raises(InvalidMessageTypeError):
            lc._map_message_from_langchain(object())


class MapMessageToLangchainTests(unittest.TestCase):
    def test_map_message_to_langchain_ai(self) -> None:
        message = AIMessage(
            content="hi", calls=[ToolCall(name="lookup", args={}, id="tc-1")]
        )
        mapped = lc._map_message_to_langchain(message)

        assert isinstance(mapped, LC_AIMessage)
        assert mapped.content == "hi"
        assert mapped.tool_calls == [LC_ToolCall(name="lookup", args={}, id="tc-1")]

    def test_map_message_to_langchain_ai_with_agent_call(self) -> None:
        message = AIMessage(
            content="hi",
            calls=[AgentCall(name="assistant", args={"q": "test"}, id="tc-2")],
        )
        mapped = lc._map_message_to_langchain(message)

        assert isinstance(mapped, LC_AIMessage)
        assert mapped.tool_calls == [
            LC_ToolCall(
                name=f"{lc.AGENT_PREFIX}assistant", args={"q": "test"}, id="tc-2"
            )
        ]

    def test_map_message_to_langchain_tool_call_with_agent_prefix_raises(
        self,
    ) -> None:
        message = AIMessage(
            content="hi",
            calls=[ToolCall(name=f"{lc.AGENT_PREFIX}bad-tool", args={}, id="tc-3")],
        )

        with pytest.raises(InvalidToolNameError):
            lc._map_message_to_langchain(message)

    def test_map_message_to_langchain_agent_call_with_agent_prefix_raises(
        self,
    ) -> None:
        message = AIMessage(
            content="hi",
            calls=[
                AgentCall(
                    name=f"{lc.AGENT_PREFIX}bad-agent", args={"q": "test"}, id="tc-4"
                )
            ],
        )

        with pytest.raises(InvalidToolNameError):
            lc._map_message_to_langchain(message)

    def test_map_message_to_langchain_human(self) -> None:
        message = HumanMessage(content="hello")
        mapped = lc._map_message_to_langchain(message)

        assert isinstance(mapped, LC_HumanMessage)
        assert mapped.content == "hello"

    def test_map_message_to_langchain_system(self) -> None:
        message = SystemMessage(content="be helpful")
        mapped = lc._map_message_to_langchain(message)

        assert isinstance(mapped, LC_SystemMessage)
        assert mapped.content == "be helpful"

    def test_map_message_to_langchain_tool(self) -> None:
        message = ToolMessage(
            name="lookup", content="result", call_id="call-1", status="error"
        )
        mapped = lc._map_message_to_langchain(message)

        assert isinstance(mapped, LC_ToolMessage)
        assert mapped.content == "result"
        assert mapped.name == "lookup"
        assert mapped.tool_call_id == "call-1"
        assert mapped.status == "error"

    def test_map_message_to_langchain_subagent(self) -> None:
        message = SubagentMessage(
            name="My Agent", content="ping", call_id="call-2", status="error"
        )
        mapped = lc._map_message_to_langchain(message)

        assert isinstance(mapped, LC_ToolMessage)
        assert mapped.content == "ping"
        assert mapped.name == f"{lc.AGENT_PREFIX}My-Agent"
        assert mapped.tool_call_id == "call-2"
        assert mapped.status == "error"

    def test_map_message_to_langchain_invalid_raises(self) -> None:
        with pytest.raises(InvalidMessageTypeError):
            lc._map_message_to_langchain(object())


class CreateLangchainModelTests(unittest.TestCase):
    def test_create_langchain_model_invalid_raises(self) -> None:
        with pytest.raises(InvalidModelError):
            lc._create_langchain_model(PredefinedModel(model="unknown"))

    def test_create_langchain_model_openai(self) -> None:
        langchain_openai = pytest.importorskip("langchain_openai")
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


if __name__ == "__main__":
    unittest.main()

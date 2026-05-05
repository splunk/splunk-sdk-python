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

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any, override

import pytest

from splunklib.ai import Agent
from splunklib.ai.conversation_store import ConversationStore
from splunklib.ai.messages import (
    AgentResponse,
    AIMessage,
    BaseMessage,
    HumanMessage,
    StructuredOutputCall,
    StructuredOutputMessage,
    SubagentCall,
    SubagentMessage,
    SubagentTextResult,
    SystemMessage,
    ToolCall,
    ToolMessage,
    ToolResult,
)
from splunklib.ai.middleware import (
    AgentMiddleware,
    AgentMiddlewareHandler,
    AgentRequest,
    ModelMiddlewareHandler,
    ModelRequest,
    ModelResponse,
    agent_middleware,
    model_middleware,
)
from splunklib.ai.tools import ToolType
from tests.ai_testlib import AITestCase, ai_snapshot_test


@model_middleware
async def noop_model(
    _request: ModelRequest,
    _handler: ModelMiddlewareHandler,
) -> ModelResponse:
    return ModelResponse(message=AIMessage(content="", calls=[]))


@dataclass
class MockStore(ConversationStore):
    msgs: Sequence[BaseMessage]

    @override
    async def get_messages(self, thread_id: str) -> Sequence[BaseMessage]:
        return self.msgs

    @override
    async def store_messages(self, thread_id: str, messages: list[BaseMessage]) -> None:
        pass


class TestMessageValidation(AITestCase):
    @ai_snapshot_test()
    async def test_message_validation_invoke(self) -> None:
        pytest.importorskip("langchain_openai")

        class _Alien(BaseMessage):
            role: str = "alien"

        class _AlienAIMessage(AIMessage):
            pass

        class _AlienToolCall(ToolCall):
            pass

        class _AlienSubagentCall(SubagentCall):
            pass

        class _AlienStructuredOutputCall(StructuredOutputCall):
            pass

        cases: list[tuple[list[BaseMessage], str]] = [
            ([], "messages list is empty"),
            (
                [
                    HumanMessage(content="hello"),
                    AIMessage(
                        content="",
                        calls=[
                            ToolCall(
                                name="my_tool", args={}, id="id-1", type=ToolType.LOCAL
                            )
                        ],
                    ),
                ],
                "ToolCall does not have a corresponding ToolMessage; ids=\\['id-1'\\]",
            ),
            (
                [
                    HumanMessage(content="hello"),
                    AIMessage(
                        content="",
                        calls=[
                            SubagentCall(
                                name="my_agent", args={}, id="id-1", thread_id=None
                            )
                        ],
                    ),
                ],
                "SubagentCall does not have a corresponding SubagentMessage; ids=\\['id-1'\\]",
            ),
            (
                [
                    HumanMessage(content="hello"),
                    AIMessage(
                        content="",
                        calls=[],
                        structured_output_calls=[
                            StructuredOutputCall(name="my_schema", args={}, id="id-1")
                        ],
                    ),
                ],
                "StructuredToolCall does not have a corresponding StructuredOutputMessage; ids=\\['id-1'\\]",
            ),
            (
                [
                    HumanMessage(content="hello"),
                    AIMessage(
                        content="",
                        calls=[
                            ToolCall(
                                name="my_tool", args={}, id="id-1", type=ToolType.LOCAL
                            )
                        ],
                    ),
                    HumanMessage(content="hello"),
                ],
                "ToolCall does not have a corresponding ToolMessage; ids=\\['id-1'\\]",
            ),
            (
                [
                    HumanMessage(content="hello"),
                    AIMessage(
                        content="",
                        calls=[
                            SubagentCall(
                                name="my_agent", args={}, id="id-1", thread_id=None
                            )
                        ],
                    ),
                    HumanMessage(content="hello"),
                ],
                "SubagentCall does not have a corresponding SubagentMessage; ids=\\['id-1'\\]",
            ),
            (
                [
                    HumanMessage(content="hello"),
                    AIMessage(
                        content="",
                        calls=[],
                        structured_output_calls=[
                            StructuredOutputCall(name="my_schema", args={}, id="id-1")
                        ],
                    ),
                    HumanMessage(content="hello"),
                ],
                "StructuredToolCall does not have a corresponding StructuredOutputMessage; ids=\\['id-1'\\]",
            ),
            (
                [
                    HumanMessage(content="hello"),
                    AIMessage(content="done", calls=[]),
                    ToolMessage(
                        name="ghost",
                        type=ToolType.LOCAL,
                        call_id="no-such-id",
                        result=ToolResult(content="x", structured_content=None),
                    ),
                ],
                "ToolMessage does not have a corresponding ToolCall",
            ),
            (
                [
                    HumanMessage(content="hello"),
                    AIMessage(content="done", calls=[]),
                    SubagentMessage(
                        name="ghost",
                        call_id="no-such-id",
                        result=SubagentTextResult(content="x"),
                    ),
                ],
                "SubagentMessage does not have a corresponding SubagentCall",
            ),
            (
                [
                    HumanMessage(content="hello"),
                    AIMessage(content="done", calls=[]),
                    StructuredOutputMessage(
                        call_id="no-such-id",
                        name="ghost",
                        status="success",
                        content="{}",
                    ),
                ],
                "StructuredOutputMessage does not have a corresponding StructuredOutputCall",
            ),
            (
                [
                    HumanMessage(content="hello"),
                    AIMessage(content="done", calls=[]),
                    ToolMessage(
                        name="ghost",
                        type=ToolType.LOCAL,
                        call_id="no-such-id",
                        result=ToolResult(content="x", structured_content=None),
                    ),
                    HumanMessage(content="hello"),
                ],
                "ToolMessage does not have a corresponding ToolCall",
            ),
            (
                [
                    HumanMessage(content="hello"),
                    AIMessage(content="done", calls=[]),
                    SubagentMessage(
                        name="ghost",
                        call_id="no-such-id",
                        result=SubagentTextResult(content="x"),
                    ),
                    HumanMessage(content="hello"),
                ],
                "SubagentMessage does not have a corresponding SubagentCall",
            ),
            (
                [
                    HumanMessage(content="hello"),
                    AIMessage(content="done", calls=[]),
                    StructuredOutputMessage(
                        call_id="no-such-id",
                        name="ghost",
                        status="success",
                        content="{}",
                    ),
                    HumanMessage(content="hello"),
                ],
                "StructuredOutputMessage does not have a corresponding StructuredOutputCall",
            ),
            (
                [
                    HumanMessage(content="hello"),
                    AIMessage(
                        content="",
                        calls=[
                            ToolCall(
                                name="my_tool", args={}, id="id-1", type=ToolType.LOCAL
                            )
                        ],
                    ),
                    ToolMessage(
                        name="wrong",
                        type=ToolType.LOCAL,
                        call_id="id-1",
                        result=ToolResult(content="x", structured_content=None),
                    ),
                    AIMessage(content="done", calls=[]),
                ],
                "ToolMessage.name = wrong, but the corresponding ToolCall.name = my_tool",
            ),
            (
                [
                    HumanMessage(content="hello"),
                    AIMessage(
                        content="",
                        calls=[
                            SubagentCall(
                                name="my_agent", args={}, id="id-1", thread_id=None
                            )
                        ],
                    ),
                    SubagentMessage(
                        name="wrong",
                        call_id="id-1",
                        result=SubagentTextResult(content="x"),
                    ),
                    AIMessage(content="done", calls=[]),
                ],
                "SubagentMessage.name = wrong, but the corresponding SubagentCall.name = my_agent",
            ),
            (
                [
                    HumanMessage(content="hello"),
                    AIMessage(
                        content="",
                        calls=[],
                        structured_output_calls=[
                            StructuredOutputCall(name="my_schema", args={}, id="id-1")
                        ],
                    ),
                    StructuredOutputMessage(
                        call_id="id-1", name="wrong", status="success", content="{}"
                    ),
                    AIMessage(content="done", calls=[]),
                ],
                "StructuredOutputMessage.name = wrong, but the corresponding StructuredOutputCall.name = my_schema",
            ),
            (
                [
                    HumanMessage(content="hello"),
                    AIMessage(
                        content="",
                        calls=[
                            ToolCall(name="t1", args={}, id="dup", type=ToolType.LOCAL),
                            ToolCall(name="t2", args={}, id="dup", type=ToolType.LOCAL),
                        ],
                    ),
                ],
                "Duplicated tool call_id: dup",
            ),
            (
                [
                    HumanMessage(content="hello"),
                    AIMessage(
                        content="",
                        calls=[
                            SubagentCall(name="a1", args={}, id="dup", thread_id=None),
                            SubagentCall(name="a2", args={}, id="dup", thread_id=None),
                        ],
                    ),
                ],
                "Duplicated subagent call_id: dup",
            ),
            (
                [
                    HumanMessage(content="hello"),
                    AIMessage(
                        content="",
                        calls=[],
                        structured_output_calls=[
                            StructuredOutputCall(name="s1", args={}, id="dup"),
                            StructuredOutputCall(name="s2", args={}, id="dup"),
                        ],
                    ),
                ],
                "Duplicated structured output tool call_id: dup",
            ),
            (
                [
                    HumanMessage(content="hello"),
                    AIMessage(
                        content="",
                        calls=[
                            ToolCall(
                                name="t", args={}, id="shared", type=ToolType.LOCAL
                            ),
                            SubagentCall(
                                name="a", args={}, id="shared", thread_id=None
                            ),
                        ],
                    ),
                ],
                "Duplicated subagent call_id: shared",
            ),
            (
                [
                    HumanMessage(content="hello"),
                    AIMessage(
                        content="",
                        calls=[ToolCall(name="t", args={}, id="", type=ToolType.LOCAL)],
                    ),
                ],
                "Empty tool call_id",
            ),
            (
                [
                    HumanMessage(content="hello"),
                    AIMessage(
                        content="",
                        calls=[SubagentCall(name="a", args={}, id="", thread_id=None)],
                    ),
                ],
                "Empty subagent call_id",
            ),
            (
                [
                    HumanMessage(content="hello"),
                    AIMessage(
                        content="",
                        calls=[],
                        structured_output_calls=[
                            StructuredOutputCall(name="s", args={}, id="")
                        ],
                    ),
                ],
                "Empty structured output tool call_id",
            ),
            (
                [
                    HumanMessage(content="hello"),
                    AIMessage(
                        content="",
                        calls=[
                            ToolCall(name="", args={}, id="id-x", type=ToolType.LOCAL)
                        ],
                    ),
                ],
                "Empty tool name",
            ),
            (
                [
                    HumanMessage(content="hello"),
                    AIMessage(
                        content="",
                        calls=[
                            SubagentCall(name="", args={}, id="id-x", thread_id=None)
                        ],
                    ),
                ],
                "Empty subagent name",
            ),
            (
                [
                    HumanMessage(content="hello"),
                    AIMessage(
                        content="",
                        calls=[],
                        structured_output_calls=[
                            StructuredOutputCall(name="", args={}, id="id-x")
                        ],
                    ),
                ],
                "Empty structured output tool name",
            ),
            ([_Alien()], "Messages contains invalid message type"),
            (
                [_AlienAIMessage(content="", calls=[])],
                "Messages contains invalid message type",
            ),
            (
                [
                    SystemMessage(content="Follow rules."),
                    HumanMessage(content="hello"),
                    AIMessage(
                        content="",
                        calls=[
                            _AlienToolCall(
                                name="my_tool", args={}, id="id-1", type=ToolType.LOCAL
                            )
                        ],
                    ),
                ],
                "AIMessage contains invalid call type",
            ),
            (
                [
                    SystemMessage(content="Follow rules."),
                    HumanMessage(content="hello"),
                    AIMessage(
                        content="",
                        calls=[
                            _AlienSubagentCall(
                                name="my_agent", args={}, id="id-1", thread_id=None
                            )
                        ],
                    ),
                ],
                "AIMessage contains invalid call type",
            ),
            (
                [
                    SystemMessage(content="Follow rules."),
                    HumanMessage(content="hello"),
                    AIMessage(
                        content="",
                        calls=[],
                        structured_output_calls=[
                            _AlienStructuredOutputCall(
                                name="my_schema", args={}, id="id-1"
                            )
                        ],
                    ),
                ],
                "AIMessage contains invalid call type",
            ),
            (
                [
                    HumanMessage(content="hello"),
                    AIMessage(
                        content="",
                        calls=[
                            SubagentCall(
                                name="my_agent",
                                args={},
                                id="id-1",
                                thread_id="",
                            )
                        ],
                    ),
                    SubagentMessage(
                        name="my_agent",
                        call_id="id-1",
                        result=SubagentTextResult(content="foo"),
                    ),
                ],
                "thread_id should not be an empty string",
            ),
        ]

        async with Agent(
            model=(await self.model()),
            system_prompt="test",
            service=self.service,
            middleware=[noop_model],
        ) as agent:
            for messages, exception in cases:
                with self.subTest(messages=messages, exception=exception):
                    with pytest.raises(Exception, match=exception):
                        await agent.invoke(messages)

        async with Agent(
            model=(await self.model()),
            system_prompt="test",
            service=self.service,
            middleware=[noop_model],
        ) as agent:
            for messages, exception in cases:
                with self.subTest(messages=messages, exception=exception):
                    with pytest.raises(Exception, match=exception):
                        await agent.invoke(messages)

        store = MockStore([])

        async with Agent(
            model=(await self.model()),
            system_prompt="test",
            service=self.service,
            middleware=[noop_model],
            conversation_store=store,
        ) as agent:
            for messages, exception in cases:
                if len(messages) == 0:
                    continue

                with self.subTest(messages=messages, exception=exception):
                    store.msgs = messages
                    with pytest.raises(Exception, match=exception):
                        await agent.invoke(messages=[HumanMessage(content="")])

    @ai_snapshot_test()
    async def test_message_validation_store_with_invoke(self) -> None:
        pytest.importorskip("langchain_openai")

        # Since conversation store should contain a previously valid messages list from previous
        # invocation of the agent loop, the validator logic should treat them separately.

        store = MockStore(
            [
                HumanMessage(content="hello"),
                AIMessage(
                    content="",
                    calls=[
                        ToolCall(
                            name="my_tool", args={}, id="id-1", type=ToolType.LOCAL
                        )
                    ],
                ),
            ],
        )

        async with Agent(
            model=(await self.model()),
            system_prompt="test",
            service=self.service,
            middleware=[noop_model],
            conversation_store=store,
        ) as agent:
            messages: list[BaseMessage] = [
                ToolMessage(
                    call_id="id-1",
                    name="my_tool",
                    type=ToolType.LOCAL,
                    result=ToolResult(content="", structured_content={}),
                ),
                HumanMessage(content=""),
            ]
            with pytest.raises(
                Exception, match="ToolCall does not have a corresponding ToolMessage"
            ):
                await agent.invoke(messages=messages)

    @ai_snapshot_test()
    async def test_message_validation_agent_middleware_modifies_messages(self) -> None:
        pytest.importorskip("langchain_openai")

        @agent_middleware
        async def no_ai_message(
            request: AgentRequest,
            handler: AgentMiddlewareHandler,
        ) -> AgentResponse[Any]:
            await handler(request)
            return AgentResponse(
                structured_output=None,
                messages=[HumanMessage(content="only human")],
            )

        @agent_middleware
        async def ai_message_with_calls(
            request: AgentRequest,
            handler: AgentMiddlewareHandler,
        ) -> AgentResponse[Any]:
            await handler(request)
            return AgentResponse(
                structured_output=None,
                messages=[
                    HumanMessage(content="hello"),
                    AIMessage(
                        content="",
                        calls=[
                            ToolCall(name="t", args={}, id="id-1", type=ToolType.LOCAL)
                        ],
                    ),
                    ToolMessage(
                        name="t",
                        type=ToolType.LOCAL,
                        call_id="id-1",
                        result=ToolResult(content="result", structured_content=None),
                    ),
                ],
            )

        @agent_middleware
        async def tool_call_without_response(
            request: AgentRequest,
            handler: AgentMiddlewareHandler,
        ) -> AgentResponse[Any]:
            await handler(request)
            return AgentResponse(
                structured_output=None,
                messages=[
                    HumanMessage(content="hello"),
                    AIMessage(
                        content="",
                        calls=[
                            ToolCall(name="t", args={}, id="id-1", type=ToolType.LOCAL)
                        ],
                    ),
                    AIMessage(content="done", calls=[]),
                ],
            )

        cases: list[tuple[AgentMiddleware, str]] = [
            (
                no_ai_message,
                "Agent middleware modified messages and made it invalid: messages does not have an AIMessage",
            ),
            (
                ai_message_with_calls,
                "Agent middleware modified messages and made it invalid: last AIMessage has tool calls",
            ),
            (
                tool_call_without_response,
                "Agent middleware modified messages and made it invalid: ToolCall does not have a corresponding ToolMessage; ids=\\['id-1'\\]",
            ),
        ]

        for middleware, exception in cases:
            with self.subTest(exception=exception):
                async with Agent(
                    model=(await self.model()),
                    system_prompt="test",
                    service=self.service,
                    middleware=[noop_model, middleware],
                ) as agent:
                    with pytest.raises(Exception, match=exception):
                        await agent.invoke([HumanMessage(content="hello")])

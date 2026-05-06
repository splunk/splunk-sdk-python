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

import unittest
from time import monotonic

from splunklib.ai.agent import Agent
from splunklib.ai.limits import (
    DEFAULT_STEP_LIMIT,
    DEFAULT_TIMEOUT_SECONDS,
    DEFAULT_TOKEN_LIMIT,
    StepLimitMiddleware,
    StepsLimitExceededException,
    TimeoutExceededException,
    TimeoutLimitMiddleware,
    TokenLimitExceededException,
    TokenLimitMiddleware,
)
from splunklib.ai.messages import AIMessage, AgentResponse
from splunklib.ai.middleware import AgentMiddleware, AgentRequest, AgentState, ModelRequest, ModelResponse
from splunklib.ai.model import OpenAIModel
from splunklib.client import Service


def _make_agent(middleware: list[AgentMiddleware] | None = None) -> Agent:  # type: ignore[type-arg]
    return Agent(
        system_prompt="test",
        model=OpenAIModel(model="gpt-4o", base_url="http://localhost", api_key="test"),
        service=Service(host="localhost", port=8089, token="test"),
        middleware=middleware,
    )


def _make_agent_request() -> AgentRequest:
    return AgentRequest(messages=[], thread_id="foo")


def _make_model_request(token_count: int = 0, total_steps: int = 0) -> ModelRequest:
    state = AgentState(
        messages=[],
        total_steps=total_steps,
        token_count=token_count,
        thread_id="foo",
    )
    return ModelRequest(system_message="", state=state)


class TestDefaultLimitsInjection(unittest.TestCase):
    def test_all_defaults_injected_when_no_middleware(self) -> None:
        agent = _make_agent()
        mw = list(agent.middleware or [])
        assert any(isinstance(m, TokenLimitMiddleware) for m in mw)
        assert any(isinstance(m, StepLimitMiddleware) for m in mw)
        assert any(isinstance(m, TimeoutLimitMiddleware) for m in mw)

    def test_default_values_match_constants(self) -> None:
        agent = _make_agent()
        mw = list(agent.middleware or [])
        token = next(m for m in mw if isinstance(m, TokenLimitMiddleware))
        step = next(m for m in mw if isinstance(m, StepLimitMiddleware))
        timeout = next(m for m in mw if isinstance(m, TimeoutLimitMiddleware))
        assert token._limit == DEFAULT_TOKEN_LIMIT  # pyright: ignore[reportPrivateUsage]
        assert step._limit == DEFAULT_STEP_LIMIT  # pyright: ignore[reportPrivateUsage]
        assert timeout._seconds == DEFAULT_TIMEOUT_SECONDS  # pyright: ignore[reportPrivateUsage]

    def test_user_token_limit_suppresses_default(self) -> None:
        agent = _make_agent(middleware=[TokenLimitMiddleware(50_000)])
        mw = list(agent.middleware or [])
        token_mws = [m for m in mw if isinstance(m, TokenLimitMiddleware)]
        assert len(token_mws) == 1
        assert token_mws[0]._limit == 50_000  # pyright: ignore[reportPrivateUsage]
        assert any(isinstance(m, StepLimitMiddleware) for m in mw)
        assert any(isinstance(m, TimeoutLimitMiddleware) for m in mw)

    def test_user_step_limit_suppresses_default(self) -> None:
        agent = _make_agent(middleware=[StepLimitMiddleware(10)])
        mw = list(agent.middleware or [])
        step_mws = [m for m in mw if isinstance(m, StepLimitMiddleware)]
        assert len(step_mws) == 1
        assert step_mws[0]._limit == 10  # pyright: ignore[reportPrivateUsage]
        assert any(isinstance(m, TokenLimitMiddleware) for m in mw)
        assert any(isinstance(m, TimeoutLimitMiddleware) for m in mw)

    def test_user_timeout_limit_suppresses_default(self) -> None:
        agent = _make_agent(middleware=[TimeoutLimitMiddleware(30.0)])
        mw = list(agent.middleware or [])
        timeout_mws = [m for m in mw if isinstance(m, TimeoutLimitMiddleware)]
        assert len(timeout_mws) == 1
        assert timeout_mws[0]._seconds == 30.0  # pyright: ignore[reportPrivateUsage]
        assert any(isinstance(m, TokenLimitMiddleware) for m in mw)
        assert any(isinstance(m, StepLimitMiddleware) for m in mw)

    def test_all_user_limits_suppress_all_defaults(self) -> None:
        agent = _make_agent(
            middleware=[TokenLimitMiddleware(50_000), StepLimitMiddleware(10), TimeoutLimitMiddleware(30.0)]
        )
        mw = list(agent.middleware or [])
        assert len([m for m in mw if isinstance(m, TokenLimitMiddleware)]) == 1
        assert len([m for m in mw if isinstance(m, StepLimitMiddleware)]) == 1
        assert len([m for m in mw if isinstance(m, TimeoutLimitMiddleware)]) == 1


async def _noop_model_handler(_request: ModelRequest) -> ModelResponse:
    return ModelResponse(message=AIMessage(content="", calls=[]))


class TestTimeoutLimitMiddleware(unittest.IsolatedAsyncioTestCase):
    async def test_deadline_reset_on_each_invoke(self) -> None:
        mw = TimeoutLimitMiddleware(60.0)
        request = _make_agent_request()

        first_deadline: float | None = None
        second_deadline: float | None = None

        async def _first_agent_handler(_request: AgentRequest) -> AgentResponse[None]:
            nonlocal first_deadline
            first_deadline = mw._deadline_per_thread_id["foo"]  # pyright: ignore[reportPrivateUsage]
            return AgentResponse(messages=[], structured_output=None)

        async def _second_agent_handler(_request: AgentRequest) -> AgentResponse[None]:
            nonlocal second_deadline
            second_deadline = mw._deadline_per_thread_id["foo"]  # pyright: ignore[reportPrivateUsage]
            return AgentResponse(messages=[], structured_output=None)

        await mw.agent_middleware(request, _first_agent_handler)
        await mw.agent_middleware(request, _second_agent_handler)

        assert first_deadline is not None
        assert second_deadline is not None  # pyright: ignore[reportUnreachable]
        assert second_deadline >= first_deadline

    async def test_deadline_is_none_before_first_invoke(self) -> None:
        mw = TimeoutLimitMiddleware(60.0)
        assert mw._deadline_per_thread_id.get("foo") is None  # pyright: ignore[reportPrivateUsage]

    async def test_timeout_fires_when_deadline_exceeded(self) -> None:
        mw = TimeoutLimitMiddleware(60.0)
        mw._deadline_per_thread_id["foo"] = monotonic() - 1.0  # pyright: ignore[reportPrivateUsage]  # already in the past

        state = AgentState(messages=[], total_steps=0, token_count=0, thread_id="foo")
        request = ModelRequest(system_message="", state=state)

        with self.assertRaises(TimeoutExceededException):
            await mw.model_middleware(request, _noop_model_handler)


class TestTokenLimitMiddleware(unittest.IsolatedAsyncioTestCase):
    async def test_raises_when_token_count_in_request_exceeds_limit(self) -> None:
        mw = TokenLimitMiddleware(200)

        await mw.model_middleware(_make_model_request(token_count=100), _noop_model_handler)
        await mw.model_middleware(_make_model_request(token_count=199), _noop_model_handler)
        with self.assertRaises(TokenLimitExceededException):
            await mw.model_middleware(_make_model_request(token_count=200), _noop_model_handler)


class TestStepLimitMiddleware(unittest.IsolatedAsyncioTestCase):
    async def test_raises_when_steps_in_request_reach_limit(self) -> None:
        mw = StepLimitMiddleware(3)

        await mw.model_middleware(_make_model_request(total_steps=1), _noop_model_handler)
        await mw.model_middleware(_make_model_request(total_steps=2), _noop_model_handler)
        with self.assertRaises(StepsLimitExceededException):
            await mw.model_middleware(_make_model_request(total_steps=3), _noop_model_handler)

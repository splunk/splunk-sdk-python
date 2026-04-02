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

import os
from collections.abc import AsyncGenerator, Sequence
from contextlib import AbstractAsyncContextManager, AsyncExitStack, asynccontextmanager
from logging import Logger
from typing import Any, Self, final, override
from uuid import uuid4

from pydantic import BaseModel

from splunklib.ai.base_agent import BaseAgent
from splunklib.ai.conversation_store import ConversationStore
from splunklib.ai.core.backend import AgentImpl
from splunklib.ai.core.backend_registry import get_backend
from splunklib.ai.messages import AgentResponse, BaseMessage, HumanMessage, OutputT
from splunklib.ai.middleware import AgentMiddleware
from splunklib.ai.model import PredefinedModel
from splunklib.ai.security import create_structured_prompt
from splunklib.ai.tool_filtering import ToolFilters, filter_tools
from splunklib.ai.tools import (
    Tool,
    ToolType,
    build_local_tools_path,
    connect_local_mcp,
    connect_remote_mcp,
    load_mcp_tools,
    locate_app,
)
from splunklib.client import Service

# For testing purposes, overrides the automatically inferred tools.py path.
_testing_local_tools_path: str | None = None
_testing_app_id: str | None = None


@final
class Agent(BaseAgent[OutputT]):
    """
    Core entry point for interacting with LLMs in the Agentic Splunk SDK.

    Agents are async context managers and must be used with `async with`:

        async with Agent(
            model=model,
            system_prompt="You are a helpful Splunk assistant.",
            service=service,
        ) as agent:
            result = await agent.invoke([...])

    Args:
        model:
            The underlying LLM to use. Must be a `PredefinedModel` instance
            (for example, `OpenAIModel`).

        system_prompt:
            The system message used to prime and control the agent behavior.

        service:
            A `Service` instance, that is the authenticated to the Splunk service.

        use_mcp_tools:
            If `True`, the agent will load and expose MCP tools to the model.
            This includes:
              * Remote tools provided by the Splunk MCP Server App.
              * Local tools registered via `ToolRegistry` in `bin/tools.py`.

            When enabled, the model can decide when and how to call tools
            as part of its reasoning. Defaults to `False`.

        tool_filters:
            Optional `ToolFilters` instance used to restrict which tools are
            exposed to the model when MCP tools are enabled.

        agents:
            Optional list of subagents available to this agent.

        output_schema:
            Optional Pydantic model type describing the structured output this
            agent should return. If `None`, the agent returns free-form text only.

        input_schema:
            Optional Pydantic model type describing the structured input this
            agent accepts. Currently this is only honored when the agent is
            used as a *subagent*. The supervisor agent uses this schema to
            understand how to call the subagent and how to format its inputs.

        name:
            Name of the agent when used as a subagent. This is
            surfaced to the supervisor and used to decide whether this agent
            is appropriate for a given task. Ignored for top-level agents.

        description:
            Description of the agent when used as a subagent. This is
            surfaced to the supervisor and used to decide whether this agent
            is appropriate for a given task. Ignored for top-level agents.

        logger:
            Optional logger instance used for tracing and debugging the agent's execution.
            Additionally logs from the local tools are forwarded to this logger.

        conversation_store:
            Optional `ConversationStore` instance used to persist conversation history
            across multiple `invoke` calls. When provided, the agent automatically loads
            prior messages for the active thread before each invocation and saves the
            full updated history afterwards.

            Use the built-in `InMemoryStore` for in-process persistence, or implement
            `ConversationStore` to back history with an external store.

            Without a store, each `invoke` call is stateless and the agent has no memory
            of previous turns.

        thread_id:
            Identifies the conversation thread used when reading from and writing to the
            `conversation_store`. Each unique `thread_id` maintains a separate history,
            so different users or sessions can share one store without interference.

            If omitted, a random ID is generated automatically. The `thread_id` can
            also be overridden per-call by passing it directly to `invoke`.

            Never invoke an Agent using the same thread_id more than once concurrently
            while using the same conversation_store.
    """

    _impl: AgentImpl[OutputT] | None
    _use_mcp_tools: bool
    _service: Service
    _tool_filters: ToolFilters | None
    _agent_context_manager: AbstractAsyncContextManager[Self] | None = None

    def __init__(
        self,
        model: PredefinedModel,
        system_prompt: str,
        service: Service,
        use_mcp_tools: bool = False,  # TODO: should we default to True?
        tool_filters: ToolFilters | None = None,
        agents: Sequence[BaseAgent[BaseModel | None]] | None = None,
        output_schema: type[OutputT] | None = None,
        input_schema: type[BaseModel] | None = None,  # Only used by Subagents
        middleware: Sequence[AgentMiddleware] | None = None,
        name: str = "",  # Only used by Subagents
        description: str = "",  # Only used by Subagents
        logger: Logger | None = None,
        conversation_store: ConversationStore | None = None,
        thread_id: str | None = None,
    ) -> None:
        super().__init__(
            model=model,
            system_prompt=system_prompt,
            name=name,
            description=description,
            tools=None,
            agents=agents,
            input_schema=input_schema,
            output_schema=output_schema,
            middleware=middleware,
            logger=logger,
            conversation_store=conversation_store,
            thread_id=thread_id if thread_id is not None else str(uuid4()),
        )

        self._use_mcp_tools = use_mcp_tools
        self._tool_filters = tool_filters
        self._service = service
        self._impl = None

    @asynccontextmanager
    async def _start_agent(self) -> AsyncGenerator[Self]:
        async with AsyncExitStack() as stack:
            assert self._impl is None, (
                "internal error: _impl was not set to None after agent invocation"
            )

            if self.name:
                self.logger.debug(
                    f"Creating agent {self.name}; trace_id={self.trace_id}"
                )
            else:
                self.logger.debug(f"Creating agent; trace_id={self.trace_id}")

            if self._use_mcp_tools:
                tools: list[Tool] = []

                self.logger.debug("Local tool registry detected")
                local_tools_path, app_id = _local_tools_path()
                if local_tools_path:
                    local_session = await stack.enter_async_context(
                        connect_local_mcp(local_tools_path, self.logger)
                    )
                    self.logger.debug("Loading local tools")
                    local_tools = await load_mcp_tools(
                        local_session,
                        ToolType.LOCAL,
                        app_id,
                        self.trace_id,
                        self._service,
                    )
                    self.logger.debug(f"Local tools loaded; {local_tools=}")
                    tools.extend(local_tools)

                self.logger.debug("Probing MCP Server App availability")
                remote_session = await stack.enter_async_context(
                    connect_remote_mcp(
                        self._service,
                        app_id,
                        self.trace_id,
                    )
                )
                if remote_session:
                    self.logger.debug("Loading remote tools - MCP Server available")
                    remote_tools = await load_mcp_tools(
                        remote_session,
                        ToolType.REMOTE,
                        app_id,
                        self.trace_id,
                        self._service,
                    )
                    self.logger.debug(f"Remote tools loaded; {remote_tools=}")
                    tools.extend(remote_tools)

                if self._tool_filters:
                    tools = filter_tools(tools, self._tool_filters)

                self.logger.debug(
                    f"Tools loaded & filtered successfully; tools_after_filtering={[tool.name for tool in tools]}"
                )

                self._tools = tools

            backend = get_backend()
            self._impl = await backend.create_agent(self)

            if self.name:
                self.logger.debug(
                    f"Agent {self.name} created; trace_id={self.trace_id}"
                )
            else:
                self.logger.debug(f"Agent created; trace_id={self.trace_id}")

            yield self

            self._impl = None

    async def __aenter__(self) -> Self:
        if self._agent_context_manager:
            raise AssertionError("Agent is already in `async with` context")
        self._agent_context_manager = self._start_agent()
        return await self._agent_context_manager.__aenter__()

    async def __aexit__(
        self, exc_type: ..., exc_value: ..., traceback: ...
    ) -> bool | None:
        assert self._agent_context_manager is not None
        result = await self._agent_context_manager.__aexit__(
            exc_type,
            exc_value,
            traceback,
        )
        self._agent_context_manager = None
        return result

    # TODO: for now we have a thread_id as an optional param, should
    # we wrap it in a dataclass? Might help with future-proofing the API??
    @override
    async def invoke(
        self, messages: list[BaseMessage], thread_id: str | None = None
    ) -> AgentResponse[OutputT]:
        """Invokes the agent with a list of messages.

        Use this for multi-message or role-based conversations.
        When passing external data (log entries, alert payloads, API responses, etc.)
        inside a HumanMessage, use `create_structured_prompt` to reduce the risk of
        prompt injection, or use `invoke_with_data` instead.
        """
        if not self._impl:
            raise AssertionError("Agent must be used inside 'async with'")

        if thread_id is None:
            thread_id = self._thread_id

        return await self._impl.invoke(messages, thread_id)

    async def invoke_with_data(
        self,
        instructions: str,
        data: str | dict[str, Any],
        thread_id: str | None = None,
    ) -> AgentResponse[OutputT]:
        """Invokes the agent with external data that may come from untrusted sources.

        Use instead of `invoke` when passing external data (log entries, alert payloads,
        API responses, etc.) to reduce the risk of prompt injection.
        """
        return await self.invoke(
            [HumanMessage(content=create_structured_prompt(instructions, data))],
            thread_id=thread_id,
        )


def _local_tools_path() -> tuple[str | None, str]:
    local_tools_path = _testing_local_tools_path
    app_id = _testing_app_id

    if local_tools_path is None:
        app_id, app_dir = locate_app()
        local_tools_path = build_local_tools_path(app_dir)

    assert app_id is not None, (
        "_load_tools_from_mcp was mocked, but _testing_app_id not"
    )

    if not os.path.exists(local_tools_path):
        local_tools_path = None

    return local_tools_path, app_id

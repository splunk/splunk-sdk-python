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

import os
from collections.abc import Sequence
from typing import Self, final, override

from pydantic import BaseModel

from splunklib.ai.base_agent import BaseAgent
from splunklib.ai.core.backend import AgentImpl
from splunklib.ai.core.backend_registry import get_backend
from splunklib.ai.hooks import AgentHook
from splunklib.ai.messages import AgentResponse, BaseMessage, OutputT
from splunklib.ai.model import PredefinedModel
from splunklib.ai.tool_filtering import ToolFilters, filter_tools
from splunklib.ai.tools import Tool, build_local_tools_path, load_mcp_tools, locate_app
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

        hooks:
            Optional sequence of `AgentHook`. Hooks are user-defined callback
            functions that can be registered to execute at specific points
            during the agent's operation.

        name:
            Name of the agent when used as a subagent. This is
            surfaced to the supervisor and used to decide whether this agent
            is appropriate for a given task. Ignored for top-level agents.

        description:
            Description of the agent when used as a subagent. This is
            surfaced to the supervisor and used to decide whether this agent
            is appropriate for a given task. Ignored for top-level agents.
    """

    _impl: AgentImpl[OutputT] | None
    _use_mcp_tools: bool
    _service: Service
    _tool_filters: ToolFilters | None

    # TODO: We should have a logger inside of an agent, debugging and such.

    def __init__(
        self,
        model: PredefinedModel,
        system_prompt: str,
        service: Service,
        use_mcp_tools: bool = False,  # TODO: should we default to True?
        tool_filters: ToolFilters | None = None,
        agents: Sequence[BaseAgent[BaseModel | None]] | None = None,
        output_schema: type[OutputT] | None = None,
        input_schema: type[BaseModel] | None = None,  # Only used by Subgents
        hooks: Sequence[AgentHook] | None = None,
        name: str = "",  # Only used by Subgents
        description: str = "",  # Only used by Subagents
    ) -> None:
        super().__init__(
            model=model,
            system_prompt=system_prompt,
            name=name,
            description=description,
            agents=agents,
            input_schema=input_schema,
            output_schema=output_schema,
            hooks=hooks,
        )

        if duplicate_hook_names := _find_duplicate_hook_names(self.hooks):
            raise ValueError(f"Duplicate hook names found: {duplicate_hook_names!r}")

        self._use_mcp_tools = use_mcp_tools
        self._tool_filters = tool_filters
        self._service = service
        self._impl = None

    async def __aenter__(self) -> Self:
        if self._impl:
            raise AssertionError("Agent is already in `async with` context")

        if self._use_mcp_tools:
            self._tools = await _load_tools_from_mcp(
                self._service, self._tool_filters, self.trace_id
            )

        backend = get_backend()
        self._impl = await backend.create_agent(self)

        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:  # noqa: ANN001  # pyright: ignore[reportUnknownParameterType, reportMissingParameterType]
        self._impl = None  # Make sure invoke fails if called after exit.
        return None

    @override
    async def invoke(self, messages: list[BaseMessage]) -> AgentResponse[OutputT]:
        if not self._impl:
            raise AssertionError("Agent must be used inside 'async with'")

        return await self._impl.invoke(messages)


async def _load_tools_from_mcp(
    service: Service,
    filters: ToolFilters | None,
    trace_id: str,
) -> list[Tool]:
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

    mcp_tools = await load_mcp_tools(service, local_tools_path, app_id, trace_id)
    if filters:
        return filter_tools(mcp_tools, filters)

    return mcp_tools


def _find_duplicate_hook_names(hooks: Sequence[AgentHook] | None) -> set[str]:
    seen: set[str] = set()
    duplicates: set[str] = set()

    if not hooks:
        return set()

    for hook in hooks:
        if hook.name in seen:
            duplicates.add(hook.name)
        else:
            seen.add(hook.name)

    return duplicates

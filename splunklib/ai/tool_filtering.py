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

from splunklib.ai.tools import Tool


@dataclass(frozen=True)
class ToolFilters:
    """Allowlists by which Tools are filtered."""

    allowed_names: Sequence[str] | None = None
    allowed_tags: Sequence[str] | None = None


def _is_allowed(tool: Tool, filters: ToolFilters) -> bool:
    return (
        tool.name in (filters.allowed_names or [])
        or len(set(filters.allowed_tags or []).intersection(tool.tags or [])) > 0
    )


def filter_tools(tools: Sequence[Tool], filters: ToolFilters) -> list[Tool]:
    """Filters all tools by allowlists provided by user to the Agent."""

    filtered_tools = [t for t in tools if _is_allowed(t, filters)]
    return filtered_tools

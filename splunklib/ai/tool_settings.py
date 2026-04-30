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

from collections.abc import Callable, Sequence
from dataclasses import dataclass, field

from splunklib.ai.tools import ToolMetadata


@dataclass(frozen=True, kw_only=True)
class ToolAllowlist:
    """Holds tool names and tags allowed to be used by Agents.

    NOTE: Names and tags take precedence over custom predicates.
    """

    names: Sequence[str] = field(default_factory=list[str])
    tags: Sequence[str] = field(default_factory=list[str])
    custom_predicate: Callable[[ToolMetadata], bool] | None = None

    # TODO: Support for remote tag filtering when MCP Server App starts responding with that data
    # remote_tags: Sequence[str] = []

    def is_allowed(self, tool: ToolMetadata) -> bool:
        is_allowed_by_name = tool.name in self.names
        is_allowed_by_tag = len(set(self.tags).intersection(tool.tags)) > 0
        if is_allowed_by_name or is_allowed_by_tag:
            return True

        return self.custom_predicate(tool) if self.custom_predicate else False


@dataclass(frozen=True, kw_only=True)
class RemoteToolSettings:
    allowlist: ToolAllowlist


@dataclass(frozen=True, kw_only=True)
class LocalToolSettings:
    allowlist: ToolAllowlist


@dataclass(frozen=True, kw_only=True)
class ToolSettings:
    local: LocalToolSettings | bool
    """Controls local tool loading (via ``bin/tools.py``).

    - ``False``: local tools are not loaded.
    - ``True``: all local tools are loaded without filtering.
    - ``LocalToolSettings(allowlist=...)``: local tools are loaded and filtered
      by the ToolAllowlist.
    """

    remote: RemoteToolSettings | None
    """Controls remote tool loading (HTTP MCP from the Splunk MCP Server App).

    - ``None`` (default): remote tools are not loaded.
    - ``RemoteToolSettings(allowlist=...)``: remote tools are loaded and filtered
      by the ToolAllowlist. Requires the Splunk MCP Server App to
      be installed and configured properly.
    """

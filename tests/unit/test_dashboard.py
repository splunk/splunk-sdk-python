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

from unittest.mock import MagicMock, patch

import pytest

from splunklib.client import (
    PATH_DASHBOARDS,
    Collection,
    Dashboard,
    Dashboards,
    Entity,
)


class TestDashboard:
    def test_is_entity_subclass(self) -> None:
        assert issubclass(Dashboard, Entity)

    def test_path_constant(self) -> None:
        assert PATH_DASHBOARDS == "data/ui/views/"

    def test_export_returns_eai_data(self) -> None:
        dashboard = MagicMock(spec=Dashboard)
        dashboard.content = {"eai:data": "<dashboard><label>Test</label></dashboard>"}
        assert Dashboard.export(dashboard) == "<dashboard><label>Test</label></dashboard>"

    def test_export_returns_empty_when_missing(self) -> None:
        dashboard = MagicMock(spec=Dashboard)
        dashboard.content = {}
        assert Dashboard.export(dashboard) == ""


class TestDashboards:
    def test_is_collection_subclass(self) -> None:
        assert issubclass(Dashboards, Collection)

    @patch.object(Collection, "create")
    def test_create_passes_xml_as_eai_data(self, mock_create: MagicMock) -> None:
        dashboards = Dashboards.__new__(Dashboards)
        xml = "<dashboard><label>Test</label></dashboard>"
        Dashboards.create(dashboards, "test_dash", xml)
        mock_create.assert_called_once_with(dashboards, "test_dash", **{"eai:data": xml})

    def test_create_raises_on_missing_xml(self) -> None:
        dashboards = Dashboards.__new__(Dashboards)
        with pytest.raises(TypeError):
            Dashboards.create(dashboards, "test_dash")  # pyright: ignore[reportCallIssue]

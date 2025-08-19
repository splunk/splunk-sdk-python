#!/usr/bin/env python
#
# Copyright © 2011-2024 Splunk, Inc.
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

from tests import testlib
from splunklib import results


@pytest.mark.smoke
class TestEventingApp(testlib.SDKTestCase):
    app_name = "eventing_app"

    def test_metadata(self):
        self.assertTrue(
            TestEventingApp.app_name in self.service.apps,
            msg=f"{TestEventingApp.app_name} is not installed.",
        )

        # Fetch the app
        app = self.service.apps[TestEventingApp.app_name]
        app.refresh()

        # Extract app info
        access = app.access
        content = app.content
        state = app.state

        # App info assertions
        self.assertEqual(state.title, TestEventingApp.app_name)

        self.assertEqual(access.app, "system")
        self.assertEqual(access.can_change_perms, "1")
        self.assertEqual(access.can_list, "1")
        self.assertEqual(access.can_share_app, "1")
        self.assertEqual(access.can_share_global, "1")
        self.assertEqual(access.can_share_user, "0")
        self.assertEqual(access.can_write, "1")
        self.assertEqual(access.modifiable, "1")
        self.assertEqual(access.owner, "nobody")
        self.assertEqual(access.sharing, "app")
        self.assertEqual(access.perms.read, ["*"])
        self.assertEqual(access.perms.write, ["admin", "power"])
        self.assertEqual(access.removable, "0")

        self.assertEqual(content.author, "Splunk")
        self.assertEqual(content.configured, "0")
        self.assertEqual(content.description, "Eventing custom search commands example")
        self.assertEqual(content.label, "Eventing App")
        self.assertEqual(content.version, "1.0.0")
        self.assertEqual(content.visible, "1")

    def test_behavior(self):
        makeresults_count = 20
        expected_results_count = 10
        expected_status = "200"

        search_query = f"""
        | makeresults count={makeresults_count}
        | streamstats count as row_num
        | eval status=case(
            (row_num % 2) == 1, 200,
            1=1, 500
        )
        | eventingcsc status={expected_status}
        """
        stream = self.service.jobs.oneshot(search_query, output_mode="json")

        results_reader = results.JSONResultsReader(stream)
        items = list(results_reader)

        self.assertFalse(results_reader.is_preview)

        # filter out informational messages and keep only search results
        actual_results = [
            item for item in items if not isinstance(item, results.Message)
        ]

        self.assertTrue(len(actual_results) == expected_results_count)

        for res in actual_results:
            self.assertIn("status", res)
            self.assertEqual(res["status"], expected_status)


@pytest.mark.smoke
class TestGeneratingApp(testlib.SDKTestCase):
    app_name = "generating_app"

    def test_metadata(self):
        self.assertTrue(
            TestGeneratingApp.app_name in self.service.apps,
            msg=f"{TestGeneratingApp.app_name} is not installed.",
        )

        # Fetch the app
        app = self.service.apps[TestGeneratingApp.app_name]
        app.refresh()

        # Extract app info
        access = app.access
        content = app.content
        state = app.state

        # App info assertions
        self.assertEqual(state.title, TestGeneratingApp.app_name)

        self.assertEqual(access.app, "system")
        self.assertEqual(access.can_change_perms, "1")
        self.assertEqual(access.can_list, "1")
        self.assertEqual(access.can_share_app, "1")
        self.assertEqual(access.can_share_global, "1")
        self.assertEqual(access.can_share_user, "0")
        self.assertEqual(access.can_write, "1")
        self.assertEqual(access.modifiable, "1")
        self.assertEqual(access.owner, "nobody")
        self.assertEqual(access.sharing, "app")
        self.assertEqual(access.perms.read, ["*"])
        self.assertEqual(access.perms.write, ["admin", "power"])
        self.assertEqual(access.removable, "0")

        self.assertEqual(content.author, "Splunk")
        self.assertEqual(content.configured, "0")
        self.assertEqual(
            content.description, "Generating custom search commands example"
        )
        self.assertEqual(content.label, "Generating App")
        self.assertEqual(content.version, "1.0.0")
        self.assertEqual(content.visible, "1")

    def test_behavior(self):
        stream = self.service.jobs.oneshot(
            "| generatingcsc count=4", output_mode="json"
        )
        result = results.JSONResultsReader(stream)
        ds = list(result)
        self.assertTrue(len(ds) == 4)


@pytest.mark.smoke
class TestReportingApp(testlib.SDKTestCase):
    app_name = "reporting_app"

    def test_metadata(self):
        self.assertTrue(
            TestReportingApp.app_name in self.service.apps,
            msg=f"{TestReportingApp.app_name} is not installed.",
        )

        # Fetch the app
        app = self.service.apps[TestReportingApp.app_name]
        app.refresh()

        # Extract app info
        access = app.access
        content = app.content
        state = app.state

        # App info assertions
        self.assertEqual(state.title, TestReportingApp.app_name)

        self.assertEqual(access.app, "system")
        self.assertEqual(access.can_change_perms, "1")
        self.assertEqual(access.can_list, "1")
        self.assertEqual(access.can_share_app, "1")
        self.assertEqual(access.can_share_global, "1")
        self.assertEqual(access.can_share_user, "0")
        self.assertEqual(access.can_write, "1")
        self.assertEqual(access.modifiable, "1")
        self.assertEqual(access.owner, "nobody")
        self.assertEqual(access.sharing, "app")
        self.assertEqual(access.perms.read, ["*"])
        self.assertEqual(access.perms.write, ["admin", "power"])
        self.assertEqual(access.removable, "0")

        self.assertEqual(content.author, "Splunk")
        self.assertEqual(content.configured, "0")
        self.assertEqual(
            content.description, "Reporting custom search commands example"
        )
        self.assertEqual(content.label, "Reporting App")
        self.assertEqual(content.version, "1.0.0")
        self.assertEqual(content.visible, "1")

    def test_behavior_all_entries_above_cutoff(self):
        jobs = self.service.jobs

        stream = jobs.oneshot(
            "| makeresults count=10 | eval math=100, eng=100, cs=100 | reportingcsc cutoff=150 math eng cs",
            output_mode="json",
        )
        result = results.JSONResultsReader(stream)
        ds = list(result)

        self.assertTrue(len(ds) > 0)
        self.assertTrue(ds[0].values() is not None)
        self.assertTrue(len(ds[0].values()) > 0)

        no_of_students = int(list(ds[0].values())[0])
        self.assertTrue(no_of_students == 10)

    def test_behavior_all_entries_below_cutoff(self):
        stream = self.service.jobs.oneshot(
            "| makeresults count=10 | eval math=45, eng=45, cs=45 | reportingcsc cutoff=150 math eng cs",
            output_mode="json",
        )
        result = results.JSONResultsReader(stream)
        ds = list(result)

        self.assertTrue(len(ds) > 0)
        self.assertTrue(ds[0].values() is not None)
        self.assertTrue(len(ds[0].values()) > 0)

        no_of_students = int(list(ds[0].values())[0])
        self.assertTrue(no_of_students == 0)


@pytest.mark.smoke
class TestStreamingApp(testlib.SDKTestCase):
    app_name = "streaming_app"

    def test_metadata(self):
        self.assertTrue(
            TestStreamingApp.app_name in self.service.apps,
            msg=f"{TestStreamingApp.app_name} is not installed.",
        )

        # Fetch the app
        app = self.service.apps[TestStreamingApp.app_name]
        app.refresh()

        # Extract app info
        access = app.access
        content = app.content
        state = app.state

        # App info assertions
        self.assertEqual(state.title, TestStreamingApp.app_name)

        self.assertEqual(access.app, "system")
        self.assertEqual(access.can_change_perms, "1")
        self.assertEqual(access.can_list, "1")
        self.assertEqual(access.can_share_app, "1")
        self.assertEqual(access.can_share_global, "1")
        self.assertEqual(access.can_share_user, "0")
        self.assertEqual(access.can_write, "1")
        self.assertEqual(access.modifiable, "1")
        self.assertEqual(access.owner, "nobody")
        self.assertEqual(access.sharing, "app")
        self.assertEqual(access.perms.read, ["*"])
        self.assertEqual(access.perms.write, ["admin", "power"])
        self.assertEqual(access.removable, "0")

        self.assertEqual(content.author, "Splunk")
        self.assertEqual(content.configured, "0")
        self.assertEqual(
            content.description, "Streaming custom search commands example"
        )
        self.assertEqual(content.label, "Streaming App")
        self.assertEqual(content.version, "1.0.0")
        self.assertEqual(content.visible, "1")

    def test_behavior(self):
        stream = self.service.jobs.oneshot(
            "| makeresults count=5 | eval celsius = 35 | streamingcsc",
            output_mode="json",
        )
        result = results.JSONResultsReader(stream)
        ds = list(result)

        self.assertTrue(len(ds) == 5)
        self.assertTrue("_time" in ds[0])
        self.assertTrue("celsius" in ds[0])
        self.assertTrue("fahrenheit" in ds[0])
        self.assertTrue(ds[0]["celsius"] == "35")
        self.assertTrue(ds[0]["fahrenheit"] == "95.0")
        self.assertTrue(len(ds) == 5)


if __name__ == "__main__":
    unittest.main()

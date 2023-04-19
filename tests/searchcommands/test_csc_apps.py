#!/usr/bin/env python
#
# Copyright 2011-2015 Splunk, Inc.
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
class TestCSC(testlib.SDKTestCase):

    def test_eventing_app(self):
        app_name = "eventing_app"

        self.assertTrue(app_name in self.service.apps, msg="%s is not installed." % app_name)

        # Fetch the app
        app = self.service.apps[app_name]
        app.refresh()

        # Extract app info
        access = app.access
        content = app.content
        state = app.state

        # App info assertions
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
        self.assertEqual(access.perms.read, ['*'])
        self.assertEqual(access.perms.write, ['admin', 'power'])
        self.assertEqual(access.removable, "0")

        self.assertEqual(content.author, "Splunk")
        self.assertEqual(content.configured, "0")
        self.assertEqual(content.description, "Eventing custom search commands example")
        self.assertEqual(content.label, "Eventing App")
        self.assertEqual(content.version, "1.0.0")
        self.assertEqual(content.visible, "1")

        self.assertEqual(state.title, "eventing_app")

        jobs = self.service.jobs
        stream = jobs.oneshot('search index="_internal" | head 4000 | eventingcsc status=200 | head 10',
                              output_mode='json')
        result = results.JSONResultsReader(stream)
        ds = list(result)

        self.assertEqual(result.is_preview, False)
        self.assertTrue(isinstance(ds[0], (dict, results.Message)))
        nonmessages = [d for d in ds if isinstance(d, dict)]
        self.assertTrue(len(nonmessages) <= 10)

    def test_generating_app(self):
        app_name = "generating_app"

        self.assertTrue(app_name in self.service.apps, msg="%s is not installed." % app_name)

        # Fetch the app
        app = self.service.apps[app_name]
        app.refresh()

        # Extract app info
        access = app.access
        content = app.content
        state = app.state

        # App info assertions
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
        self.assertEqual(access.perms.read, ['*'])
        self.assertEqual(access.perms.write, ['admin', 'power'])
        self.assertEqual(access.removable, "0")

        self.assertEqual(content.author, "Splunk")
        self.assertEqual(content.configured, "0")
        self.assertEqual(content.description, "Generating custom search commands example")
        self.assertEqual(content.label, "Generating App")
        self.assertEqual(content.version, "1.0.0")
        self.assertEqual(content.visible, "1")

        self.assertEqual(state.title, "generating_app")

        jobs = self.service.jobs
        stream = jobs.oneshot('| generatingcsc count=4', output_mode='json')
        result = results.JSONResultsReader(stream)
        ds = list(result)
        self.assertTrue(len(ds) == 4)

    def test_reporting_app(self):
        app_name = "reporting_app"

        self.assertTrue(app_name in self.service.apps, msg="%s is not installed." % app_name)

        # Fetch the app
        app = self.service.apps[app_name]
        app.refresh()

        # Extract app info
        access = app.access
        content = app.content
        state = app.state

        # App info assertions
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
        self.assertEqual(access.perms.read, ['*'])
        self.assertEqual(access.perms.write, ['admin', 'power'])
        self.assertEqual(access.removable, "0")

        self.assertEqual(content.author, "Splunk")
        self.assertEqual(content.configured, "0")
        self.assertEqual(content.description, "Reporting custom search commands example")
        self.assertEqual(content.label, "Reporting App")
        self.assertEqual(content.version, "1.0.0")
        self.assertEqual(content.visible, "1")

        self.assertEqual(state.title, "reporting_app")

        jobs = self.service.jobs

        # All above 150
        stream = jobs.oneshot(
            '| makeresults count=10 | eval math=100, eng=100, cs=100 | reportingcsc cutoff=150 math eng cs',
            output_mode='json')
        result = results.JSONResultsReader(stream)
        ds = list(result)

        self.assertTrue(len(ds) > 0)
        self.assertTrue(ds[0].values() is not None)
        self.assertTrue(len(ds[0].values()) > 0)

        no_of_students = int(list(ds[0].values())[0])
        self.assertTrue(no_of_students == 10)

        # All below 150
        stream = jobs.oneshot(
            '| makeresults count=10 | eval math=45, eng=45, cs=45 | reportingcsc cutoff=150 math eng cs',
            output_mode='json')
        result = results.JSONResultsReader(stream)
        ds = list(result)

        self.assertTrue(len(ds) > 0)
        self.assertTrue(ds[0].values() is not None)
        self.assertTrue(len(ds[0].values()) > 0)

        no_of_students = int(list(ds[0].values())[0])
        self.assertTrue(no_of_students == 0)

    def test_streaming_app(self):
        app_name = "streaming_app"

        self.assertTrue(app_name in self.service.apps, msg="%s is not installed." % app_name)

        # Fetch the app
        app = self.service.apps[app_name]
        app.refresh()

        # Extract app info
        access = app.access
        content = app.content
        state = app.state

        # App info assertions
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
        self.assertEqual(access.perms.read, ['*'])
        self.assertEqual(access.perms.write, ['admin', 'power'])
        self.assertEqual(access.removable, "0")

        self.assertEqual(content.author, "Splunk")
        self.assertEqual(content.configured, "0")
        self.assertEqual(content.description, "Streaming custom search commands example")
        self.assertEqual(content.label, "Streaming App")
        self.assertEqual(content.version, "1.0.0")
        self.assertEqual(content.visible, "1")

        self.assertEqual(state.title, "streaming_app")

        jobs = self.service.jobs

        stream = jobs.oneshot('| makeresults count=5 | eval celsius = 35 | streamingcsc', output_mode='json')
        result = results.JSONResultsReader(stream)
        ds = list(result)

        self.assertTrue(len(ds) == 5)
        self.assertTrue('_time' in ds[0])
        self.assertTrue('celsius' in ds[0])
        self.assertTrue('fahrenheit' in ds[0])
        self.assertTrue(ds[0]['celsius'] == '35')
        self.assertTrue(ds[0]['fahrenheit'] == '95.0')
        self.assertTrue(len(ds) == 5)


if __name__ == "__main__":
    unittest.main()

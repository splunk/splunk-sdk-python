#!/usr/bin/env python
#
# Copyright 2011-2012 Splunk, Inc.
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

import testlib
import logging

import splunklib.client as client

class FiredAlertTestCase(testlib.SDKTestCase):
    def setUp(self):
        super(FiredAlertTestCase, self).setUp()
        self.index_name = testlib.tmpname()
        self.assertFalse(self.index_name in self.service.indexes)
        self.index = self.service.indexes.create(self.index_name)
        self.service.restart(120)
        self.index = self.service.indexes[self.index_name]
        saved_searches = self.service.saved_searches
        self.saved_search_name = testlib.tmpname()
        self.assertFalse(self.saved_search_name in saved_searches)
        query = "search index=%s" % self.index_name
        kwargs = {'alert_type': 'always',
                  'alert.severity': "3",
                  'alert.suppress': "0",
                  'alert.track': "1",
                  'dispatch.earliest_time': "-1h",
                  'dispatch.latest_time': "now",
                  'is_scheduled': "1",
                  'cron_schedule': "* * * * *"}
        self.saved_search = saved_searches.create(
            self.saved_search_name,
            query, **kwargs)

    def tearDown(self):
        super(FiredAlertTestCase, self).tearDown()
        for saved_search in self.service.saved_searches:
            if saved_search.name.startswith('delete-me'):
                self.service.saved_searches.delete(saved_search.name)
                self.assertFalse(saved_search.name in self.service.saved_searches)
                self.assertFalse(saved_search.name in self.service.fired_alerts)

    def test_new_search_is_empty(self):
        self.assertEqual(self.saved_search.alert_count, 0)
        self.assertEqual(len(self.saved_search.history()), 0)
        self.assertEqual(len(self.saved_search.fired_alerts), 0)
        self.assertFalse(self.saved_search_name in self.service.fired_alerts)
        
    def test_alerts_on_events(self):
        self.assertEqual(self.saved_search.alert_count, 0)
        self.assertEqual(len(self.saved_search.fired_alerts), 0)
        eventCount = int(self.index['totalEventCount'])
        self.assertEqual(self.index['sync'], '0')
        self.assertEqual(self.index['disabled'], '0')
        self.index.refresh()
        self.index.submit('This is a test ' + testlib.tmpname(),
                          sourcetype='sdk_use', host='boris')
        testlib.retry(self.index, 'totalEventCount', str(eventCount+1), step=1, times=50)
        self.assertEqual(self.index['totalEventCount'], str(eventCount+1))
        testlib.retry(self.saved_search, lambda s: s.alert_count, 1, step=2, times=100)
        self.assertEqual(self.saved_search.alert_count, 1)
        alerts = self.saved_search.fired_alerts
        self.assertEqual(len(alerts), 1)

    def test_read(self):
        service = client.connect(**self.opts.kwargs)
        for alert_group in service.fired_alerts:
            alert_group.count
            for alert in alert_group.alerts:
                alert.content

if __name__ == "__main__":
    testlib.main()

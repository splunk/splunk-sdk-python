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

def event_count(index):
    return int(index.content.totalEventCount)

def alert_count(search):
    return int(search.content.get('triggered_alert_count', 0))

class TestCase(testlib.TestCase):
    def setUp(self):
        testlib.TestCase.setUp(self)
        saved_searches = self.service.saved_searches
        self.saved_search_name = testlib.tmpname()
        self.assertFalse(self.saved_search_name in saved_searches)
        query = "search index=_internal GET | head 10"
        kwargs = {'alert_type': "number of events",
                  'alert_comparator': "greater than",
                  'alert_threshold': "0",
                  'alert.severity': "3",
                  'alert.suppress': "0",
                  'alert.track': "1",
                  'dispatch.earliest_time': "rt-1m",
                  'dispatch.latest_time': "rt-0m",
                  'is_scheduled': "1",
                  'cron_schedule': "* * * * *"}
        self.saved_search = saved_searches.create(
            self.saved_search_name,
            query, **kwargs)

    def test_new_search_is_empty(self):
        self.assertEqual(alert_count(self.saved_search), 0)
        self.assertEqual(len(self.saved_search.history()), 0)
        
    def test_alert_on_event(self):
        N = alert_count(self.saved_search)
        self.saved_search.refresh()
        self.assertEqual(alert_count(self.saved_search), N+1)


    #     # Wait for the saved search to run. When it runs we will see a new job
    #     # show up in the search's history.
    #     def f(search):
    #         search.refresh()
    #         n = len(search.history())
    #         return n==1
    #     testlib.wait(search, f, timeout=120)
    #     self.assertEqual(len(search.history()), 1)

    #     # There should be no alerts if the search job hasn't been
    #     # created yet.
    #     search.refresh()
    #     self.assertTrue((alert_count(search) == 0) == (search_name not in fired_alerts))

    #     # Submit events and verify that they each trigger the expected
    #     # alert
    #     base_count = event_count(index)

    #     for count in xrange(1, 6):
    #         # Submit an event that the search is expected to match, and wait 
    #         # for the indexer to process.
    #         self.assertTrue(event_count(index) <= base_count+count)
    #         index.submit("Hello #%d!!!" % count)
    #         log("Submitted %d" % count)
    #         testlib.wait(index, lambda index: event_count(index) == base_count+count)
    #         time.sleep(2)
    #         log("Finished sleep")
    #         # return
            
    #         # # Wait for the saved search to register the triggered alert
    #         # self.assertTrue(alert_count(search) <= count)
    #         # testlib.wait(
    #         #     search, 
    #         #     lambda search: alert_count(search) == count, 
    #         #     timeout=10)
    #         # self.assertEqual(alert_count(search), count)

    #         # # And now .. after all that trouble, verify that we see the alerts!
    #         # self.assertTrue(search_name in fired_alerts)
    #         # alert_group = fired_alerts[search_name]
    #         # import pprint; pprint.pprint(alert_group._state)
    #         # self.assertEqual(alert_group.savedsearch_name, search_name)
    #         # import pprint; pprint.pprint(alert_group._state)
    #         # self.assertEqual(alert_group.count, count)
    #     return
    #     # Cleanup
    #     searches.delete(search_name)
    #     self.assertFalse(search_name in searches)
    #     self.assertFalse(search_name in fired_alerts)

    # def test_read(self):
    #     service = client.connect(**self.opts.kwargs)

    #     for alert_group in service.fired_alerts:
    #         alert_group.count
    #         for alert in alert_group.alerts:
    #             alert.content

if __name__ == "__main__":
    testlib.main()

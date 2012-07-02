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

f = open('log', 'w')

def log(s):
    print >>f, "FJR:" + time.asctime() + ": " + s
    f.flush()

import testlib
import time
import splunklib.client as client

def event_count(index):
    return int(index.content.totalEventCount)

def alert_count(search):
    n = int(search.content.get('triggered_alert_count', 0))
    print "# alerts: %d" % n
    return n

class TestCase(testlib.TestCase):
    def test_crud(self):
        service = client.connect(**self.opts.kwargs)

        searches = service.saved_searches
        fired_alerts = service.fired_alerts

        if 'sdk-tests' not in service.indexes:
            service.indexes.create("sdk-tests")

        # Clean out the test index
        index = service.indexes['sdk-tests']

        # Delete any leftover test search
        search_name = "sdk-test-search" + str(time.time())
        if search_name in searches: searches.delete(search_name)
        self.assertFalse(search_name in searches)

        # Create a saved search that will register an alert for any event
        # submitted to the `sdk-tests` index. Note that the search is not
        # yet scheduled - we wil schedule after doing a little more cleanup.
        query = "index=sdk-tests"
        kwargs = {
            'actions': "rss",
            'alert_type': "always",
            'alert_comparator': "greater than",
            'alert_threshold': "0",
            'alert.severity': "5",
            'alert.suppress': "0",
            'alert.track': "1",
            'dispatch.earliest_time': "rt",
            'dispatch.latest_time': "rt",
            'is_scheduled': "0",
            'realtime_schedule': "1",
            'cron_schedule': "* * * * *"
        }
        search = searches.create(search_name, query, **kwargs)
        self.assertEqual(search.name, search_name)
        self.assertEqual(search.content.is_scheduled, "0")

        # Clear out any search history that may have matched due to reuse of 
        # the saved search name.
        for job in search.history(): job.cancel()
        testlib.wait(search, lambda search: len(search.history()) == 0)
        self.assertEqual(len(search.history()), 0)

        # Now schedule the saved search
        search.update(is_scheduled=1)
        search.refresh()
        self.assertEqual(search.content.is_scheduled, "1")
        self.assertEqual(alert_count(search), 0)

        # Wait for the saved search to run. When it runs we will see a new job
        # show up in the search's history.
        testlib.wait(search, lambda search: len(search.history()) == 1)
        self.assertEqual(len(search.history()), 1)

        # When it first runs the alert count should be zero.
        search.refresh()
        self.assertEqual(alert_count(search), 0)

        # And the fired alerts category should not exist
        self.assertFalse(search_name in fired_alerts)

        # Submit events and verify that they each trigger the expected
        # alert
        base_count = event_count(index)

        for count in xrange(1, 6):
            # Submit an event that the search is expected to match, and wait 
            # for the indexer to process.
            self.assertTrue(event_count(index) <= base_count+count)
            index.submit("Hello #%d!!!" % count)
            log("Submitted %d" % count)
            testlib.wait(index, lambda index: event_count(index) == base_count+count)
            time.sleep(2)
            log("Finished sleep")
            # return
            
            # # Wait for the saved search to register the triggered alert
            # self.assertTrue(alert_count(search) <= count)
            # testlib.wait(
            #     search, 
            #     lambda search: alert_count(search) == count, 
            #     timeout=10)
            # self.assertEqual(alert_count(search), count)

            # # And now .. after all that trouble, verify that we see the alerts!
            # self.assertTrue(search_name in fired_alerts)
            # alert_group = fired_alerts[search_name]
            # import pprint; pprint.pprint(alert_group._state)
            # self.assertEqual(alert_group.savedsearch_name, search_name)
            # import pprint; pprint.pprint(alert_group._state)
            # self.assertEqual(alert_group.count, count)
        return
        # Cleanup
        searches.delete(search_name)
        self.assertFalse(search_name in searches)
        self.assertFalse(search_name in fired_alerts)

    def test_read(self):
        service = client.connect(**self.opts.kwargs)

        for alert_group in service.fired_alerts:
            alert_group.count
            for alert in alert_group.alerts:
                alert.content

if __name__ == "__main__":
    testlib.main()

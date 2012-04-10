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

import sys
from time import sleep
import unittest

import splunklib.client as client
from utils import parse

opts = None # Command line options

def event_count(index):
    return int(index.content.totalEventCount)

def alert_count(search):
    return int(search.content.get('triggered_alert_count', 0))

# UNDONE: move the following (duplicated) routine into utility module
def wait(entity, predicate, timeout=60):
    secs = 0
    while not predicate(entity):
        if secs > timeout:
            raise Exception, "Operation timed out."
        sleep(1)
        secs += 1
        entity.refresh()
    return entity

class TestCase(unittest.TestCase):
    def test_crud(self):
        service = client.connect(**opts.kwargs)

        searches = service.saved_searches
        fired_alerts = service.fired_alerts

        # Clean out the test index
        index = service.indexes['sdk-tests']
        index.clean()
        index.refresh()
        self.assertEqual(event_count(index), 0)

        # Delete any leftover test search
        search_name = "sdk-test-search"
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
        wait(search, lambda search: len(search.history()) == 0)
        self.assertEqual(len(search.history()), 0)

        # Now schedule the saved search
        search.update(is_scheduled=1)
        search.refresh()
        self.assertEqual(search.content.is_scheduled, "1")
        self.assertEqual(alert_count(search), 0)

        # Wait for the saved search to run. When it runs we will see a new job
        # show up in the search's history.
        wait(search, lambda search: len(search.history()) == 1)
        self.assertEqual(len(search.history()), 1)

        # When it first runs the alert count should be zero.
        search.refresh()
        self.assertEqual(alert_count(search), 0)

        # And the fired alerts category should not exist
        self.assertFalse(search_name in fired_alerts)

        # Submit events and verify that they each trigger the expected alert
        for count in xrange(1, 6):
            # Submit an event that the search is expected to match, and wait 
            # for the indexer to process.
            self.assertTrue(event_count(index) <= count)
            index.submit("Hello #%d!!!" % count)
            wait(index, lambda index: event_count(index) == count)

            # Wait for the saved search to register the triggered alert
            self.assertTrue(alert_count(search) <= count)
            wait(search, lambda search: alert_count(search) == count)
            self.assertEqual(alert_count(search), count)

            # And now .. after all that trouble, verify that we see the 
            # expected alerts!
            self.assertTrue(search_name in fired_alerts)
            alerts = fired_alerts[search_name]
            self.assertEqual(alerts.name, search_name)
            actual = int(alerts.content.triggered_alert_count)
            self.assertEqual(actual, count)

        # Cleanup
        searches.delete(search_name)
        self.assertFalse(search_name in searches)
        self.assertFalse(search_name in fired_alerts)

    def test_read(self):
        service = client.connect(**opts.kwargs)
        fired_alerts = service.fired_alerts

        for fired_alert in fired_alerts:
            fired_alert.content

if __name__ == "__main__":
    opts = parse(sys.argv[1:], {}, ".splunkrc")
    unittest.main(argv=sys.argv[:1])

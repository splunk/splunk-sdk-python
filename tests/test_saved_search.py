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

import datetime
import testlib
import logging

from time import sleep

import splunklib.client as client

def to_bool(x):
    if x == '1':
        return True
    elif x == '0':
        return False
    else:
        raise ValueError("Not a boolean value: %s", x)

class TestSavedSearch(testlib.TestCase):
    def setUp(self):
        super(TestSavedSearch, self).setUp()
        saved_searches = self.service.saved_searches
        self.saved_search_name = testlib.tmpname()
        query = "search index=_internal * earliest=-1m | head 3"
        self.saved_search = saved_searches.create(self.saved_search_name, query)

    def tearDown(self):
        super(TestSavedSearch, self).setUp()
        for saved_search in self.service.saved_searches:
            if saved_search.name.startswith('delete-me'):
                try:
                    for job in saved_search.history():
                        job.cancel()
                    self.service.saved_searches.delete(saved_search.name)
                except KeyError:
                    pass

    def check_saved_search(self, saved_search):
        self.check_entity(saved_search)
        saved_search['alert.expires']
        saved_search['alert.severity']
        saved_search['alert.track']
        saved_search['alert_type']
        saved_search['dispatch.buckets']
        saved_search['dispatch.lookups']
        saved_search['dispatch.max_count']
        saved_search['dispatch.max_time']
        saved_search['dispatch.reduce_freq']
        saved_search['dispatch.spawn_process']
        saved_search['dispatch.time_format']
        saved_search['dispatch.ttl']
        saved_search['max_concurrent']
        saved_search['realtime_schedule']
        saved_search['restart_on_searchpeer_add']
        saved_search['run_on_startup']
        saved_search['search']
        saved_search['action.email']
        saved_search['action.populate_lookup']
        saved_search['action.rss']
        saved_search['action.script']
        saved_search['action.summary_index']
        self.assertGreaterEqual(saved_search['suppressed'], 0)
        is_scheduled = saved_search.content['is_scheduled']
        self.assertTrue(is_scheduled == '1' or is_scheduled == '0')
        is_visible = saved_search.content['is_visible']
        self.assertTrue(is_visible == '1' or is_visible == '0')

    def test_create(self):
        self.assertTrue(self.saved_search_name in self.service.saved_searches)
        self.check_saved_search(self.saved_search)

    def test_delete(self):
        self.assertTrue(self.saved_search_name in self.service.saved_searches)
        self.service.saved_searches.delete(self.saved_search_name)
        self.assertFalse(self.saved_search_name in self.service.saved_searches)
        self.assertRaises(client.EntityDeletedException,
                          self.saved_search.refresh)

    
    def test_update(self):
        is_visible = to_bool(self.saved_search['is_visible'])
        self.saved_search.update(is_visible=not is_visible)
        self.saved_search.refresh()
        self.assertEqual(to_bool(self.saved_search['is_visible']), not is_visible)
        
    def test_cannot_update_name(self):
        new_name = self.saved_search_name + '-alteration'
        self.assertRaises(client.IllegalOperationException, 
                          self.saved_search.update, new_name)

    def test_name_collision(self):
        opts = self.opts.kwargs.copy()
        opts['owner'] = '-'
        opts['app'] = '-'
        opts['sharing'] = 'user'
        service = client.connect(**opts)
        logging.debug("Namespace for collision testing: %s", service.namespace)
        saved_searches = service.saved_searches
        name = testlib.tmpname()
        
        query1 = '* earliest=-1m | head 1'
        query2 = '* earliest=-2m | head 2'
        namespace1 = client.namespace(app='search', sharing='app')
        namespace2 = client.namespace(owner='admin', app='search', sharing='user')
        saved_search2 = saved_searches.create(
            name, query2,
            namespace=namespace1)
        saved_search1 = saved_searches.create(
            name, query1,
            namespace=namespace2)

        self.assertRaises(client.AmbiguousReferenceException,
                          saved_searches[name])
        self.check_saved_search(saved_searches[name, namespace1])
        self.check_saved_search(saved_searches[name, namespace2])

    def test_dispatch(self):
        try:
            job = self.saved_search.dispatch()
            while not job.isReady():
                sleep(0.1)
            self.assertTrue(job.sid in self.service.jobs)
        finally:
            job.cancel()
        
    def test_dispatch_with_options(self):
        try:
            kwargs = { 'dispatch.buckets': 100 }
            job = self.saved_search.dispatch(**kwargs)
            while not job.isReady():
                sleep(0.1)
            self.assertTrue(job.sid in self.service.jobs)
        finally:
            job.cancel()

    def test_history(self):
        try:
            old_jobs = self.saved_search.history()
            N = len(old_jobs)
            logging.debug("Found %d jobs in saved search history", N)
            job = self.saved_search.dispatch()
            while not job.isReady():
                sleep(0.1)
            history = self.saved_search.history()
            self.assertEqual(len(history), N+1)
            self.assertTrue(job.sid in [j.sid for j in history])
        finally:
            job.cancel()

    def test_scheduled_times(self):
        self.saved_search.update(cron_schedule='*/5 * * * *', is_scheduled=True)
        scheduled_times = self.saved_search.scheduled_times()
        logging.debug("Scheduled times: %s", scheduled_times)
        self.assertTrue(all([isinstance(x, datetime.datetime) 
                             for x in scheduled_times]))
        time_pairs = zip(scheduled_times[:-1], scheduled_times[1:])
        for earlier, later in time_pairs:
            diff = later-earlier
            self.assertEqual(diff.total_seconds()/60, 5)

    def test_no_equality(self):
        self.assertRaises(client.IncomparableException,
                          self.saved_search.__eq__, self.saved_search)

    def test_suppress(self):
        suppressed_time = self.saved_search['suppressed']
        self.assertGreaterEqual(suppressed_time, 0)
        new_suppressed_time = suppressed_time+100
        self.saved_search.suppress(new_suppressed_time)
        self.assertLessEqual(self.saved_search['suppressed'], 
                             new_suppressed_time)
        self.assertGreater(self.saved_search['suppressed'],
                           suppressed_time)
        self.saved_search.unsuppress()
        self.assertEqual(self.saved_search['suppressed'], 0)

if __name__ == "__main__":
    testlib.main()

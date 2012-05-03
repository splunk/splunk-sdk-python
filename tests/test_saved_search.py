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

import splunklib.client as client

class TestCase(testlib.TestCase):
    def check_saved_search(self, saved_search):
        self.check_entity(saved_search)
        saved_search.content['alert.expires']
        saved_search.content['alert.severity']
        saved_search.content['alert.track']
        saved_search.content.alert_type
        saved_search.content['dispatch.buckets']
        saved_search.content['dispatch.lookups']
        saved_search.content['dispatch.max_count']
        saved_search.content['dispatch.max_time']
        saved_search.content['dispatch.reduce_freq']
        saved_search.content['dispatch.spawn_process']
        saved_search.content['dispatch.time_format']
        saved_search.content['dispatch.ttl']
        saved_search.content.max_concurrent
        saved_search.content.realtime_schedule
        saved_search.content.restart_on_searchpeer_add
        saved_search.content.run_on_startup
        saved_search.content.search
        saved_search.content['action.email']
        saved_search.content['action.populate_lookup']
        saved_search.content['action.rss']
        saved_search.content['action.script']
        saved_search.content['action.summary_index']
        saved_search.content.is_scheduled
        saved_search.content.is_visible

    def test_read(self):
        service = client.connect(**self.opts.kwargs)
        saved_searches = service.saved_searches

        if 'sdk-test1' in saved_searches:
            saved_searches.delete('sdk-test1')
        self.assertFalse('sdk-test1' in saved_searches)

        # Make sure there is at least one saved search to read
        search = "search index=sdk-tests * earliest=-1m"
        saved_search = saved_searches.create('sdk-test1', search)
        self.assertEqual('sdk-test1', saved_search.name)
        self.assertTrue('sdk-test1' in saved_searches)

        for saved_search in saved_searches:
            self.check_saved_search(saved_search)
            saved_search.refresh()
            self.check_saved_search(saved_search)

        saved_searches.delete('sdk-test1')
        self.assertFalse('sdk-test1' in saved_searches)

    def test_crud(self):
        service = client.connect(**self.opts.kwargs)
        saved_searches = service.saved_searches

        if 'sdk-test1' in saved_searches:
            saved_searches.delete('sdk-test1')
        self.assertFalse('sdk-test1' in saved_searches)

        search = "search index=sdk-tests * earliest=-1m"
        saved_search = saved_searches.create('sdk-test1', search)
        self.assertEqual('sdk-test1', saved_search.name)
        self.assertTrue('sdk-test1' in saved_searches)

        saved_search = saved_searches['sdk-test1']
        self.check_content(saved_search, is_visible=1)

        saved_search.update(is_visible=False)
        saved_search.refresh()
        self.check_content(saved_search, is_visible=0)

        self.assertRaises(ValueError, saved_search.update, saved_search, name="Anything")

        saved_searches.delete('sdk-test1')
        self.assertFalse('sdk-test1' in saved_searches)

        saved_search = saved_searches.create(
            'sdk-test1', search, is_visible=False)
        self.assertEqual('sdk-test1', saved_search.name)
        self.assertTrue('sdk-test1' in saved_searches)
        self.check_content(saved_search, is_visible=0)

        saved_searches.delete('sdk-test1')
        self.assertFalse('sdk-test1' in saved_searches)

    def test_dispatch(self):
        service = client.connect(**self.opts.kwargs)
        saved_searches = service.saved_searches

        if 'sdk-test1' in saved_searches:
            saved_searches.delete('sdk-test1')
        self.assertFalse('sdk-test1' in saved_searches)

        search = "search index=sdk-tests * earliest=-1m"
        saved_search = saved_searches.create('sdk-test1', search)
        self.assertEqual('sdk-test1', saved_search.name)
        self.assertTrue('sdk-test1' in saved_searches)

        job = saved_search.dispatch()
        testlib.wait(job, lambda job: bool(int(job['isDone'])))
        job.results().close()
        job.cancel()

        # Dispatch with some additional options
        kwargs = { 'dispatch.buckets': 100 }
        job = saved_search.dispatch(**kwargs)
        testlib.wait(job, lambda job: bool(int(job['isDone'])))
        job.timeline().close()
        job.cancel()

        saved_searches.delete('sdk-test1')
        self.assertFalse('sdk-test1' in saved_searches)

    def test_history(self):
        service = client.connect(**self.opts.kwargs)
        saved_searches = service.saved_searches

        if 'sdk-test1' in saved_searches:
            saved_searches.delete('sdk-test1')
        self.assertFalse('sdk-test1' in saved_searches)

        search = "search index=sdk-tests * earliest=-1m"
        saved_search = saved_searches.create('sdk-test1', search)
        self.assertEqual('sdk-test1', saved_search.name)
        self.assertTrue('sdk-test1' in saved_searches)

        # Clear the history in case any is left over from a previous saved
        # search with the same name.
        for job in saved_search.history():
            job.cancel()

        history = saved_search.history()
        self.assertEqual(len(history), 0)

        def contains(history, sid):
            return sid in [job.sid for job in history]

        job1 = saved_search.dispatch()
        history = saved_search.history()
        self.assertEqual(len(history), 1)
        self.assertTrue(contains(history, job1.sid))

        job2 = saved_search.dispatch()
        history = saved_search.history()
        self.assertEqual(len(history), 2)
        self.assertTrue(contains(history, job1.sid))
        self.assertTrue(contains(history, job2.sid))

        job1.cancel()
        history = saved_search.history()
        self.assertEqual(len(history), 1)
        self.assertFalse(contains(history, job1.sid))
        self.assertTrue(contains(history, job2.sid))

        job2.cancel()
        history = saved_search.history()
        self.assertEqual(len(history), 0)
        self.assertFalse(contains(history, job1.sid))
        self.assertFalse(contains(history, job2.sid))

        saved_searches.delete('sdk-test1')
        self.assertFalse('sdk-test1' in saved_searches)

if __name__ == "__main__":
    testlib.main()

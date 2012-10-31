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

import unittest

import splunklib.client as client
import splunklib.results as results

from splunklib.binding import _log_duration

class TestUtilities(testlib.SDKTestCase):
    def test_service_search(self):
        job = self.service.search('search index=_internal earliest=-1m | head 3')
        self.assertTrue(self.service.jobs.contains(job.sid))
        job.cancel()

    def test_oneshot_with_garbage_fails(self):
        jobs = self.service.jobs
        self.assertRaises(TypeError, jobs.create, "abcd", exec_mode="oneshot")

    def test_oneshot(self):
        jobs = self.service.jobs
        stream = jobs.oneshot("search index=_internal earliest=-1m | head 3")
        result = results.ResultsReader(stream)
        ds = list(result)
        self.assertEqual(result.is_preview, False)
        self.assertTrue(isinstance(ds[0], dict) or \
                            isinstance(ds[0], results.Message))
        nonmessages = [d for d in ds if isinstance(d, dict)]
        self.assertTrue(len(nonmessages) <= 3)

    def test_export_with_garbage_fails(self):
        jobs = self.service.jobs
        self.assertRaises(ValueError, jobs.export, "asdaf;lkj2r23=")

    def test_export(self):
        jobs = self.service.jobs
        stream = jobs.export("search index=_internal earliest=-1m | head 3")
        result = results.ResultsReader(stream)
        ds = list(result)
        self.assertEqual(result.is_preview, False)
        self.assertTrue(isinstance(ds[0], dict) or \
                            isinstance(ds[0], results.Message))
        nonmessages = [d for d in ds if isinstance(d, dict)]
        self.assertTrue(len(nonmessages) <= 3)

    def test_normal_job_with_garbage_fails(self):
        jobs = self.service.jobs
        try:
            bad_search = "abcd|asfwqqq"
            jobs.create(bad_search)
        except TypeError as te:
            self.assertTrue('abcd' in te.message)
            return
        self.fail("Job with garbage search failed to raise TypeError.")

    def test_cancel(self):
        jobs = self.service.jobs
        job = jobs.create(query="search index=_internal | head 3",
                          earliest_time="-1m",
                          latest_time="now")
        self.assertTrue(job.sid in jobs)
        job.cancel()
        self.assertFalse(job.sid in jobs)

    def test_cancel_is_idempotent(self):
        jobs = self.service.jobs
        job = jobs.create(query="search index=_internal | head 3",
                          earliest_time="-1m",
                          latest_time="now")
        self.assertTrue(job.sid in jobs)
        job.cancel()
        job.cancel() # Second call should be nop

    def check_job(self, job):
        self.check_entity(job)
        keys = ['cursorTime', 'delegate', 'diskUsage', 'dispatchState',
                'doneProgress', 'dropCount', 'earliestTime', 'eventAvailableCount',
                'eventCount', 'eventFieldCount', 'eventIsStreaming',
                'eventIsTruncated', 'eventSearch', 'eventSorting', 'isDone',
                'isFailed', 'isFinalized', 'isPaused', 'isPreviewEnabled',
                'isRealTimeSearch', 'isRemoteTimeline', 'isSaved', 'isSavedSearch',
                'isZombie', 'keywords', 'label', 'latestTime', 'messages',
                'numPreviews', 'priority', 'remoteSearch', 'reportSearch',
                'resultCount', 'resultIsStreaming', 'resultPreviewCount',
                'runDuration', 'scanCount', 'searchProviders', 'sid',
                'statusBuckets', 'ttl']
        for key in keys:
            self.assertTrue(key in job.content)

    def test_read_jobs(self):
        jobs = self.service.jobs
        for job in jobs.list(count=5):
            self.check_job(job)
            job.refresh()
            self.check_job(job)

class TestJobWithDelayedDone(testlib.SDKTestCase):
    def setUp(self):
        super(TestJobWithDelayedDone, self).setUp()
        self.install_app_from_collection("sleep_command")
        self.query = "search index=_internal | sleep done=100"
        self.job = self.service.jobs.create(
            query=self.query,
            earliest_time="-1m",
            priority=5,
            latest_time="now")

    def tearDown(self):
        super(TestJobWithDelayedDone, self).tearDown()
        self.job.cancel()
        self.assertEventuallyTrue(lambda: self.job.sid not in self.service.jobs)

    def test_enable_preview(self):
        self.assertEqual(self.job['isPreviewEnabled'], '0')
        self.job.enable_preview()
        def is_preview():
            if self.job.is_done():
                self.fail('Job finished before preview enabled.')
            return self.job['isPreviewEnabled'] == '1'
        self.assertEventuallyTrue(is_preview)

    def test_setpriority(self):
        # Note that you can only *decrease* the priority (i.e., 5 decreased to 3)
        # of a job unless Splunk is running as root. This is because Splunk jobs
        # are tied up with operating system processes and their priorities.
        self.assertEqual(5, int(self.job['priority']))

        new_priority = 3
        self.job.set_priority(new_priority)

        def f():
            if self.job.is_done():
                self.fail("Job already done before priority was set.")
            self.job.refresh()
            return int(self.job['priority']) == new_priority
        self.assertEventuallyTrue(f, timeout=120)

class TestJob(testlib.SDKTestCase):
    def setUp(self):
        super(TestJob, self).setUp()
        self.query = "search index=_internal | head 3"
        self.job = self.service.jobs.create(
            query=self.query, 
            earliest_time="-1m", 
            latest_time="now")

    def tearDown(self):
        super(TestJob, self).tearDown()
        self.job.cancel()

    @_log_duration
    def test_get_preview_and_events(self):
        self.assertEventuallyTrue(self.job.is_done)
        self.assertLessEqual(int(self.job['eventCount']), 3)

        preview_stream = self.job.preview()
        preview_r = results.ResultsReader(preview_stream)
        self.assertFalse(preview_r.is_preview)

        events_stream = self.job.events()
        events_r = results.ResultsReader(events_stream)

        n_events = len([x for x in events_r if isinstance(x, dict)])
        n_preview = len([x for x in preview_r if isinstance(x, dict)])
        self.assertEqual(n_events, n_preview)

    def test_pause(self):
        if self.job['isPaused'] == '1':
            self.job.unpause()
            self.job.refresh()
            self.assertEqual(self.job['isPaused'], '0')

        self.job.pause()
        self.assertEventuallyTrue(lambda: self.job.refresh()['isPaused'] == '1')

    def test_unpause(self):
        if self.job['isPaused'] == '0':
            self.job.pause()
            self.job.refresh()
            self.assertEqual(self.job['isPaused'], '1')
        self.job.unpause()
        self.assertEventuallyTrue(lambda: self.job.refresh()['isPaused'] == '0')

    def test_finalize(self):
        if self.job['isFinalized'] == '1':
            self.fail("Job is already finalized; can't test .finalize() method.")
        else:
            self.job.finalize()
            self.assertEventuallyTrue(lambda: self.job.refresh()['isFinalized'] == '1')

    def test_setttl(self):
        old_ttl = int(self.job['ttl'])
        new_ttl = old_ttl + 1000
        
        from datetime import datetime
        start_time = datetime.now()
        self.job.set_ttl(new_ttl)

        tries = 3
        while True:
            self.job.refresh()
            ttl = int(self.job['ttl'])
            if ttl <= new_ttl and ttl > old_ttl:
                break
            else:
                tries -= 1
        self.assertLessEqual(ttl, new_ttl)
        self.assertGreater(ttl, old_ttl)

    def test_touch(self):
        # This cannot be tested very fast. touch will reset the ttl to the original value for the job,
        # so first we have to wait just long enough for the ttl to tick down. Its granularity is 1s,
        # so we'll wait 1.1s before we start.
        import time; time.sleep(1.1)
        old_ttl = int(self.job['ttl'])
        self.job.touch()
        self.job.refresh()
        new_ttl = int(self.job['ttl'])
        if new_ttl == old_ttl:
            self.fail("Didn't wait long enough for TTL to change and make touch meaningful.")
        self.assertGreater(int(self.job['ttl']), old_ttl)

class TestResultsReader(unittest.TestCase):
    def test_results_reader(self):
        # Run jobs.export("search index=_internal | stats count",
        # earliest_time="rt", latest_time="rt") and you get a
        # streaming sequence of XML fragments containing results.
        with open('data/results.xml') as input:
            reader = results.ResultsReader(input)
            self.assertFalse(reader.is_preview)
            N_results = 0
            N_messages = 0
            for r in reader:
                import collections
                self.assertTrue(isinstance(r, collections.OrderedDict) 
                                or isinstance(r, results.Message))
                if isinstance(r, collections.OrderedDict):
                    N_results += 1
                elif isinstance(r, results.Message):
                    N_messages += 1
            self.assertEqual(N_results, 4999)
            self.assertEqual(N_messages, 2)

    def test_results_reader_with_streaming_results(self):
        # Run jobs.export("search index=_internal | stats count",
        # earliest_time="rt", latest_time="rt") and you get a
        # streaming sequence of XML fragments containing results.
        with open('data/streaming_results.xml') as input:
            reader = results.ResultsReader(input)
            N_results = 0
            N_messages = 0
            for r in reader:
                import collections
                self.assertTrue(isinstance(r, collections.OrderedDict) 
                                or isinstance(r, results.Message))
                if isinstance(r, collections.OrderedDict):
                    N_results += 1
                elif isinstance(r, results.Message):
                    N_messages += 1
            self.assertEqual(N_results, 3)
            self.assertEqual(N_messages, 3)
        

    def test_xmldtd_filter(self):
        from StringIO import StringIO
        s = results._XMLDTDFilter(StringIO("<?xml asdf awe awdf=""><boris>Other stuf</boris><?xml dafawe \n asdfaw > ab"))
        self.assertEqual(s.read(), "<boris>Other stuf</boris> ab")

    def test_concatenated_stream(self):
        from StringIO import StringIO
        s = results._ConcatenatedStream(StringIO("This is a test "),
                                       StringIO("of the emergency broadcast system."))
        self.assertEqual(s.read(3), "Thi")
        self.assertEqual(s.read(20), 's is a test of the e')
        self.assertEqual(s.read(), 'mergency broadcast system.')

if __name__ == "__main__":
    import unittest
    unittest.main()

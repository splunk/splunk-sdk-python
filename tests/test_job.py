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
import splunklib.results as results

from splunklib.binding import log_duration

class TestUtilities(testlib.TestCase):
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
        self.assertRaises(TypeError, jobs.create, "abcd|asfwqqq")

    def test_cancel(self):
        jobs = self.service.jobs
        job = jobs.create(query="search index=_intenal | head 3",
                          earliest_time="-1m",
                          latest_time="now")
        self.assertTrue(job.sid in jobs)
        job.cancel()
        self.assertFalse(job.sid in jobs)

    def test_cancel_is_idempotent(self):
        jobs = self.service.jobs
        job = jobs.create(query="search index=_intenal | head 3",
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

def retry(job, field, expected, times=3):
    # Sometimes there is a slight delay in the value getting
    # set in splunkd. If it fails, just try again.
    tries = times
    while tries > 0:
        job.refresh()
        p = job[field]
        if p != expected:
            tries -= 1
        else:
            break


class TestJob(testlib.TestCase):
    def setUp(self):
        testlib.TestCase.setUp(self)
        self.query = "search index=_internal earliest=-1m | head 3"
        self.job = self.service.jobs.create(
            query=self.query, 
            earliest_time="-1m", 
            latest_time="now")

    def tearDown(self):
        testlib.TestCase.tearDown(self)
        self.job.cancel()

    def test_get_preview_and_events(self):
        with log_duration():
            tries = 0
            while not self.job.isDone():
                tries += 1
        logging.debug("Polled %d times", tries)

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
        retry(self.job, 'isPaused', '1')
        self.assertEqual(self.job['isPaused'], '1')

    def test_unpause(self):
        if self.job['isPaused'] == '0':
            self.job.pause()
            self.job.refresh()
            self.assertEqual(self.job['isPaused'], '1')
        self.job.unpause()
        retry(self.job, 'isPaused', '0')
        self.assertEqual(self.job['isPaused'], '0')

    def test_finalize(self):
        if self.job['isFinalized'] == '1':
            self.fail("Job is already finalized; can't test .finalize() method.")
        else:
            self.job.finalize()
            retry(self.job, 'isFinalized', '1')
            self.assertEqual(self.job['isFinalized'], '1')

    def test_setpriority(self):
        old_priority = int(self.job['priority'])
        new_priority = old_priority%10 + 1
        self.assertNotEqual(old_priority, new_priority)

        self.job.set_priority(new_priority)
        retry(self.job, 'priority', str(new_priority))
        self.assertEqual(int(self.job['priority']), new_priority)

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
        # This is a problem to test. You have to wait for it to change
        # before touch gets anywhere, and the granularity of ttl is seconds.
        old_ttl = int(self.job['ttl'])
        import time; time.sleep(2)
        self.job.touch()
        self.job.refresh()
        new_ttl = int(self.job['ttl'])
        if new_ttl == old_ttl:
            self.fail("Didn't wait long enough for TTL to change and make touch meaningful.")
        self.assertGreaterEqual(int(self.job['ttl']), old_ttl)
        
    # def test_update(self):
    #     job = self.job

    #     new_priority = int(job['priority']) % 10  +  1
    #     new_ttl = int(job['ttl']) + 1

    #     job.disable_preview()
    #     job.pause()
    #     job.set_ttl(new_ttl)
    #     job.set_priority(new_priority)
    #     job.touch()

    #     job.refresh()

    #     self.assertEqual(job['isPaused'], '1')
    #     self.assertEqual(job['isPreviewEnabled'], '0')
    #     self.assertEqual(int(job['ttl']), new_ttl)
    #     self.assertEqual(int(job['priority']), new_priority)

    #     job.enable_preview()
    #     job.unpause()
    #     job.refresh()

    #     #self.assertEqual(job['isPreviewEnabled'], '1')
    #     self.assertEqual(job['isPaused'], '0')
    #     self.assertEqual(job['isFinalized'], '0')

    #     job.disable_preview()
    #     job.pause()
    #     job.set_ttl(1001)
    #     job.set_priority(6)
    #     job.touch()
    #     job.finalize()

    #     job.refresh()

    #     self.assertEqual(job['isPaused'], '1')
    #     self.assertEqual(job['isPreviewEnabled'], '0')
    #     self.assertEqual(job['ttl'], '1001')
    #     self.assertEqual(job['priority'], '6')
    #     self.assertEqual(job['isFinalized'], '1')

#     def test_results(self):
#         service = client.connect(**self.opts.kwargs)

#         jobs = service.jobs

#         # Run a new job to get the results, but we also make
#         # sure that there is at least one event in the index already
#         index = service.indexes['_internal']
#         self.assertTrue(index['totalEventCount'] > 0)

#         job = jobs.create("search index=_internal | head 1 | stats count")
#         job.refresh()
#         self.assertEqual(job['isDone'], '0')
#         # When a job was first created in Splunk 4.x, results would
#         # return 204 before results were available. Itay requested a
#         # change for Ace, and now it just returns 200 with an empty
#         # <results/> element. Thus this test is obsolete. I leave it
#         # here as a caution to future generations:
#         # self.assertRaises(ValueError, job.results)
#         while not job.isDone():
#             sleep(1)
#         reader = results.ResultsReader(job.results(timeout=60))
#         job.refresh()
#         self.assertEqual(job['isDone'], '1')

#         self.assertEqual(reader.is_preview, False)

#         result = reader.next()
#         self.assertTrue(isinstance(result, dict))
#         self.assertLessEqual(int(result["count"]), 1)

#         # Repeat the same thing, but without the .is_preview reference.
#         job = jobs.create("search index=_internal | head 1 | stats count")
#         while not job.isDone():
#             sleep(1)
#         reader = results.ResultsReader(job.results(timeout=60))
#         job.refresh()
#         self.assertEqual(job['isDone'], '1')
#         result = reader.next()
#         self.assertTrue(isinstance(result, dict))
#         self.assertLessEqual(int(result["count"]), 1)

#     def test_results_reader(self):
#         # Run jobs.export("search index=_internal | stats count",
#         # earliest_time="rt", latest_time="rt") and you get a
#         # streaming sequence of XML fragments containing results.
#         with open('streaming_results.xml') as input:
#             reader = results.ResultsReader(input)
#             print reader.next()
#             self.assertTrue(isinstance(reader.next(), dict))

#     def test_xmldtd_filter(self):
#         from StringIO import StringIO
#         s = results.XMLDTDFilter(StringIO("<?xml asdf awe awdf=""><boris>Other stuf</boris><?xml dafawe \n asdfaw > ab"))
#         self.assertEqual(s.read(3), "<bo")
#         self.assertEqual(s.read(), "ris>Other stuf</boris> ab")


#     def test_concatenated_stream(self):
#         from StringIO import StringIO
#         s = results.ConcatenatedStream(StringIO("This is a test "), 
#                                        StringIO("of the emergency broadcast system."))
#         self.assertEqual(s.read(3), "Thi")
#         self.assertEqual(s.read(20), 's is a test of the e')
#         self.assertEqual(s.read(), 'mergency broadcast system.')
            

if __name__ == "__main__":
    testlib.main()

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

from io import BytesIO
from pathlib import Path
from time import sleep

import io

from tests import testlib

import unittest

from splunklib import client
from splunklib import results

from splunklib.binding import _log_duration, HTTPError

import pytest


class TestUtilities(testlib.SDKTestCase):
    def test_service_search(self):
        job = self.service.search('search index=_internal earliest=-1m | head 3')
        self.assertTrue(job.sid in self.service.jobs)
        job.cancel()

    def test_create_job_with_output_mode_json(self):
        job = self.service.jobs.create(query='search index=_internal earliest=-1m | head 3', output_mode='json')
        self.assertTrue(job.sid in self.service.jobs)
        job.cancel()

    def test_oneshot_with_garbage_fails(self):
        jobs = self.service.jobs
        self.assertRaises(TypeError, jobs.create, "abcd", exec_mode="oneshot")

    @pytest.mark.smoke
    def test_oneshot(self):
        jobs = self.service.jobs
        stream = jobs.oneshot("search index=_internal earliest=-1m | head 3", output_mode='json')
        result = results.JSONResultsReader(stream)
        ds = list(result)
        self.assertEqual(result.is_preview, False)
        self.assertTrue(isinstance(ds[0], dict) or \
                            isinstance(ds[0], results.Message))
        nonmessages = [d for d in ds if isinstance(d, dict)]
        self.assertTrue(len(nonmessages) <= 3)

    def test_export_with_garbage_fails(self):
        jobs = self.service.jobs
        self.assertRaises(client.HTTPError, jobs.export, "asdaf;lkj2r23=")

    def test_export(self):
        jobs = self.service.jobs
        stream = jobs.export("search index=_internal earliest=-1m | head 3", output_mode='json')
        result = results.JSONResultsReader(stream)
        ds = list(result)
        self.assertEqual(result.is_preview, False)
        self.assertTrue(isinstance(ds[0], dict) or \
                            isinstance(ds[0], results.Message))
        nonmessages = [d for d in ds if isinstance(d, dict)]
        self.assertTrue(len(nonmessages) <= 3)

    def test_export_docstring_sample(self):
        from splunklib import client
        from splunklib import results
        service = self.service # cheat
        rr = results.JSONResultsReader(service.jobs.export("search * | head 5", output_mode='json'))
        for result in rr:
            if isinstance(result, results.Message):
                # Diagnostic messages may be returned in the results
                pass #print(f'{result.type}: {result.message}')
            elif isinstance(result, dict):
                # Normal events are returned as dicts
                pass #print(result)
        assert rr.is_preview == False

    def test_results_docstring_sample(self):
        from splunklib import results
        service = self.service  # cheat
        job = service.jobs.create("search * | head 5")
        while not job.is_done():
            sleep(0.2)
        rr = results.JSONResultsReader(job.results(output_mode='json'))
        for result in rr:
            if isinstance(result, results.Message):
                # Diagnostic messages may be returned in the results
                pass #print(f'{result.type}: {result.message}')
            elif isinstance(result, dict):
                # Normal events are returned as dicts
                pass #print(result)
        assert rr.is_preview == False

    def test_preview_docstring_sample(self):
        from splunklib import client
        from splunklib import results
        service = self.service # cheat
        job = service.jobs.create("search * | head 5")
        rr = results.JSONResultsReader(job.preview(output_mode='json'))
        for result in rr:
            if isinstance(result, results.Message):
                # Diagnostic messages may be returned in the results
                pass #print(f'{result.type}: {result.message}')
            elif isinstance(result, dict):
                # Normal events are returned as dicts
                pass #print(result)
        if rr.is_preview:
            pass #print("Preview of a running search job.")
        else:
            pass #print("Job is finished. Results are final.")

    def test_oneshot_docstring_sample(self):
        from splunklib import client
        from splunklib import results
        service = self.service # cheat
        rr = results.JSONResultsReader(service.jobs.oneshot("search * | head 5", output_mode='json'))
        for result in rr:
            if isinstance(result, results.Message):
                # Diagnostic messages may be returned in the results
                pass #print(f'{result.type}: {result.message}')
            elif isinstance(result, dict):
                # Normal events are returned as dicts
                pass #print(result)
        assert rr.is_preview == False

    def test_normal_job_with_garbage_fails(self):
        jobs = self.service.jobs
        try:
            bad_search = "abcd|asfwqqq"
            jobs.create(bad_search)
        except client.HTTPError as he:
            self.assertTrue('abcd' in str(he))
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
                'isZombie', 'keywords', 'label', 'messages',
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

    def test_get_job(self):
        sid = self.service.search("search index=_internal | head 10").sid
        self.assertTrue(len(sid) > 0)

        job = self.service.job(sid)
        self.assertIsNotNone(job)

        while not job.is_done():
            sleep(1)

        self.assertEqual(10, int(job["eventCount"]))
        self.assertEqual(10, int(job["resultCount"]))

class TestJobWithDelayedDone(testlib.SDKTestCase):
    def setUp(self):
        super().setUp()
        self.job = None

    def tearDown(self):
        super().tearDown()
        if self.job is not None:
            self.job.cancel()
            self.assertEventuallyTrue(lambda: self.job.sid not in self.service.jobs)

    @pytest.mark.app
    def test_enable_preview(self):
        self.install_app_from_collection("sleep_command")
        sleep_duration = 100
        self.query = "search index=_internal | sleep %d" % sleep_duration
        self.job = self.service.jobs.create(
            query=self.query,
            earliest_time="-1m",
            priority=5,
            latest_time="now")
        while not self.job.is_ready():
            pass
        self.assertEqual(self.job.content['isPreviewEnabled'], '0')
        self.job.enable_preview()

        def is_preview_enabled():
            is_done = self.job.is_done()
            if is_done:
                self.fail('Job finished before preview enabled.')
            return self.job.content['isPreviewEnabled'] == '1'

        self.assertEventuallyTrue(is_preview_enabled)

    @pytest.mark.app
    def test_setpriority(self):
        self.install_app_from_collection("sleep_command")
        sleep_duration = 100
        self.query = "search index=_internal | sleep %s" % sleep_duration
        self.job = self.service.jobs.create(
            query=self.query,
            earliest_time="-1m",
            priority=5,
            latest_time="now")

        # Note: You can only *decrease* the priority (i.e., 5 decreased to 3) of
        # a job unless Splunk is running as root. This is because Splunk jobs
        # are tied up with operating system processes and their priorities.

        if self.service._splunk_version[0] < 6:
            # BUG: Splunk 6 doesn't return priority until job is ready
            old_priority = int(self.job.content['priority'])
            self.assertEqual(5, old_priority)

        new_priority = 3
        self.job.set_priority(new_priority)

        if self.service._splunk_version[0] > 5:
            # BUG: Splunk 6 doesn't return priority until job is ready
            while not self.job.is_ready():
                pass

        def f():
            if self.job.is_done():
                self.fail("Job already done before priority was set.")
            return int(self.job.content['priority']) == new_priority

        self.assertEventuallyTrue(f, timeout=sleep_duration + 5)


class TestJob(testlib.SDKTestCase):
    def setUp(self):
        super().setUp()
        self.query = "search index=_internal | head 3"
        self.job = self.service.jobs.create(
            query=self.query,
            earliest_time="-1m",
            latest_time="now")

    def tearDown(self):
        super().tearDown()
        self.job.cancel()

    @_log_duration
    def test_get_preview_and_events(self):
        self.assertEventuallyTrue(self.job.is_done)
        self.assertLessEqual(int(self.job['eventCount']), 3)

        preview_stream = self.job.preview(output_mode='json')
        preview_r = results.JSONResultsReader(preview_stream)
        self.assertFalse(preview_r.is_preview)

        events_stream = self.job.events(output_mode='json')
        events_r = results.JSONResultsReader(events_stream)

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
        while not self.job.is_done():
            pass
        sleep(2)
        self.job.refresh()
        old_updated = self.job.state.updated
        self.job.touch()
        sleep(2)
        self.job.refresh()
        new_updated = self.job.state.updated

        # Touch will increase the updated time
        self.assertLess(old_updated, new_updated)


    def test_search_invalid_query_as_json(self):
        args = {
            'output_mode': 'json',
            'exec_mode': 'normal'
        }
        try:
            self.service.jobs.create('invalid query', **args)
        except SyntaxError as pe:
            self.fail("Something went wrong with parsing the REST API response. %s" % pe.message)
        except HTTPError as he:
            self.assertEqual(he.status, 400)
        except Exception as e:
            self.fail("Got some unexpected error. %s" % e.message)

    @pytest.mark.smoke
    def test_v1_job_fallback(self):
        self.assertEventuallyTrue(self.job.is_done)
        self.assertLessEqual(int(self.job['eventCount']), 3)

        preview_stream = self.job.preview(output_mode='json', search='| head 1')
        preview_r = results.JSONResultsReader(preview_stream)
        self.assertFalse(preview_r.is_preview)

        events_stream = self.job.events(output_mode='json', search='| head 1')
        events_r = results.JSONResultsReader(events_stream)
        
        results_stream = self.job.results(output_mode='json', search='| head 1')
        results_r = results.JSONResultsReader(results_stream)
        
        n_events = len([x for x in events_r if isinstance(x, dict)])
        n_preview = len([x for x in preview_r if isinstance(x, dict)])
        n_results = len([x for x in results_r if isinstance(x, dict)])

        # Fallback test for Splunk Version 9.0.2+
        if not self.service.disable_v2_api:
            self.assertTrue(client.PATH_JOBS_V2 in self.job.path)
        self.assertEqual(n_events, n_preview, n_results)


class TestResultsReader(unittest.TestCase):
    def test_results_reader(self):
        # Run jobs.export("search index=_internal | stats count",
        # earliest_time="rt", latest_time="rt") and you get a
        # streaming sequence of XML fragments containing results.
        test_dir = Path(__file__).parent
        data_file = test_dir / 'data' / 'results.xml'
        with io.open(str(data_file), mode='br') as input:
            reader = results.ResultsReader(input)
            self.assertFalse(reader.is_preview)
            N_results = 0
            N_messages = 0
            for r in reader:
                from collections import OrderedDict
                self.assertTrue(isinstance(r, OrderedDict)
                                or isinstance(r, results.Message))
                if isinstance(r, OrderedDict):
                    N_results += 1
                elif isinstance(r, results.Message):
                    N_messages += 1
            self.assertEqual(N_results, 4999)
            self.assertEqual(N_messages, 2)

    def test_results_reader_with_streaming_results(self):
        # Run jobs.export("search index=_internal | stats count",
        # earliest_time="rt", latest_time="rt") and you get a
        # streaming sequence of XML fragments containing results.
        test_dir = Path(__file__).parent
        data_file = test_dir / 'data' / 'streaming_results.xml'
        with io.open(str(data_file), 'br') as input:
            reader = results.ResultsReader(input)
            N_results = 0
            N_messages = 0
            for r in reader:
                from collections import OrderedDict
                self.assertTrue(isinstance(r, OrderedDict)
                                or isinstance(r, results.Message))
                if isinstance(r, OrderedDict):
                    N_results += 1
                elif isinstance(r, results.Message):
                    N_messages += 1
            self.assertEqual(N_results, 3)
            self.assertEqual(N_messages, 3)

    def test_xmldtd_filter(self):
        s = results._XMLDTDFilter(BytesIO(b"""<?xml asdf awe awdf=""><boris>Other stuf</boris><?xml dafawe \n asdfaw > ab"""))
        self.assertEqual(s.read(), b"<boris>Other stuf</boris> ab")

    def test_concatenated_stream(self):
        s = results._ConcatenatedStream(BytesIO(b"This is a test "),
                                       BytesIO(b"of the emergency broadcast system."))
        self.assertEqual(s.read(3), b"Thi")
        self.assertEqual(s.read(20), b's is a test of the e')
        self.assertEqual(s.read(), b'mergency broadcast system.')

if __name__ == "__main__":
    unittest.main()

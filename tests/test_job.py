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

from time import sleep

import testlib

import splunklib.client as client
import splunklib.results as results

class TestCase(testlib.TestCase):
    # UNDONE: Shouldn't the following assert something on exit?
    def check_properties(self, job, properties, secs = 10):
        while secs > 0 and len(properties) > 0:
            content = job.refresh().content

            # Try and check every property we specified. If we fail,
            # we'll try again later. If we succeed, delete it so we
            # don't check it again.
            for k, v in properties.items():
                try:
                    self.assertEqual(content[k], v)
                    
                    # Since we succeeded, delete it
                    del properties[k]
                except:
                    pass

            secs -= 1
            sleep(1)

    def check_job(self, job):
        self.check_entity(job)

        keys = [
            'cursorTime', 'delegate', 'diskUsage', 'dispatchState',
            'doneProgress', 'dropCount', 'earliestTime', 'eventAvailableCount',
            'eventCount', 'eventFieldCount', 'eventIsStreaming',
            'eventIsTruncated', 'eventSearch', 'eventSorting', 'isDone',
            'isFailed', 'isFinalized', 'isPaused', 'isPreviewEnabled',
            'isRealTimeSearch', 'isRemoteTimeline', 'isSaved', 'isSavedSearch',
            'isZombie', 'keywords', 'label', 'latestTime', 'messages',
            'numPreviews', 'priority', 'remoteSearch', 'reportSearch',
            'resultCount', 'resultIsStreaming', 'resultPreviewCount',
            'runDuration', 'scanCount', 'searchProviders', 'sid',
            'statusBuckets', 'ttl'
        ]
        for key in keys: self.assertTrue(key in job.content)

    def test_read(self):
        service = client.connect(**self.opts.kwargs)

        for job in service.jobs: 
            self.check_job(job)
            job.refresh()
            self.check_job(job)

    def test_crud(self):
        service = client.connect(**self.opts.kwargs)

        jobs = service.jobs

        if not service.indexes.contains("sdk-tests"):
            service.indexes.create("sdk-tests")
        service.indexes['sdk-tests'].clean()

        # Make sure we can create a job
        job = jobs.create("search index=sdk-tests")
        self.assertTrue(jobs.contains(job.sid))

        # Make sure we can cancel the job
        job.cancel()
        self.assertFalse(jobs.contains(job.sid))

        # Search for non-existant data
        job = jobs.create("search index=sdk-tests TERM_DOES_NOT_EXIST")
        testlib.wait(job, lambda job: job['isDone'] == '1')
        self.assertEqual(job['isDone'], '1')
        self.assertEqual(job['eventCount'], '0')
        job.finalize()
        
        # Create a new job
        job = jobs.create("search * | head 1 | stats count")
        self.assertTrue(jobs.contains(job.sid))

        # Set various properties on it
        job.disable_preview()
        job.pause()
        job.set_ttl(1000)
        job.set_priority(5)
        job.touch()
        job.refresh()

        # Assert that the properties got set properly
        self.check_properties(job, {
            'isPreviewEnabled': '0',
            'isPaused': '1',
            'ttl': '1000',
            'priority': '5'
        })

        # Set more properties
        job.enable_preview()
        job.unpause()
        job.finalize()
        job.refresh()

        # Assert that they got set properly
        self.check_properties(job, {
            'isPreviewEnabled': '1',
            'isPaused': '0',
            'isFinalized': '1'
        })

        job.cancel()
        self.assertFalse(jobs.contains(job.sid))

    def test_results(self):
        service = client.connect(**self.opts.kwargs)

        jobs = service.jobs

        # Run a new job to get the results, but we also make
        # sure that there is at least one event in the index already
        index = service.indexes['sdk-tests']
        old_event_count = int(index['totalEventCount'])
        if old_event_count == 0:
            index.submit("test event")
            testlib.wait(index, lambda index: index['totalEventCount'] == '1')

        job = jobs.create("search index=sdk-tests | head 1 | stats count")
        testlib.wait(job, lambda job: job['isDone'] == '1')
        self.assertEqual(job['isDone'], '1')

        # Fetch the results
        reader = results.ResultsReader(job.results())

        # The first one should always be RESULTS
        kind, result = reader.next()
        self.assertEqual(results.RESULTS, kind)
        self.assertEqual(int(result["preview"]), 0)

        # The second is always the actual result
        kind, result = reader.next()
        self.assertEqual(results.RESULT, kind)
        self.assertEqual(int(result["count"]), 1)

if __name__ == "__main__":
    testlib.main()

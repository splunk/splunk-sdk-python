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

def wait(entity, predicate, timeout=30):
    secs = 0
    done = False
    while not done and secs < timeout:
        sleep(1)
        secs += 1
        entity.refresh()
        done = predicate(entity)
    return entity

class TestCase(unittest.TestCase):
    def check_content(self, entity, **kwargs):
        for k, v in kwargs.iteritems(): 
            self.assertEqual(entity[k], str(v))

    def test_crud(self):
        saved_searches = client.connect(**opts.kwargs).saved_searches

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
        saved_searches = client.connect(**opts.kwargs).saved_searches

        if 'sdk-test1' in saved_searches:
            saved_searches.delete('sdk-test1')
        self.assertFalse('sdk-test1' in saved_searches)

        search = "search index=sdk-tests * earliest=-1m"
        saved_search = saved_searches.create('sdk-test1', search)
        self.assertEqual('sdk-test1', saved_search.name)
        self.assertTrue('sdk-test1' in saved_searches)

        job = saved_search.dispatch()
        wait(job, lambda job: bool(int(job['isDone'])))
        job.results().close()
        job.cancel()

        # Dispatch with some additional options
        kwargs = { 'dispatch.buckets': 100 }
        job = saved_search.dispatch(**kwargs)
        wait(job, lambda job: bool(int(job['isDone'])))
        job.timeline().close()
        job.cancel()

        saved_searches.delete('sdk-test1')
        self.assertFalse('sdk-test1' in saved_searches)

    def test_history(self):
        pass # UNDONE

    def test_read(self):
        saved_searches = client.connect(**opts.kwargs).saved_searches

        for saved_search in saved_searches:
            saved_search.content

if __name__ == "__main__":
    opts = parse(sys.argv[1:], {}, ".splunkrc")
    unittest.main(argv=sys.argv[:1])

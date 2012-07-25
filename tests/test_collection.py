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
    # Verify that the given collections interface behaves as expected
    def check_collection(self, collection):
        # Check item metadata
        try:
            metadata = collection.itemmeta()
            self.assertTrue(isinstance(metadata, dict))
            self.assertTrue(isinstance(metadata.access, dict))
            self.assertTrue(isinstance(metadata.fields, dict))
        except client.NotSupportedError: pass

        # Check various collection options
        collection.list() # Default
        collection.list(search="title=*")
        collection.list(sort_dir="asc")
        collection.list(sort_dir="desc")
        collection.list(sort_mode="auto")
        collection.list(sort_mode="alpha")
        collection.list(sort_mode="alpha_case")
        collection.list(sort_mode="num")

        # Retrieve the entire list
        items = collection.list()
        total = len(items)

        # Make sure the default list method returns all items
        items0 = collection.list()
        total0 = len(items0)
        self.assertEqual(total, total0)

        self.check_iterable(collection, total)

        # Page through contents one-at-a-time and check count
        count = 0
        for i in xrange(total):
            item = collection.list(offset=i, count=1)
            self.assertEqual(len(item), 1)
            count += 1
        self.assertEqual(count, total)

        # Page through the collection using various page sizes and make sure
        # the expected paging invariants hold.
        page_size = int(total/2)
        while page_size > 0:
            offset = 0
            while offset < total:
                page = collection.list(offset=offset, count=page_size)
                count = len(page)
                offset += count
                self.assertTrue(count == page_size or offset == total)
            self.assertEqual(offset, total)
            page_size = int(page_size/2) # Try half the page size

    # Verify that the given collection's iterator works as expected.
    def check_iterable(self, collection, count):
        # Iterate contents and make sure we see the expected count.
        seen = 0
        for item in collection: 
            seen += 1
            item.name
        self.assertEqual(seen, count)

    def test_apps(self):
        service = client.connect(**self.opts.kwargs)
        self.check_collection(service.apps)

    def test_event_types(self):
        service = client.connect(**self.opts.kwargs)
        self.check_collection(service.event_types)

    def test_indexes(self):
        service = client.connect(**self.opts.kwargs)
        self.check_collection(service.indexes)

    def test_inputs(self):
        # The Inputs collection is an aggregated view of the various REST API
        # input endpoints, and does not support the paging interface.
        service = client.connect(**self.opts.kwargs)
        count = len(service.inputs.list())
        print [x.name for x in service.inputs.list()]
        self.check_iterable(service.inputs, count)

    def test_jobs(self):
        # The Jobs REST API endpoint does not support the paging interface.
        service = client.connect(**self.opts.kwargs)
        count = len(service.jobs.list())
        self.check_iterable(service.jobs, count)

    def test_loggers(self):
        service = client.connect(**self.opts.kwargs)
        self.check_collection(service.loggers)

    def test_messages(self):
        service = client.connect(**self.opts.kwargs)
        self.check_collection(service.messages)

    def test_roles(self):
        service = client.connect(**self.opts.kwargs)
        self.check_collection(service.roles)

    def test_users(self):
        service = client.connect(**self.opts.kwargs)
        self.check_collection(service.users)

if __name__ == "__main__":
    testlib.main()


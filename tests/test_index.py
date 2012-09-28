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

from os import path
import time
import testlib

import splunklib.client as client

import logging

class IndexTest(testlib.TestCase):
    def setUp(self):
        super(IndexTest, self).setUp()
        self.index_name = testlib.tmpname()
        self.index = self.service.indexes.create(self.index_name)

    def tearDown(self):
        super(IndexTest, self).tearDown()
        # We can't delete an index with the REST API before Splunk
        # 5.0. In 4.x, we just have to leave them lying around until
        # someone cares to go clean them up. Unique naming prevents
        # clashes, though.
        if self.service.splunk_version[0] >= 5:
            self.service.indexes.delete(self.index_name)
        else:
            logging.warning("test_index.py:TestDeleteIndex: Skipped: cannot "
                            "delete indexes via the REST API in Splunk 4.x")


class IndexWithoutRestart(IndexTest):
    def test_integrity(self):
        self.check_entity(self.index)

    def test_default(self):
        default = self.service.indexes.default()
        self.assertTrue(isinstance(default, str))

    def test_disable_enable(self):
        self.index.disable()
        self.index.refresh()
        self.assertEqual(self.index['disabled'], '1')
        self.index.enable()
        self.index.refresh()
        self.assertEqual(self.index['disabled'], '0')

class IndexWithRestartTest(IndexTest):
    def setUp(self):
        super(IndexWithRestartTest, self).setUp()
        self.service.restart(timeout=300)
        self.index = self.service.indexes[self.index_name]

    def test_prefresh(self):
        index = self.service.indexes[self.index_name]
        self.assertEqual(self.index['disabled'], '0') # Index is prefreshed


    def test_submit(self):
        eventCount = int(self.index['totalEventCount'])
        self.assertEqual(self.index['sync'], '0')
        self.assertEqual(self.index['disabled'], '0')
        self.index.submit("Hello again!", sourcetype="Boris", host="meep")
        testlib.retry(self.index, 'totalEventCount', str(eventCount+1), step=1)
        self.assertEqual(self.index['totalEventCount'], str(eventCount+1))

    def test_submit_and_clean(self):
        # This fails on Ace beta because the index cannot be cleaned or deleted when disabled.
        self.index.refresh()
        originalCount = int(self.index['totalEventCount'])
        self.index.submit("Hello again!", sourcetype="Boris", host="meep")
        testlib.retry(self.index, 'totalEventCount', str(originalCount+1), step=1)
        self.assertEqual(self.index['totalEventCount'], str(originalCount+1))
        self.index.disable()
        self.index.clean()
        testlib.retry(self.index, 'totalEventCount', '0', step=1, times=60)
        self.index.refresh()
        self.assertEqual(self.index['totalEventCount'], '0')

    def test_submit_via_attach(self):
        eventCount = int(self.index['totalEventCount'])
        cn = self.index.attach()
        cn.send("Hello Boris!\r\n")
        cn.close()
        testlib.retry(self.index, 'totalEventCount', str(eventCount+1), step=1)
        self.index.refresh()
        self.assertEqual(self.index['totalEventCount'], str(eventCount+1))

    def test_submit_via_attached_socket(self):
        eventCount = int(self.index['totalEventCount'])
        f = self.index.attached_socket
        with f() as sock:
            sock.send('Hello world!\r\n')
        testlib.retry(self.index, 'totalEventCount', str(eventCount+1), step=1)
        self.assertEqual(self.index['totalEventCount'], str(eventCount+1))

    def test_upload(self):
        # The following test must run on machine where splunkd runs,
        # otherwise a failure is expected
        eventCount = int(self.index['totalEventCount'])
        testpath = path.dirname(path.abspath(__file__))
        self.index.upload(path.join(testpath, "testfile.txt"))
        testlib.retry(self.index, 'totalEventCount', str(eventCount+1), step=1)
        self.assertEqual(self.index['totalEventCount'], str(eventCount+1))

if __name__ == "__main__":
    testlib.main()

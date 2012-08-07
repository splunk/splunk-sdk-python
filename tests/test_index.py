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

import testlib

import splunklib.client as client

import logging

class IndexTest(testlib.TestCase):
    def setUp(self):
        testlib.TestCase.setUp(self)
        self.index_name = testlib.tmpname()
        self.index = self.service.indexes.create(self.index_name)

    def tearDown(self):
        # We can't delete an index with the REST API before Splunk
        # 5.0. In 4.x, we just have to leave them lying around until
        # someone cares to go clean them up. Unique naming prevents
        # clashes, though.
        if self.splunk_version >= 5:
            logging.warning("test_index.py:TestDeleteIndex: Skipped: cannot " 
                            "delete indexes via the REST API in Splunk 4.x")
            self.service.indexes.delete(self.index_name)

class TestIndexContentIntegrity(IndexTest):
    def test_integrity(self):
        self.check_entity(self.index)

class TestIndexIsPrefreshed(IndexTest):
    def test_prefreshed(self):
        # Make sure a new index has its contents already loaded.
        self.assertEqual(self.index['disabled'], '0')

class TestDisableEnable(IndexTest):
    def test_disable_enable(self):
        self.index.disable()
        self.index.refresh()
        self.assertEqual(self.index['disabled'], '1')
        self.index.enable()
        self.index.refresh()
        self.assertEqual(self.index['disabled'], '0')

class TestSubmit(IndexTest):
    def test_submit(self):
        # At the moment, restarting the newly created index makes this
        # work. I'm waiting to see if there's a better solution.
        # Without a restart, you get ghastly messages about
        # unconfigured indexes, and submission doesn't work.
        # testlib.restart(self.service)
        eventCount = int(self.index['totalEventCount'])
        self.assertEqual(self.index['sync'], '0')
        self.assertEqual(self.index['disabled'], '0')
        self.index.submit("Hello again!", sourcetype="Boris", host="meep")
        # testlib.wait(self.index, lambda idx: int(idx['totalEventCount']) > 0, timeout=2)
        self.index.refresh()
        self.assertEqual(int(self.index['totalEventCount']), eventCount+1)

class TestCannotCleanEnabledIndex(IndexTest):
    def test_cannot_clean_enabled(self):
        self.assertEqual(self.index['disabled'], '0')
        self.assertRaises(client.IllegalOperationException, self.index.clean)

class TestSubmitAndCleanIndex(IndexTest):
    def test_submit_and_clean(self):
        self.index.submit("Hello again!", sourcetype="Boris", host="meep")
        self.index.disable()
        self.index.clean()
        self.index.refresh()
        self.assertEqual(self.index['totalEventCount'], '0')

class TestSubmitViaAttach(IndexTest):
    def test_submit_via_attach(self):
        eventCount = int(self.index['totalEventCount'])
        cn = self.index.attach()
        cn.send("Hello Boris!\r\n")
        cn.close()
        self.index.refresh()
        self.assertEqual(int(self.index['totalEventCount']), eventCount+1)

class TestUpload(IndexTest):
    def test_upload(self):
        # The following test must run on machine where splunkd runs,
        # otherwise a failure is expected
        eventCount = int(self.index['totalEventCount'])
        testpath = path.dirname(path.abspath(__file__))
        self.index.upload(path.join(testpath, "testfile.txt"))
        self.index.refresh()
        self.assertEqual(int(self.index['totalEventCount']), eventCount+1)

if __name__ == "__main__":
    testlib.main()

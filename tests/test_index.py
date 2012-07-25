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

class TestCase(testlib.TestCase):
    def setUp(self):
        testlib.TestCase.setUp(self)
        self.service = client.connect(**self.opts.kwargs)
        if not self.service.indexes.contains("sdk-tests"):
            self.service.indexes.create("sdk-tests")
        self.assertTrue(self.service.indexes.contains("sdk-tests"))
        self.index = self.service.indexes['sdk-tests']

    def check_index(self, index):
        self.check_entity(index)
        keys = [
            'thawedPath', 'quarantineFutureSecs',
            'isInternal', 'maxHotBuckets', 'disabled', 'homePath',
            'compressRawdata', 'maxWarmDBCount', 'frozenTimePeriodInSecs',
            'memPoolMB', 'maxHotSpanSecs', 'minTime', 'blockSignatureDatabase',
            'serviceMetaPeriod', 'coldToFrozenDir', 'quarantinePastSecs',
            'maxConcurrentOptimizes', 'maxMetaEntries', 'minRawFileSyncSecs',
            'maxMemMB', 'maxTime', 'partialServiceMetaPeriod', 'maxHotIdleSecs',
            'coldToFrozenScript', 'thawedPath_expanded', 'coldPath_expanded',
            'defaultDatabase', 'throttleCheckPeriod', 'totalEventCount',
            'enableRealtimeSearch', 'indexThreads', 'maxDataSize',
            'currentDBSizeMB', 'homePath_expanded', 'blockSignSize',
            'syncMeta', 'assureUTF8', 'rotatePeriodInSecs', 'sync',
            'suppressBannerList', 'rawChunkSizeBytes', 'coldPath',
            'maxTotalDataSizeMB'
        ]
        for key in keys: self.assertTrue(key in index.content)

    def test_read(self):
        for index in self.service.indexes: 
            self.check_index(index)
            index.refresh()
            self.check_index(index)

    def test_disable(self):
        self.index.disable()
        # testlib.restart(self.service)
        self.index.refresh()
        self.assertEqual(self.index['disabled'], '1')

    def test_enable(self):
        self.index.enable()
        # testlib.restart(self.service)
        self.index.refresh()
        self.assertEqual(self.index['disabled'], '0')

    def test_clean(self):
        self.index.clean()
        self.index.refresh()
        self.assertEqual(self.index['totalEventCount'], '0')

    def test_attach(self):
        self.index.refresh()
        count = int(self.index['totalEventCount'])
        cn = self.index.attach()
        cn.send("Hello Boris!\r\n")
        cn.close()
        def f():
            self.index.refresh()
            n = int(self.index['totalEventCount'])
            return n
        self.assertEventuallyEqual(f, count+1)

    def test_submit(self):
        self.index.refresh()
        count = int(self.index['totalEventCount'])
        self.index.submit("Hello again!")
        self.assertEventuallyEqual(lambda: self.index.refresh() and int(self.index['totalEventCount']), count+1, timeout=60)

    def test_upload(self):
        # The following test must run on machine where splunkd runs,
        # otherwise a failure is expected
        self.index.refresh()
        count = int(self.index['totalEventCount'])
        testpath = path.dirname(path.abspath(__file__))
        self.index.upload(path.join(testpath, "testfile.txt"))
        self.assertEventuallyEqual(lambda: self.index.refresh() and int(self.index['totalEventCount']), count+1, timeout=60)

if __name__ == "__main__":
    testlib.main()

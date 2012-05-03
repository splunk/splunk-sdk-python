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
        service = client.connect(**self.opts.kwargs)

        for index in service.indexes: 
            self.check_index(index)
            index.refresh()
            self.check_index(index)

    def test_crud(self):
        service = client.connect(**self.opts.kwargs)

        if not service.indexes.contains("sdk-tests"):
            service.indexes.create("sdk-tests")
        self.assertTrue(service.indexes.contains("sdk-tests"))

        index = service.indexes['sdk-tests']

        index.disable()
        index.refresh()
        self.assertEqual(index['disabled'], '1')

        index.enable()
        index.refresh()
        self.assertEqual(index['disabled'], '0')
            
        index.clean()
        index.refresh()
        self.assertEqual(index['totalEventCount'], '0')

        cn = index.attach()
        cn.write("Hello World!")
        cn.close()
        testlib.wait(index, lambda index: index['totalEventCount'] == '1')
        self.assertEqual(index['totalEventCount'], '1')

        index.submit("Hello again!!")
        testlib.wait(index, lambda index: index['totalEventCount'] == '2')
        self.assertEqual(index['totalEventCount'], '2')

        # The following test must run on machine where splunkd runs,
        # otherwise a failure is expected
        testpath = path.dirname(path.abspath(__file__))
        index.upload(path.join(testpath, "testfile.txt"))
        testlib.wait(index, lambda index: index['totalEventCount'] == '3')
        self.assertEqual(index['totalEventCount'], '3')

        index.clean()
        index.refresh()
        self.assertEqual(index['totalEventCount'], '0')

if __name__ == "__main__":
    testlib.main()

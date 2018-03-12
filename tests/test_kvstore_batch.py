#!/usr/bin/env python
#
# Copyright 2011-2014 Splunk, Inc.
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

from __future__ import absolute_import
from tests import testlib
from splunklib.six.moves import range
try:
    import unittest
except ImportError:
    import unittest2 as unittest
import splunklib.client as client

class KVStoreBatchTestCase(testlib.SDKTestCase):
    def setUp(self):
        super(KVStoreBatchTestCase, self).setUp()
        self.service.namespace['owner'] = 'nobody'
        self.service.namespace['app'] = 'search'
        confs = self.service.kvstore
        if ('test' in confs):
            confs['test'].delete()
        confs.create('test')

        self.col = confs['test'].data

    def test_insert_find_update_data(self):
        data = [{'_key': str(x), 'data': '#' + str(x), 'num': x} for x in range(1000)]
        self.col.batch_save(*data)

        testData = self.col.query(sort='num')
        self.assertEqual(len(testData), 1000)

        for x in range(1000):
            self.assertEqual(testData[x]['_key'], str(x))
            self.assertEqual(testData[x]['data'], '#' + str(x))
            self.assertEqual(testData[x]['num'], x)

        data = [{'_key': str(x), 'data': '#' + str(x + 1), 'num': x + 1} for x in range(1000)]
        self.col.batch_save(*data)

        testData = self.col.query(sort='num')
        self.assertEqual(len(testData), 1000)

        for x in range(1000):
            self.assertEqual(testData[x]['_key'], str(x))
            self.assertEqual(testData[x]['data'], '#' + str(x + 1))
            self.assertEqual(testData[x]['num'], x + 1)

        query = [{"query": {"num": x + 1}} for x in range(100)]
        testData = self.col.batch_find(*query)

        self.assertEqual(len(testData), 100)
        testData.sort(key=lambda x: x[0]['num'])

        for x in range(100):
            self.assertEqual(testData[x][0]['_key'], str(x))
            self.assertEqual(testData[x][0]['data'], '#' + str(x + 1))
            self.assertEqual(testData[x][0]['num'], x + 1)
   

    def tearDown(self):
        confs = self.service.kvstore
        if ('test' in confs):
            confs['test'].delete()

if __name__ == "__main__":
    try:
        import unittest2 as unittest
    except ImportError:
        import unittest
    unittest.main()

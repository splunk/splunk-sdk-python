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
import json
from tests import testlib
from splunklib.six.moves import range
try:
    import unittest
except ImportError:
    import unittest2 as unittest
import splunklib.client as client

class KVStoreDataTestCase(testlib.SDKTestCase):
    def setUp(self):
        super(KVStoreDataTestCase, self).setUp()
        self.service.namespace['owner'] = 'nobody'
        self.service.namespace['app'] = 'search'
        self.confs = self.service.kvstore
        if ('test' in self.confs):
            self.confs['test'].delete()
        self.confs.create('test')

        self.col = self.confs['test'].data

    def test_insert_query_delete_data(self):
        for x in range(50):
            self.col.insert(json.dumps({'_key': str(x), 'data': '#' + str(x), 'num': x}))
        self.assertEqual(len(self.col.query()), 50)
        self.assertEqual(len(self.col.query(query='{"num": 10}')), 1)
        self.assertEqual(self.col.query(query='{"num": 10}')[0]['data'], '#10')
        self.col.delete(json.dumps({'num': {'$gt': 39}}))
        self.assertEqual(len(self.col.query()), 40)
        self.col.delete()
        self.assertEqual(len(self.col.query()), 0)

    def test_update_delete_data(self):
        for x in range(50):
            self.col.insert(json.dumps({'_key': str(x), 'data': '#' + str(x), 'num': x}))
        self.assertEqual(len(self.col.query()), 50)
        self.assertEqual(self.col.query(query='{"num": 49}')[0]['data'], '#49')
        self.col.update(str(49), json.dumps({'data': '#50', 'num': 50}))
        self.assertEqual(len(self.col.query()), 50)
        self.assertEqual(self.col.query(query='{"num": 50}')[0]['data'], '#50')
        self.assertEqual(len(self.col.query(query='{"num": 49}')), 0)
        self.col.delete_by_id(49)
        self.assertEqual(len(self.col.query(query='{"num": 50}')), 0)

    def test_query_data(self):
        if ('test1' in self.confs):
            self.confs['test1'].delete() 
        self.confs.create('test1')
        self.col = self.confs['test1'].data
        for x in range(10):
            self.col.insert(json.dumps({'_key': str(x), 'data': '#' + str(x), 'num': x}))
        data = self.col.query(sort='data:-1', skip=9)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['data'], '#0')
        data = self.col.query(sort='data:1')
        self.assertEqual(data[0]['data'], '#0')
        data = self.col.query(limit=2, skip=9)
        self.assertEqual(len(data), 1)
         

    def test_invalid_insert_update(self):
        self.assertRaises(client.HTTPError, lambda: self.col.insert('NOT VALID DATA'))
        id = self.col.insert(json.dumps({'foo': 'bar'}))['_key']
        self.assertRaises(client.HTTPError, lambda: self.col.update(id, 'NOT VALID DATA'))
        self.assertEqual(self.col.query_by_id(id)['foo'], 'bar')

    def test_params_data_type_conversion(self):
        self.confs['test'].post(**{'field.data': 'number', 'accelerated_fields.data': '{"data": -1}'})
        for x in range(50):
            self.col.insert(json.dumps({'_key': str(x), 'data': str(x), 'ignore': x}))
        data = self.col.query(sort='data:-1', limit=20, fields='data,_id:0', skip=10)
        self.assertEqual(len(data), 20)
        for x in range(20):
            self.assertEqual(data[x]['data'], 39 - x)
            self.assertTrue(not 'ignore' in data[x])
            self.assertTrue(not '_key' in data[x])

    def tearDown(self):
        if ('test' in self.confs):
            self.confs['test'].delete()

if __name__ == "__main__":
    try:
        import unittest2 as unittest
    except ImportError:
        import unittest
    unittest.main()

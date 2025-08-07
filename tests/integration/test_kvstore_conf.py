#!/usr/bin/env python
#
# Copyright 2011-2020 Splunk, Inc.
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

import json
from tests import testlib
from splunklib import client


class KVStoreConfTestCase(testlib.SDKTestCase):
    def setUp(self):
        super().setUp()
        self.service.namespace['app'] = 'search'
        self.confs = self.service.kvstore
        if ('test' in self.confs):
            self.confs['test'].delete()

    def test_owner_restriction(self):
        self.service.kvstore_owner = 'admin'
        self.assertRaises(client.HTTPError, lambda: self.confs.list())
        self.service.kvstore_owner = 'nobody'

    def test_create_delete_collection(self):
        self.confs.create('test')
        self.assertTrue('test' in self.confs)
        self.confs['test'].delete()
        self.assertTrue('test' not in self.confs)

    def test_create_fields(self):
        self.confs.create('test', accelerated_fields={'ind1':{'a':1}}, fields={'a':'number1'})
        self.assertEqual(self.confs['test']['field.a'], 'number1')
        self.assertEqual(self.confs['test']['accelerated_fields.ind1'], {"a": 1})
        self.confs['test'].delete()

    def test_update_collection(self):
        self.confs.create('test')
        val = {"a": 1}
        self.confs['test'].post(**{'accelerated_fields.ind1': json.dumps(val), 'field.a': 'number'})
        self.assertEqual(self.confs['test']['field.a'], 'number')
        self.assertEqual(self.confs['test']['accelerated_fields.ind1'], {"a": 1})
        self.confs['test'].delete()

    def test_update_accelerated_fields(self):
        self.confs.create('test', accelerated_fields={'ind1':{'a':1}})
        self.assertEqual(self.confs['test']['accelerated_fields.ind1'], {'a': 1})
        # update accelerated_field value
        self.confs['test'].update_accelerated_field('ind1', {'a': -1})
        self.assertEqual(self.confs['test']['accelerated_fields.ind1'], {'a': -1})
        self.confs['test'].delete()

    def test_update_fields(self):
        self.confs.create('test')
        self.confs['test'].post(**{'field.a': 'number'})
        self.assertEqual(self.confs['test']['field.a'], 'number')
        self.confs['test'].update_field('a', 'string')
        self.assertEqual(self.confs['test']['field.a'], 'string')
        self.confs['test'].delete()

    def test_create_unique_collection(self):
        self.confs.create('test')
        self.assertTrue('test' in self.confs)
        self.assertRaises(client.HTTPError, lambda: self.confs.create('test'))
        self.confs['test'].delete()

    def test_overlapping_collections(self):
        self.service.namespace['app'] = 'system'
        self.confs.create('test')
        self.service.namespace['app'] = 'search'
        self.confs.create('test')
        self.assertEqual(self.confs['test']['eai:appName'], 'search')
        self.service.namespace['app'] = 'system'
        self.assertEqual(self.confs['test']['eai:appName'], 'system')
        self.service.namespace['app'] = 'search'
        self.confs['test'].delete()
        self.confs['test'].delete()

    def tearDown(self):
        if 'test' in self.confs:
            self.confs['test'].delete()


if __name__ == "__main__":
    import unittest

    unittest.main()

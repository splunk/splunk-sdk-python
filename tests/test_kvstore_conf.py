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
try:
    import unittest
except ImportError:
    import unittest2 as unittest
import splunklib.client as client

class KVStoreConfTestCase(testlib.SDKTestCase):
    def setUp(self):
        super(KVStoreConfTestCase, self).setUp()
        self.service.namespace['owner'] = 'nobody'
        self.service.namespace['app'] = 'search'
        self.confs = self.service.kvstore
        if ('test' in self.confs):
            self.confs['test'].delete()

    def test_owner_restriction(self):
        self.service.namespace['owner'] = 'admin'
        self.assertRaises(client.HTTPError, lambda: self.confs.list())
        self.service.namespace['owner'] = 'nobody'

    def test_create_delete_collection(self):
        self.confs.create('test')
        self.assertTrue('test' in self.confs)
        self.confs['test'].delete()
        self.assertTrue(not 'test' in self.confs)

    def test_update_collection(self):
        self.confs.create('test')
        self.confs['test'].post(**{'accelerated_fields.ind1': '{"a": 1}', 'field.a': 'number'})
        self.assertEqual(self.confs['test']['field.a'], 'number')
        self.assertEqual(self.confs['test']['accelerated_fields.ind1'], '{"a": 1}')
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

    """    
    def test_create_accelerated_fields_fields(self):
        self.confs.create('test', indexes={'foo': '{"foo": 1}', 'bar': {'bar': -1}}, **{'field.foo': 'string'})       
        self.assertEqual(self.confs['test']['accelerated_fields.foo'], '{"foo": 1}')
        self.assertEqual(self.confs['test']['field.foo'], 'string')
        self.assertRaises(client.HTTPError, lambda: self.confs['test'].post(**{'accelerated_fields.foo': 'THIS IS INVALID'}))
        self.assertEqual(self.confs['test']['accelerated_fields.foo'], '{"foo": 1}')
        self.confs['test'].update_accelerated_fields('foo', '')
        self.assertEqual(self.confs['test']['accelerated_fields.foo'], None)
    """
    
    def tearDown(self):
        if ('test' in self.confs):
            self.confs['test'].delete()

if __name__ == "__main__":
    try:
        import unittest2 as unittest
    except ImportError:
        import unittest
    unittest.main()

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

test_inputs = [{'kind': 'tcp', 'name': '9999', 'host': 'sdk-test'},
               {'kind': 'udp', 'name': '9999', 'host': 'sdk-test'}]

class TestRead(testlib.TestCase):
    def test_read(self):
        inputs = self.service.inputs
        # count doesn't work on inputs; known problem tested for in
        # test_collection.py. This test will speed up dramatically
        # when that's fixed.
        for item in inputs.list(count=5): 
            self.check_entity(item)
            item.refresh()
            self.check_entity(item)

    def test_read_kind(self):
        inputs = self.service.inputs
        for kind in inputs.kinds:
            # count doesn't work on inputs; known problem tested for in
            # test_collection.py. This test will speed up dramatically
            # when that's fixed.
            for item in inputs.list(kind, count=3):
                self.assertEqual(item.kind, kind)

class TestInput(testlib.TestCase):
    def setUp(self):
        testlib.TestCase.setUp(self)
        inputs = self.service.inputs
        self.test_entities = {}
        for test_input in test_inputs:
            self.test_entities[test_input['kind']] = \
                inputs.create(**test_input)

    def tearDown(self):
        testlib.TestCase.tearDown(self)
        for test_input in test_inputs:
            try:
                self.service.inputs.delete(
                    kind=test_input['kind'],
                    name=test_input['name'])
            except KeyError:
                pass

    def test_create(self):
        inputs = self.service.inputs
        for test_input in test_inputs:
            kind, name, host = test_input['kind'], test_input['name'], test_input['host']
            entity = self.test_entities[kind]
            entity = inputs[kind, name]
            self.check_entity(entity)
            self.assertEqual(entity.name, name)
            self.assertEqual(entity.kind, kind)
            self.assertEqual(entity.host, host)

    def test_read(self):
        inputs = self.service.inputs
        for test_input in test_inputs:
            kind, name = test_input['kind'], test_input['name']
            this_entity = self.test_entities[kind]
            read_entity = inputs[kind, name]
            self.assertEqual(this_entity.kind, read_entity.kind)
            self.assertEqual(this_entity.name, read_entity.name)
            self.assertEqual(this_entity.host, read_entity.host)

    def test_update(self):
        inputs = self.service.inputs
        for test_input in test_inputs:
            kind, name = test_input['kind'], test_input['name']
            entity = self.test_entities[kind, name]
            kwargs = {'host': 'foo', 'sourcetype': 'bar'}
            entity.update(**kwargs)
            entity.refresh()
            self.assertEqual(entity.host, kwargs['host'])
            self.assertEqual(entity.sourcetype, kwargs['sourcetype'])

    def test_delete(self):
        inputs = self.service.inputs
        for test_input in test_inputs:
            kind, name = test_input['kind'], test_input['name']
            input_entity = self.service.inputs[kind,name]
            self.assertTrue(name in inputs)
            self.assertTrue((kind,name) in inputs)
            self.service.inputs.delete(kind['name'])
            self.assertFalse(name in inputs)
            self.assertFalse((kind,name) in inputs)
            self.assertRaises(client.EntityDeletedException,
                              input_entity.refresh)
                              

if __name__ == "__main__":
    testlib.main()

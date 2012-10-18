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
import logging

import splunklib.client as client

class TestRead(testlib.SDKTestCase):
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
        logging.debug("Input kinds: %s", inputs.kinds)
        for kind in inputs.kinds:
            for item in inputs.list(kind, count=3):
                self.assertEqual(item.kind, kind)

    def test_inputs_list_on_one_kind(self):
        self.service.inputs.list('monitor')

    def test_inputs_list_on_one_kind_with_count(self):
        N = 10
        expected = [x.name for x in self.service.inputs.list('monitor')[:10]]
        found = [x.name for x in self.service.inputs.list('monitor', count=10)]
        self.assertEqual(expected, found)

    def test_inputs_list_on_one_kind_with_offset(self):
        N = 2
        expected = [x.name for x in self.service.inputs.list('monitor')[N:]]
        found = [x.name for x in self.service.inputs.list('monitor', offset=N)]
        self.assertEqual(expected, found)

    def test_inputs_list_on_one_kind_with_search(self):
        search = "SPLUNK"
        expected = [x.name for x in self.service.inputs.list('monitor') if search in x.name]
        found = [x.name for x in self.service.inputs.list('monitor', search=search)]
        self.assertEqual(expected, found)

    def test_oneshot(self):
        index_name = testlib.tmpname()
        index = self.service.indexes.create(index_name)
        self.restartSplunk(timeout=120)
        index = self.service.indexes[index_name]
        eventCount = int(index['totalEventCount'])
        from os import path
        testpath = path.dirname(path.abspath(__file__))
        self.service.inputs.oneshot(path.join(testpath, 'testfile.txt'), index=index_name)
        self.assertEventuallyEqual(
            str(eventCount+1),
            lambda: index.refresh()['totalEventCount']
        )

    def test_oneshot_on_nonexistant_file(self):
        name = testlib.tmpname()
        from os import path
        self.assertFalse(path.exists(name))
        self.assertRaises(client.OperationFailedException,
            self.service.inputs.oneshot, name)


class TestInput(testlib.SDKTestCase):
    def setUp(self):
        super(TestInput, self).setUp()
        inputs = self.service.inputs
        test_inputs = [{'kind': 'tcp', 'name': '9999', 'host': 'sdk-test'},
                       {'kind': 'udp', 'name': '9999', 'host': 'sdk-test'}]
        self._test_entities = {}

        base_port = 10000
        while True:
            if str(base_port) in inputs:
                base_port += 1
            else:
                break

        self._test_entities['tcp'] = \
            inputs.create('tcp', str(base_port), host='sdk-test')
        self._test_entities['udp'] = \
            inputs.create('udp', str(base_port), host='sdk-test')

    def tearDown(self):
        super(TestInput, self).tearDown()
        for entity in self._test_entities.itervalues():
            try:
                self.service.inputs.delete(
                    kind=entity.kind,
                    name=entity.name)
            except KeyError:
                pass

    def test_list(self):
        inputs = self.service.inputs
        input_list = inputs.list()
        self.assertTrue(len(input_list) > 0)
        for input in input_list:
            self.assertTrue(input.name is not None)

    def test_lists_modular_inputs(self):
        if self.service.splunk_version[0] < 5:
            return # Modular inputs don't exist prior to 5.0
        else:
            inputs = self.service.inputs
            if ('test2','abcd') not in inputs:
                inputs.create('test2', 'abcd', field1='boris')
            input = inputs['test2', 'abcd']
            self.assertEqual(input.field1, 'boris')


    def test_create(self):
        inputs = self.service.inputs
        for entity in self._test_entities.itervalues():
            self.check_entity(entity)
            self.assertTrue(isinstance(entity, client.Input))

    def test_get_kind_list(self):
        inputs = self.service.inputs
        kinds = inputs._get_kind_list()
        self.assertTrue('tcp/raw' in kinds)

    def test_read(self):
        inputs = self.service.inputs
        for this_entity in self._test_entities.itervalues():
            kind, name = this_entity.kind, this_entity.name
            read_entity = inputs[kind, name]
            self.assertEqual(this_entity.kind, read_entity.kind)
            self.assertEqual(this_entity.name, read_entity.name)
            self.assertEqual(this_entity.host, read_entity.host)

    def test_update(self):
        inputs = self.service.inputs
        for entity in self._test_entities.itervalues():
            kind, name = entity.kind, entity.name
            kwargs = {'host': 'foo', 'sourcetype': 'bar'}
            entity.update(**kwargs)
            entity.refresh()
            self.assertEqual(entity.host, kwargs['host'])
            self.assertEqual(entity.sourcetype, kwargs['sourcetype'])

    def test_delete(self):
        inputs = self.service.inputs
        remaining = len(self._test_entities)-1
        for input_entity in self._test_entities.itervalues():
            name = input_entity.name
            kind = input_entity.kind
            self.assertTrue(name in inputs)
            self.assertTrue((kind,name) in inputs)
            if remaining == 0:
                inputs.delete(name)
                self.assertFalse(name in inputs)
            else:
                self.assertRaises(client.AmbiguousReferenceException,
                                  inputs.delete, name)
                self.service.inputs.delete(kind, name)
                self.assertFalse((kind,name) in inputs)
            self.assertRaises(client.EntityDeletedException,
                              input_entity.refresh)
            remaining -= 1
                              

if __name__ == "__main__":
    testlib.main()

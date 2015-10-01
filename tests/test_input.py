#!/usr/bin/env python
#
# Copyright 2011-2015 Splunk, Inc.
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
from splunklib.binding import HTTPError

import testlib
import logging
try:
    import unittest
except ImportError:
    import unittest2 as unittest

import splunklib.client as client

def highest_port(service, base_port, *kinds):
    """Find the first port >= base_port not in use by any input in kinds."""
    highest_port = base_port
    for input in service.inputs.list(*kinds):
        port = int(input.name.split(':')[-1])
        highest_port = max(port, highest_port)
    return highest_port

class TestTcpInputNameHandling(testlib.SDKTestCase):
    def setUp(self):
        super(TestTcpInputNameHandling, self).setUp()
        self.base_port = highest_port(self.service, 10000, 'tcp', 'splunktcp', 'udp') + 1

    def tearDown(self):
        for input in self.service.inputs.list('tcp', 'splunktcp'):
            port = int(input.name.split(':')[-1])
            if port >= self.base_port:
                input.delete()
        super(TestTcpInputNameHandling, self).tearDown()

    def create_tcp_input(self, base_port, kind, **options):
        port = base_port
        while True: # Find the next unbound port
            try:
                input = self.service.inputs.create(str(port), kind, **options)
                return input
            except client.HTTPError as he:
                if he.status == 400:
                    port += 1

    def test_create_tcp_port(self):
        for kind in ['tcp', 'splunktcp']:
            input = self.service.inputs.create(str(self.base_port), kind)
            self.check_entity(input)
            input.delete()

    def test_cannot_create_with_restrictToHost_in_name(self):
        self.assertRaises(
            client.HTTPError,
            lambda: self.service.inputs.create('boris:10000', 'tcp')
        )

    def test_create_tcp_ports_with_restrictToHost(self):
        for kind in ['tcp', 'splunktcp']: # Multiplexed UDP ports are not supported
            # Make sure we can create two restricted inputs on the same port
            boris = self.service.inputs.create(str(self.base_port), kind, restrictToHost='boris')
            natasha = self.service.inputs.create(str(self.base_port), kind, restrictToHost='natasha')
            # And that they both function
            boris.refresh()
            natasha.refresh()
            self.check_entity(boris)
            self.check_entity(natasha)
            boris.delete()
            natasha.delete()

    def test_restricted_to_unrestricted_collision(self):
        for kind in ['tcp', 'splunktcp', 'udp']:
            restricted = self.service.inputs.create(str(self.base_port), kind, restrictToHost='boris')
            self.assertTrue('boris:' + str(self.base_port) in self.service.inputs)
            self.assertRaises(
                client.HTTPError,
                lambda: self.service.inputs.create(str(self.base_port), kind)
            )
            restricted.delete()

    def test_unrestricted_to_restricted_collision(self):
        for kind in ['tcp', 'splunktcp', 'udp']:
            unrestricted = self.service.inputs.create(str(self.base_port), kind)
            self.assertTrue(str(self.base_port) in self.service.inputs)
            self.assertRaises(
                client.HTTPError,
                lambda: self.service.inputs.create(str(self.base_port), kind, restrictToHost='boris')
            )
            unrestricted.delete()

    def test_update_restrictToHost_fails(self):
        for kind in ['tcp', 'splunktcp']: # No UDP, since it's broken in Splunk
            boris = self.create_tcp_input(self.base_port, kind, restrictToHost='boris')

            self.assertRaises(
                client.IllegalOperationException,
                lambda: boris.update(restrictToHost='hilda')
            )

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
        if not self.app_collection_installed():
            print "Test requires sdk-app-collection. Skipping."
            return
        self.install_app_from_collection('file_to_upload')

        index_name = testlib.tmpname()
        index = self.service.indexes.create(index_name)
        self.assertEventuallyTrue(lambda: index.refresh() and index['disabled'] == '0')

        eventCount = int(index['totalEventCount'])

        path = self.pathInApp("file_to_upload", ["log.txt"])
        self.service.inputs.oneshot(path, index=index_name)

        def f():
            index.refresh()
            return int(index['totalEventCount']) == eventCount+4
        self.assertEventuallyTrue(f, timeout=60)

    def test_oneshot_on_nonexistant_file(self):
        name = testlib.tmpname()
        self.assertRaises(HTTPError,
            self.service.inputs.oneshot, name)

class TestInput(testlib.SDKTestCase):
    def setUp(self):
        super(TestInput, self).setUp()
        inputs = self.service.inputs
        unrestricted_port = str(highest_port(self.service, 10000, 'tcp', 'splunktcp', 'udp')+1)
        restricted_port = str(highest_port(self.service, int(unrestricted_port)+1, 'tcp', 'splunktcp')+1)
        test_inputs = [{'kind': 'tcp', 'name': unrestricted_port, 'host': 'sdk-test'},
                       {'kind': 'udp', 'name': unrestricted_port, 'host': 'sdk-test'},
                       {'kind': 'tcp', 'name': 'boris:' + restricted_port, 'host': 'sdk-test'}]
        self._test_entities = {}

        self._test_entities['tcp'] = \
            inputs.create(unrestricted_port, 'tcp', host='sdk-test')
        self._test_entities['udp'] = \
            inputs.create(unrestricted_port, 'udp', host='sdk-test')
        self._test_entities['restrictedTcp'] = \
            inputs.create(restricted_port, 'tcp', restrictToHost='boris')

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
            print "Modular inputs don't exist prior to Splunk 5.0. Skipping."
            return
        elif not self.app_collection_installed():
            print "Test requires sdk-app-collection. Skipping."
            return
        else:
            # Install modular inputs to list, and restart
            # so they'll show up.
            self.install_app_from_collection("modular-inputs")
            self.uncheckedRestartSplunk()

            inputs = self.service.inputs
            if ('abcd','test2') not in inputs:
                inputs.create('abcd', 'test2', field1='boris')

            input = inputs['abcd', 'test2']
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
            read_entity = inputs[name, kind]
            self.assertEqual(this_entity.kind, read_entity.kind)
            self.assertEqual(this_entity.name, read_entity.name)
            self.assertEqual(this_entity.host, read_entity.host)

    def test_update(self):
        inputs = self.service.inputs
        for entity in self._test_entities.itervalues():
            kind, name = entity.kind, entity.name
            kwargs = {'host': 'foo'}
            entity.update(**kwargs)
            entity.refresh()
            self.assertEqual(entity.host, kwargs['host'])

    def test_delete(self):
        inputs = self.service.inputs
        remaining = len(self._test_entities)-1
        for input_entity in self._test_entities.itervalues():
            name = input_entity.name
            kind = input_entity.kind
            self.assertTrue(name in inputs)
            self.assertTrue((name,kind) in inputs)
            if remaining == 0:
                inputs.delete(name)
                self.assertFalse(name in inputs)
            else:
                if not name.startswith('boris'):
                    self.assertRaises(client.AmbiguousReferenceException,
                        inputs.delete, name)
                self.service.inputs.delete(name, kind)
                self.assertFalse((name, kind) in inputs)
            self.assertRaises(client.HTTPError,
                              input_entity.refresh)
            remaining -= 1


if __name__ == "__main__":
    try:
        import unittest2 as unittest
    except ImportError:
        import unittest
    unittest.main()

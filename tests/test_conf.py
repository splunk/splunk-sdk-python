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

import testlib
import logging

import splunklib.client as client

class TestRead(testlib.SDKTestCase):
    def test_read(self):
        service = client.connect(**self.opts.kwargs)

        confs = service.confs

        # Make sure the collection contains some of the expected entries
        self.assertTrue('eventtypes' in confs)
        self.assertTrue('indexes' in confs)
        self.assertTrue('inputs' in confs)
        self.assertTrue('props' in confs)
        self.assertTrue('transforms' in confs)
        self.assertTrue('savedsearches' in confs)

        for stanza in confs['indexes'].list(count=5):
            self.check_entity(stanza)

class TestConfs(testlib.SDKTestCase):
    def setUp(self):
        super(TestConfs, self).setUp()
        self.app_name = testlib.tmpname()
        self.app = self.service.apps.create(self.app_name)
        # Connect using the test app context
        kwargs = self.opts.kwargs.copy()
        kwargs['app'] = self.app_name
        kwargs['owner'] = "nobody"
        kwargs['sharing'] = "app"
        self.app_service = client.connect(**kwargs)

    def tearDown(self):
        self.service.apps.delete(self.app_name)
        self.clear_restart_message()

    def test_confs(self):
        confs = self.app_service.confs
        conf_name = testlib.tmpname()
        self.assertRaises(KeyError, confs.__getitem__, conf_name)
        self.assertFalse(conf_name in confs)

        conf = confs.create(conf_name)
        self.assertTrue(conf_name in confs)
        self.assertEqual(conf.name, conf_name)

        # New conf should be empty
        stanzas = conf.list()
        self.assertEqual(len(stanzas), 0)

        # Creating a stanza works
        count = len(conf)
        stanza_name = testlib.tmpname()
        stanza = conf.create(stanza_name)
        self.assertEqual(len(conf), count+1)
        self.assertTrue(stanza_name in conf)

        # New stanzas are empty
        self.assertEqual(len(stanza), 0)

        # Update works
        key = testlib.tmpname()
        val = testlib.tmpname()
        stanza.update(**{key: val})
        self.assertEventuallyTrue(lambda: stanza.refresh() and len(stanza) == 1, pause_time=0.2)
        self.assertEqual(len(stanza), 1)
        self.assertTrue(key in stanza)

        values = {testlib.tmpname(): testlib.tmpname(),
                  testlib.tmpname(): testlib.tmpname()}
        stanza.submit(values)
        stanza.refresh()
        for key, value in values.iteritems():
            self.assertTrue(key in stanza)
            self.assertEqual(value, stanza[key])

        count = len(conf)
        conf.delete(stanza_name)
        self.assertFalse(stanza_name in conf)
        self.assertEqual(len(conf), count-1)

        # Can't actually delete configuration files directly, at least
        # not in current versions of Splunk.
        self.assertRaises(client.IllegalOperationException, confs.delete, conf_name)
        self.assertTrue(conf_name in confs)

if __name__ == "__main__":
    try:
        import unittest2 as unittest
    except ImportError:
        import unittest
    unittest.main()

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

class TestCase(testlib.TestCase):
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

        for conf in confs:
            conf.name
            conf.path
            for stanza in conf: 
                self.check_entity(stanza)

    def test_crud(self):
        service = client.connect(**self.opts.kwargs)

        # There is no way to delete a conf file via the REST API, so we 
        # create a test app to use as the context fo the conf test and then 
        # we cleanup by deleting the app.

        app_name = "sdk-test-app"

        # Delete any lingering test app
        testlib.delete_app(service, app_name)
        self.assertFalse(app_name in service.apps)

        # Create a fresh test app
        service.apps.create(app_name)
        self.assertTrue(app_name in service.apps)

        # Connect using the test app context
        kwargs = self.opts.kwargs.copy()
        kwargs['app'] = app_name
        kwargs['owner'] = "nobody"
        kwargs['sharing'] = "app"
        service = client.connect(**kwargs)

        conf_name = "sdk-test-conf"

        confs = service.confs
        self.assertFalse(conf_name in confs)

        conf = confs.create(conf_name)
        self.assertTrue(conf_name in confs)
        self.assertEqual(conf.name, conf_name)

        stanzas = conf.list()
        self.assertEqual(len(stanzas), 0)

        conf.create("stanza1")
        self.assertEqual(len(conf.list()), 1)
        self.assertTrue("stanza1" in conf)
        self.assertFalse("stanza2" in conf)
        self.assertFalse("stanza3" in conf)

        conf.create("stanza2")
        self.assertEqual(len(conf.list()), 2)
        self.assertTrue("stanza1" in conf)
        self.assertTrue("stanza2" in conf)
        self.assertFalse("stanza3" in conf)

        conf.create("stanza3")
        self.assertEqual(len(conf.list()), 3)
        self.assertTrue("stanza1" in conf)
        self.assertTrue("stanza2" in conf)
        self.assertTrue("stanza3" in conf)

        stanza1 = conf['stanza1']
        self.assertFalse('key1' in stanza1.content)
        self.assertFalse('key2' in stanza1.content)
        self.assertFalse('key3' in stanza1.content)

        stanza1.update(key1="value1")
        stanza1.refresh()
        self.assertTrue('key1' in stanza1.content)
        self.assertFalse('key2' in stanza1.content)
        self.assertFalse('key3' in stanza1.content)
        self.check_content(stanza1, key1="value1")

        stanza1.update(key2="value2")
        stanza1.refresh()
        self.assertTrue('key1' in stanza1.content)
        self.assertTrue('key2' in stanza1.content)
        self.assertFalse('key3' in stanza1.content)
        self.check_content(stanza1, key1="value1", key2="value2")

        stanza1.update(key3=42)
        stanza1.refresh()
        self.assertTrue('key1' in stanza1.content)
        self.assertTrue('key2' in stanza1.content)
        self.assertTrue('key3' in stanza1.content)
        self.check_content(stanza1, key1="value1", key2="value2", key3=42)

        conf.delete("stanza3")
        self.assertEqual(len(conf.list()), 2)
        self.assertTrue("stanza1" in conf)
        self.assertTrue("stanza2" in conf)
        self.assertFalse("stanza3" in conf)

        conf.delete("stanza2")
        self.assertEqual(len(conf.list()), 1)
        self.assertTrue("stanza1" in conf)
        self.assertFalse("stanza2" in conf)
        self.assertFalse("stanza3" in conf)

        conf.delete("stanza1")
        self.assertEqual(len(conf.list()), 0)
        self.assertFalse("stanza1" in conf)
        self.assertFalse("stanza2" in conf)
        self.assertFalse("stanza3" in conf)

        # Reconnect using original context so we can cleaup the test app
        service = client.connect(**self.opts.kwargs)
        testlib.delete_app(service, app_name)
        self.assertFalse(app_name in service.apps)

if __name__ == "__main__":
    testlib.main()

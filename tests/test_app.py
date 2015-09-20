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


class TestApp(testlib.SDKTestCase):
    app = None
    app_name = None

    def setUp(self):
        super(TestApp, self).setUp()
        if self.app is None:
            for app in self.service.apps:
                if app.name.startswith('delete-me'):
                    self.service.apps.delete(app.name)
            # Creating apps takes 0.8s, which is too long to wait for
            # each test in this test suite. Therefore we create one
            # app and reuse it. Since apps are rather less fraught
            # than entities like indexes, this is okay.
            self.app_name = testlib.tmpname()
            self.app = self.service.apps.create(self.app_name)
            logging.debug("Creating app %s", self.app_name)
        else:
            logging.debug("App %s already exists. Skipping creation.", self.app_name)
        if self.service.restart_required:
            self.service.restart(120)
        return

    def tearDown(self):
        super(TestApp, self).tearDown()
        # The rest of this will leave Splunk in a state requiring a restart.
        # It doesn't actually matter, though.
        self.service = client.connect(**self.opts.kwargs)
        for app in self.service.apps:
            app_name = app.name
            if app_name.startswith('delete-me'):
                self.service.apps.delete(app_name)
                self.assertEventuallyTrue(lambda: app_name not in self.service.apps)
        self.clear_restart_message()

    def test_app_integrity(self):
        self.check_entity(self.app)
        self.app.setupInfo
        self.app['setupInfo']

    def test_disable_enable(self):
        self.app.disable()
        self.app.refresh()
        self.assertEqual(self.app['disabled'], '1')
        self.app.enable()
        self.app.refresh()
        self.assertEqual(self.app['disabled'], '0')

    def test_update(self):
        kwargs = {
            'author': "Me",
            'description': "Test app description",
            'label': "SDK Test",
            'version': "1.2",
            'visible': True,
        }
        self.app.update(**kwargs)
        self.app.refresh()
        self.assertEqual(self.app['author'], "Me")
        self.assertEqual(self.app['label'], "SDK Test")
        self.assertEqual(self.app['version'], "1.2")
        self.assertEqual(self.app['visible'], "1")

    def test_delete(self):
        name = testlib.tmpname()
        app = self.service.apps.create(name)
        self.assertTrue(name in self.service.apps)
        self.service.apps.delete(name)
        self.assertFalse(name in self.service.apps)
        self.clear_restart_message() # We don't actually have to restart here.

    def test_package(self):
        p = self.app.package()
        self.assertEqual(p.name, self.app_name)
        self.assertTrue(p.path.endswith(self.app_name + '.spl'))
        self.assertTrue(p.url.endswith(self.app_name + '.spl'))

    def test_updateInfo(self):
        p = self.app.updateInfo()
        self.assertTrue(p is not None)

if __name__ == "__main__":
    try:
        import unittest2 as unittest
    except ImportError:
        import unittest
    unittest.main()

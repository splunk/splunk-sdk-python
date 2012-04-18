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

import splunklib.client as client

import testlib

class TestCase(testlib.TestCase):
    def check_app(self, app):
        app.name
        app.path
        app.content
        app.metadata

    def test_read(self):
        service = client.connect(**self.opts.kwargs)

        for app in service.apps:
            self.check_app(app)
            app.refresh()
            self.check_app(app)

    def test_crud(self):
        service = client.connect(**self.opts.kwargs)

        appname = "sdk-test-app"

        testlib.delete_app(service, appname)
        self.assertFalse(appname in service.apps)

        kwargs = {
            'author': "Me",
            'description': "Test app description",
            'label': "SDK Test",
            'manageable': False,
            'template': "barebones",
            'visible': True,
        }
        service.apps.create(appname, **kwargs)
        self.assertTrue(appname in service.apps)
        app = service.apps[appname]
        self.assertEqual(app['author'], "Me")
        self.assertEqual(app['label'], "SDK Test")
        self.assertEqual(app['manageable'], "0")
        self.assertEqual(app['visible'], "1")

        kwargs = {
            'author': "SDK",
            'visible': False,
        }
        app = service.apps[appname]
        app.update(**kwargs)
        app.refresh()
        self.assertEqual(app['author'], "SDK")
        self.assertEqual(app['label'], "SDK Test")
        self.assertEqual(app['manageable'], "0")
        self.assertEqual(app['visible'], "0")

        testlib.delete_app(service, appname)
        self.assertFalse(appname in service.apps)

if __name__ == "__main__":
    testlib.main()

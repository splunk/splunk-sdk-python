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

import unittest

import splunklib.data as data

import splunklib.client as client
from splunklib.binding import HTTPError

class TestCase(testlib.TestCase):
    def test_capabilities(self):
        capabilities = self.service.capabilities
        for item in client.capabilities:
            self.assertTrue(item in capabilities)

    def test_info(self):
        info = self.service.info
        keys = ["build", "cpu_arch", "guid", "isFree", "isTrial", "licenseKeys",
            "licenseSignature", "licenseState", "master_guid", "mode", 
            "os_build", "os_name", "os_version", "serverName", "version"]
        for key in keys: 
            self.assertTrue(key in info.keys())

    def test_without_namespace(self):
        service = client.connect(**self.opts.kwargs)
        service.apps.list()

    def test_app_namespace(self):
        kwargs = self.opts.kwargs.copy()
        kwargs.update({'app': "search", 'owner': None})
        service_ns = client.connect(**kwargs)
        service_ns.apps.list()

    def test_owner_wildcard(self):
        kwargs = self.opts.kwargs.copy()
        kwargs.update({ 'app': "search", 'owner': "-" })
        service_ns = client.connect(**kwargs)
        service_ns.apps.list()

    def test_default_app(self):
        kwargs = self.opts.kwargs.copy()
        kwargs.update({ 'app': None, 'owner': "admin" })
        service_ns = client.connect(**kwargs)
        service_ns.apps.list()

    def test_app_wildcard(self):
        kwargs = self.opts.kwargs.copy()
        kwargs.update({ 'app': "-", 'owner': "admin" })
        service_ns = client.connect(**kwargs)
        service_ns.apps.list()

    def test_user_namespace(self):
        kwargs = self.opts.kwargs.copy()
        kwargs.update({ 'app': "search", 'owner': "admin" })
        service_ns = client.connect(**kwargs)
        service_ns.apps.list()

    def test_parse(self):
        # Awaiting new parse method.
        response = self.service.parse('search * abc="def" | dedup abc')
        self.assertEqual(response.status, 200)
        # try:
        #     service.parse("xyzzy")
        #     self.fail()
        # except HTTPError, e:
        #     self.assertEqual(e.status, 400)
        # except:
        #     self.fail()

    def test_restart(self):
        service = client.connect(**self.opts.kwargs)
        self.service.restart(timeout=120)
        service.login() # Make sure we are awake

class TestSettings(testlib.TestCase):
    def test_read_settings(self):
        settings = self.service.settings
        # Verify that settings contains the keys we expect
        keys = [
            "SPLUNK_DB", "SPLUNK_HOME", "enableSplunkWebSSL", "host",
            "httpport", "mgmtHostPort", "minFreeSpace", "pass4SymmKey",
            "serverName", "sessionTimeout", "startwebserver", "trustedIP"
        ]
        for key in keys:
            self.assertTrue(key in settings)

    def test_update_settings(self):
        settings = self.service.settings
        # Verify that we can update the settings
        original = settings['sessionTimeout']
        self.assertTrue(original != "42h")
        settings.update(sessionTimeout="42h")
        settings.refresh()
        updated = settings['sessionTimeout']
        self.assertEqual(updated, "42h")

        # Restore (and verify) original value
        settings.update(sessionTimeout=original)
        settings.refresh()
        updated = settings['sessionTimeout']
        self.assertEqual(updated, original)

class TestTrailing(unittest.TestCase):
    template = '/servicesNS/boris/search/another/path/segment/that runs on'

    def test_raises_when_not_found_first(self):
        self.assertRaises(ValueError, client.trailing, 'this is a test', 'boris')

    def test_raises_when_not_found_second(self):
        self.assertRaises(ValueError, client.trailing, 'this is a test', 's is', 'boris')

    def test_no_args_is_identity(self):
        self.assertEqual(self.template, client.trailing(self.template))

    def test_trailing_with_one_arg_works(self):
        self.assertEqual('boris/search/another/path/segment/that runs on', client.trailing(self.template, 'ervicesNS/'))

    def test_trailing_with_n_args_works(self):
        self.assertEqual('another/path/segment/that runs on', client.trailing(self.template, 'servicesNS/', '/', '/'))


if __name__ == "__main__":
    testlib.main()

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
from splunklib.binding import HTTPError

class TestCase(testlib.TestCase):
    def test_capabilities(self):
        service = client.connect(**self.opts.kwargs)

        expected = [
            "admin_all_objects", "change_authentication", 
            "change_own_password", "delete_by_keyword",
            "edit_deployment_client", "edit_deployment_server",
            "edit_dist_peer", "edit_forwarders", "edit_httpauths",
            "edit_input_defaults", "edit_monitor", "edit_roles",
            "edit_scripted", "edit_search_server", "edit_server",
            "edit_splunktcp", "edit_splunktcp_ssl", "edit_tcp",
            "edit_udp", "edit_user", "edit_web_settings", "get_metadata",
            "get_typeahead", "indexes_edit", "license_edit", "license_tab",
            "list_deployment_client", "list_forwarders", "list_httpauths",
            "list_inputs", "request_remote_tok", "rest_apps_management",
            "rest_apps_view", "rest_properties_get", "rest_properties_set",
            "restart_splunkd", "rtsearch", "schedule_search", "search",
            "use_file_operator" ]

        capabilities = service.capabilities
        for item in expected: self.assertTrue(item in capabilities)

    def test_info(self):
        service = client.connect(**self.opts.kwargs)

        info = service.info
        keys = [
            "build", "cpu_arch", "guid", "isFree", "isTrial", "licenseKeys",
            "licenseSignature", "licenseState", "master_guid", "mode", 
            "os_build", "os_name", "os_version", "serverName", "version" ]
        for key in keys: self.assertTrue(key in info.keys())

    def test_namespaces(self):
        kwargs = self.opts.kwargs.copy()

        # Verify connect with no namespace
        service = client.connect(**kwargs)
        service.apps()

        # Verify namespace permutations using standard app & owner args 
        kwargs.update({ 'app': "search", 'owner': None })
        service_ns = client.connect(**kwargs)
        service_ns.apps()

        kwargs.update({ 'app': "search", 'owner': "-" })
        service_ns = client.connect(**kwargs)
        service_ns.apps()

        kwargs.update({ 'app': None, 'owner': "admin" })
        service_ns = client.connect(**kwargs)
        service_ns.apps()

        kwargs.update({ 'app': "-", 'owner': "admin" })
        service_ns = client.connect(**kwargs)
        service_ns.apps()

        kwargs.update({ 'app': "search", 'owner': "admin" })
        service_ns = client.connect(**kwargs)
        service_ns.apps()

        appname = "sdk-test-app"
        username = "sdk-test-user"
        testlib.delete_app(service, appname)
        if username in service.users: service.users.delete(username)
        self.assertFalse(service.apps.contains(appname))
        self.assertFalse(service.users.contains(username))

        # App & owner dont exist, verify that the following errors
        kwargs.update({ 'app': appname, 'owner': username })
        with self.assertRaises(HTTPError):
            service_ns = client.connect(**kwargs)
            service_ns.apps()

        # Validate namespace permutations with new app & user
        service.apps.create(appname)
        service.users.create(username, password="changeme", roles="power")

        kwargs.update({ 'app': appname, 'owner': None })
        service_ns = client.connect(**kwargs)
        service_ns.apps()

        kwargs.update({ 'app': appname, 'owner': "-" })
        service_ns = client.connect(**kwargs)
        service_ns.apps()

        kwargs.update({ 'app': None, 'owner': username })
        service_ns = client.connect(**kwargs)
        service_ns.apps()

        kwargs.update({ 'app': "-", 'owner': username })
        service_ns = client.connect(**kwargs)
        service_ns.apps()

        kwargs.update({ 'app': appname, 'owner': username })
        service_ns = client.connect(**kwargs)
        service_ns.apps()

        # Cleanup
        testlib.delete_app(service, appname)
        service.users.delete(username)

        self.assertFalse(service.apps.contains(appname))
        self.assertFalse(service.users.contains(username))

    def test_parse(self):
        service = client.connect(**self.opts.kwargs)

        response = service.parse("search *")
        self.assertEqual(response.status, 200)

        response = service.parse("search index=twitter status_count=* | stats count(status_source) as count by status_source | sort -count | head 20")
        self.assertEqual(response.status, 200)

        try:
            service.parse("xyzzy")
            self.fail()
        except HTTPError, e:
            self.assertEqual(e.status, 400)
        except:
            self.fail()

    def test_restart(self):
        service = client.connect(**self.opts.kwargs)
        testlib.restart(service)
        service.login() # Make sure we are awake

    def test_settings(self):
        service = client.connect(**self.opts.kwargs)
        settings = service.settings

        # Verify that settings contains the keys we expect
        keys = [
            "SPLUNK_DB", "SPLUNK_HOME", "enableSplunkWebSSL", "host",
            "httpport", "mgmtHostPort", "minFreeSpace", "pass4SymmKey",
            "serverName", "sessionTimeout", "startwebserver", "trustedIP"
        ]
        for key in keys: self.assertTrue(key in settings.content)

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

if __name__ == "__main__":
    testlib.main()

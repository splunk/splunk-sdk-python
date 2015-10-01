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
import unittest

import splunklib.client as client
from splunklib.client import AuthenticationError
from splunklib.client import Service
from splunklib.binding import HTTPError


class ServiceTestCase(testlib.SDKTestCase):

    def test_autologin(self):
        service = client.connect(autologin=True, **self.opts.kwargs)
        self.service.restart(timeout=120)
        reader = service.jobs.oneshot("search index=internal | head 1")
        self.assertIsNotNone(reader)

    def test_capabilities(self):
        capabilities = self.service.capabilities
        self.assertTrue(isinstance(capabilities, list))
        self.assertTrue(all([isinstance(c, str) for c in capabilities]))
        self.assertTrue('change_own_password' in capabilities) # This should always be there...

    def test_info(self):
        info = self.service.info
        keys = ["build", "cpu_arch", "guid", "isFree", "isTrial", "licenseKeys",
            "licenseSignature", "licenseState", "master_guid", "mode", 
            "os_build", "os_name", "os_version", "serverName", "version"]
        for key in keys: 
            self.assertTrue(key in info.keys())

    def test_info_with_namespace(self):
        # Make sure we're not accessing /servicesNS/admin/search/server/info
        # instead of /services/server/info
        # Backup the values, which are probably set to None
        owner, app = self.service.namespace["owner"], self.service.namespace["app"]

        self.service.namespace["owner"] = self.service.username
        self.service.namespace["app"] = "search"
        try:
            self.assertEqual(self.service.info.licenseState, 'OK')
        except HTTPError as he:
            self.fail("Couldn't get the server info, probably got a 403! %s" % he.message)

        self.service.namespace["owner"] = owner
        self.service.namespace["app"] = app

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
        # At the moment the parse method returns the raw XML. At
        # some point this will change and it will return a nice,
        # objectified form of the results, but for now there's
        # nothing to test but a good response code.
        response = self.service.parse('search * abc="def" | dedup abc')
        self.assertEqual(response.status, 200)

    def test_parse_fail(self):
        try:
            self.service.parse("xyzzy")
            self.fail('Parse on nonsense did not fail')
        except HTTPError, e:
            self.assertEqual(e.status, 400)

    def test_restart(self):
        service = client.connect(**self.opts.kwargs)
        self.service.restart(timeout=120)
        service.login() # Make sure we are awake

    def test_read_outputs_with_type(self):
        name = testlib.tmpname()
        service = client.connect(**self.opts.kwargs)
        service.post('data/outputs/tcp/syslog', name=name, type='tcp')
        entity = client.Entity(service, 'data/outputs/tcp/syslog/' + name)
        self.assertTrue('tcp', entity.content.type)

        if service.restart_required:
            self.restartSplunk()
        service = client.connect(**self.opts.kwargs)
        client.Entity(service, 'data/outputs/tcp/syslog/' + name).delete()
        if service.restart_required:
            self.restartSplunk()

    def test_splunk_version(self):
        service = client.connect(**self.opts.kwargs)
        v = service.splunk_version
        self.assertTrue(isinstance(v, tuple))
        self.assertTrue(len(v) >= 2)
        for p in v:
            self.assertTrue(isinstance(p, int) and p >= 0)

        for version in [(4,3,3), (5,), (5,0,1)]:
            with self.fake_splunk_version(version):
                self.assertEqual(version, self.service.splunk_version)
    
    def test_query_without_login_raises_auth_error(self):
        service = self._create_unauthenticated_service()
        self.assertRaises(AuthenticationError, lambda: service.indexes.list())
    
    # This behavior is needed for backward compatibility for code
    # prior to the introduction of AuthenticationError
    def test_query_without_login_raises_http_401(self):
        service = self._create_unauthenticated_service()
        try:
            service.indexes.list()
            self.fail('Expected HTTP 401.')
        except HTTPError as he:
            if he.status == 401:
                # Good
                pass
            else:
                raise
    
    def test_server_info_without_login(self):
        service = self._create_unauthenticated_service()
        # Should succeed without AuthenticationError
        service.info['version']
    
    def _create_unauthenticated_service(self):
        return Service(**{
            'host': self.opts.kwargs['host'],
            'port': self.opts.kwargs['port'],
            'scheme': self.opts.kwargs['scheme']
        })


class TestCookieAuthentication(unittest.TestCase):
    def setUp(self):
        self.opts = testlib.parse([], {}, ".splunkrc")
        self.service = client.Service(**self.opts.kwargs)

        # Skip these tests if running below Splunk 6.2, cookie-auth didn't exist before
        splver = self.service.splunk_version
        # TODO: Workaround the fact that skipTest is not defined by unittest2.TestCase
        if splver[:2] < (6, 2):
            self.skipTest("Skipping cookie-auth tests, running in %d.%d.%d, this feature was added in 6.2+" % splver)

    if getattr(unittest.TestCase, 'assertIsNotNone', None) is None:

        def assertIsNotNone(self, obj, msg=None):
            if obj is None:
                raise self.failureException, (msg or '%r is not None' % obj)

    def test_login_and_store_cookie(self):
        self.assertIsNotNone(self.service.get_cookies())
        self.assertEquals(len(self.service.get_cookies()), 0)
        self.service.login()
        self.assertIsNotNone(self.service.get_cookies())
        self.assertNotEquals(self.service.get_cookies(), {})
        self.assertEquals(len(self.service.get_cookies()), 1)

    def test_login_with_cookie(self):
        self.service.login()
        self.assertIsNotNone(self.service.get_cookies())
        # Use the cookie from the other service as the only auth param (don't need user/password)
        service2 = client.Service(**{"cookie": "%s=%s" % self.service.get_cookies().items()[0]})
        service2.login()
        self.assertEqual(len(service2.get_cookies()), 1)
        self.assertEqual(service2.get_cookies(), self.service.get_cookies())
        self.assertEqual(len(service2.get_cookies()), len(self.service.get_cookies()))
        self.assertEqual(service2.get_cookies().keys()[0][:8], "splunkd_")
        self.assertEqual(service2.apps.get().status, 200)

    def test_login_fails_with_bad_cookie(self):
        bad_cookie = {'bad': 'cookie'}
        service2 = client.Service()
        self.assertEquals(len(service2.get_cookies()), 0)
        service2.get_cookies().update(bad_cookie)
        service2.login()
        self.assertEquals(service2.get_cookies(), {'bad': 'cookie'})

        # Should get an error with a bad cookie
        try:
            service2.apps.get()
            self.fail()
        except AuthenticationError as ae:
            self.assertEqual(str(ae), "Request failed: Session is not logged in.")

    def test_autologin_with_cookie(self):
        self.service.login()
        self.assertTrue(self.service.has_cookies())
        service = client.connect(
            autologin=True,
            cookie="%s=%s" % self.service.get_cookies().items()[0],
            **self.opts.kwargs)
        self.assertTrue(service.has_cookies())
        self.service.restart(timeout=120)
        reader = service.jobs.oneshot("search index=internal | head 1")
        self.assertIsNotNone(reader)

    def test_login_fails_with_no_cookie(self):
        service2 = client.Service()
        self.assertEquals(len(service2.get_cookies()), 0)

        # Should get an error when no authentication method
        try:
            service2.login()
            self.fail()
        except AuthenticationError as ae:
            self.assertEqual(str(ae), "Login failed.")

    def test_login_with_multiple_cookie_headers(self):
        cookies = {
            'bad': 'cookie',
            'something_else': 'bad'
        }
        self.service.logout()
        self.service.get_cookies().update(cookies)

        self.service.login()
        self.assertEqual(self.service.apps.get().status, 200)

    def test_login_with_multiple_cookies(self):
        bad_cookie = 'bad=cookie'
        self.service.login()
        self.assertIsNotNone(self.service.get_cookies())

        service2 = client.Service(**{"cookie": bad_cookie})
        service2.login()

        # Should get an error with a bad cookie
        try:
            service2.apps.get()
            self.fail()
        except AuthenticationError as ae:
            self.assertEqual(str(ae), "Request failed: Session is not logged in.")

            # Add on valid cookies, and try to use all of them
            service2.get_cookies().update(self.service.get_cookies())

            self.assertEqual(len(service2.get_cookies()), 2)
            self.service.get_cookies().update({'bad': 'cookie'})
            self.assertEqual(service2.get_cookies(), self.service.get_cookies())
            self.assertEqual(len(service2.get_cookies()), 2)
            self.assertEqual(service2.get_cookies().keys()[1][:8], "splunkd_")
            self.assertTrue('bad' in service2.get_cookies().keys())
            self.assertEqual(service2.get_cookies()['bad'], 'cookie')
            self.assertEqual(self.service.get_cookies().items(), service2.get_cookies().items())
            service2.login()
            self.assertEqual(service2.apps.get().status, 200)

class TestSettings(testlib.SDKTestCase):
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
        self.restartSplunk()

class TestTrailing(unittest.TestCase):
    template = '/servicesNS/boris/search/another/path/segment/that runs on'

    def test_raises_when_not_found_first(self):
        self.assertRaises(ValueError, client._trailing, 'this is a test', 'boris')

    def test_raises_when_not_found_second(self):
        self.assertRaises(ValueError, client._trailing, 'this is a test', 's is', 'boris')

    def test_no_args_is_identity(self):
        self.assertEqual(self.template, client._trailing(self.template))

    def test_trailing_with_one_arg_works(self):
        self.assertEqual('boris/search/another/path/segment/that runs on', client._trailing(self.template, 'ervicesNS/'))

    def test_trailing_with_n_args_works(self):
        self.assertEqual(
            'another/path/segment/that runs on',
            client._trailing(self.template, 'servicesNS/', '/', '/')
        )

class TestEntityNamespacing(testlib.SDKTestCase):
    def test_proper_namespace_with_arguments(self):
        entity = self.service.apps['search']
        self.assertEquals((None,None,"global"), entity._proper_namespace(sharing="global"))
        self.assertEquals((None,"search","app"), entity._proper_namespace(sharing="app", app="search"))
        self.assertEquals(
            ("admin", "search", "user"),
            entity._proper_namespace(sharing="user", app="search", owner="admin")
        )

    def test_proper_namespace_with_entity_namespace(self):
        entity = self.service.apps['search']
        namespace = (entity.access.owner, entity.access.app, entity.access.sharing)
        self.assertEquals(namespace, entity._proper_namespace())

    def test_proper_namespace_with_service_namespace(self):
        entity = client.Entity(self.service, client.PATH_APPS + "search")
        del entity._state['access']
        namespace = (self.service.namespace.owner,
                     self.service.namespace.app,
                     self.service.namespace.sharing)
        self.assertEquals(namespace, entity._proper_namespace())

if __name__ == "__main__":
    try:
        import unittest2 as unittest
    except ImportError:
        import unittest
    unittest.main()

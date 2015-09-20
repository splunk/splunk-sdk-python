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


class Tests(testlib.SDKTestCase):
    def setUp(self):
        self.service = client.connect(**self.opts.kwargs)
        self.storage_passwords = self.service.storage_passwords

    def tearDown(self):
        # Delete all passwords created by SDK tests
        for sp in self.storage_passwords:
            if "delete-me" in sp.username or "delete-me" in sp.realm:
                sp.delete()

    def test_create(self):
        start_count = len(self.storage_passwords)
        realm = testlib.tmpname()
        username = testlib.tmpname()

        p = self.storage_passwords.create("changeme", username, realm)
        self.assertEqual(start_count + 1, len(self.storage_passwords))
        self.assertEqual(p.realm, realm)
        self.assertEqual(p.username, username)
        self.assertEqual(p.clear_password, "changeme")
        self.assertEqual(p.name, realm + ":" + username + ":")

        p.delete()
        self.assertEqual(start_count, len(self.storage_passwords))

    def test_create_with_backslashes(self):
        start_count = len(self.storage_passwords)
        realm = "\\" + testlib.tmpname()
        username = "\\" + testlib.tmpname()

        # Prepends one escaped slash
        p = self.storage_passwords.create("changeme", username, realm)
        self.assertEqual(start_count + 1, len(self.storage_passwords))
        self.assertEqual(p.realm, realm)
        # Prepends one escaped slash
        self.assertEqual(p.username, username)
        self.assertEqual(p.clear_password, "changeme")
        # Checks for 2 escaped slashes (Splunk encodes the single slash)
        self.assertEqual(p.name, "\\" + realm + ":\\" + username + ":")

        p.delete()
        self.assertEqual(start_count, len(self.storage_passwords))

    def test_create_with_slashes(self):
        start_count = len(self.storage_passwords)
        realm = "/" + testlib.tmpname()
        username = "/" + testlib.tmpname()

        # Prepends one escaped slash
        p = self.storage_passwords.create("changeme", username, realm)
        self.assertEqual(start_count + 1, len(self.storage_passwords))
        self.assertEqual(p.realm, realm)
        # Prepends one escaped slash
        self.assertEqual(p.username, username)
        self.assertEqual(p.clear_password, "changeme")
        # Checks for 2 escaped slashes (Splunk encodes the single slash)
        self.assertEqual(p.name, realm + ":" + username + ":")

        p.delete()
        self.assertEqual(start_count, len(self.storage_passwords))

    def test_create_norealm(self):
        start_count = len(self.storage_passwords)
        username = testlib.tmpname()

        p = self.storage_passwords.create("changeme", username)
        self.assertEqual(start_count + 1, len(self.storage_passwords))
        self.assertEqual(p.realm, None)
        self.assertEqual(p.username, username)
        self.assertEqual(p.clear_password, "changeme")
        self.assertEqual(p.name, ":" + username + ":")

        p.delete()
        self.assertEqual(start_count, len(self.storage_passwords))

    def test_create_with_colons(self):
        start_count = len(self.storage_passwords)
        username = testlib.tmpname()
        realm = testlib.tmpname()

        p = self.storage_passwords.create("changeme", username + ":end",
                                          ":start" + realm)
        self.assertEqual(start_count + 1, len(self.storage_passwords))
        self.assertEqual(p.realm, ":start" + realm)
        self.assertEqual(p.username, username + ":end")
        self.assertEqual(p.clear_password, "changeme")
        self.assertEqual(p.name,
                         "\\:start" + realm + ":" + username + "\\:end:")

        p.delete()
        self.assertEqual(start_count, len(self.storage_passwords))

        prefix = testlib.tmpname()
        realm = prefix + ":r:e:a:l:m:"
        user = ":u:s:e:r:"
        p = self.storage_passwords.create("changeme", user, realm)
        self.assertEqual(start_count + 1, len(self.storage_passwords))
        self.assertEqual(p.realm, realm)
        self.assertEqual(p.username, user)
        self.assertEqual(p.clear_password, "changeme")
        self.assertEqual(p.name,
                         prefix + "\\:r\\:e\\:a\\:l\\:m\\::\\:u\\:s\\:e\\:r\\::")

        p.delete()
        self.assertEqual(start_count, len(self.storage_passwords))

    def test_create_crazy(self):
        start_count = len(self.storage_passwords)
        username = testlib.tmpname()
        realm = testlib.tmpname()

        p = self.storage_passwords.create("changeme",
                                          username + ":end!@#$%^&*()_+{}:|<>?",
                                          ":start::!@#$%^&*()_+{}:|<>?" + realm)
        self.assertEqual(start_count + 1, len(self.storage_passwords))
        self.assertEqual(p.realm, ":start::!@#$%^&*()_+{}:|<>?" + realm)
        self.assertEqual(p.username, username + ":end!@#$%^&*()_+{}:|<>?")
        self.assertEqual(p.clear_password, "changeme")
        self.assertEqual(p.name,
                         "\\:start\\:\\:!@#$%^&*()_+{}\\:|<>?" + realm + ":" + username + "\\:end!@#$%^&*()_+{}\\:|<>?:")

        p.delete()
        self.assertEqual(start_count, len(self.storage_passwords))

    def test_read(self):
        start_count = len(self.storage_passwords)
        username = testlib.tmpname()

        p = self.storage_passwords.create("changeme", username)
        self.assertEqual(start_count + 1, len(self.storage_passwords))

        for sp in self.storage_passwords:
            self.assertTrue(p.name in self.storage_passwords)
            # Name works with or without a trailing colon
            self.assertTrue((":" + username + ":") in self.storage_passwords)
            self.assertTrue((":" + username) in self.storage_passwords)

        p.delete()
        self.assertEqual(start_count, len(self.storage_passwords))

    def test_update(self):
        start_count = len(self.storage_passwords)
        realm = testlib.tmpname()
        username = testlib.tmpname()

        p = self.storage_passwords.create("changeme", username, realm)
        self.assertEqual(start_count + 1, len(self.storage_passwords))
        self.assertEqual(p.realm, realm)
        self.assertEqual(p.username, username)
        self.assertEqual(p.clear_password, "changeme")
        self.assertEqual(p.name, realm + ":" + username + ":")

        p.update(password="Splunkeroo!")
        self.assertEqual(p.clear_password, "changeme")

        p.refresh()
        self.assertEqual(start_count + 1, len(self.storage_passwords))
        self.assertEqual(p.realm, realm)
        self.assertEqual(p.username, username)
        self.assertEqual(p.clear_password, "Splunkeroo!")
        self.assertEqual(p.name, realm + ":" + username + ":")

        p.delete()
        self.assertEqual(start_count, len(self.storage_passwords))

    def test_delete(self):
        start_count = len(self.storage_passwords)
        username = testlib.tmpname()

        p = self.storage_passwords.create("changeme", username, "myrealm")
        self.assertEqual(start_count + 1, len(self.storage_passwords))
        self.assertEqual(p.realm, "myrealm")
        self.assertEqual(p.username, username)
        self.assertEqual(p.clear_password, "changeme")
        self.assertEqual(p.name, "myrealm:" + username + ":")

        self.storage_passwords.delete(username, "myrealm")
        self.assertEqual(start_count, len(self.storage_passwords))

        self.storage_passwords.create("changeme", username, "myrealm")
        self.assertEqual(start_count + 1, len(self.storage_passwords))

        self.storage_passwords.delete("myrealm:" + username + ":")
        self.assertEqual(start_count, len(self.storage_passwords))

        # Test named parameters
        self.storage_passwords.create(password="changeme", username=username,
                                      realm="myrealm")
        self.assertEqual(start_count + 1, len(self.storage_passwords))

        self.storage_passwords.delete(username, "myrealm")
        self.assertEqual(start_count, len(self.storage_passwords))

        self.storage_passwords.create(password="changeme", username=username + "/foo",
                                      realm="/myrealm")
        self.assertEqual(start_count + 1, len(self.storage_passwords))

        self.storage_passwords.delete(username + "/foo", "/myrealm")
        self.assertEqual(start_count, len(self.storage_passwords))


if __name__ == "__main__":
    try:
        import unittest2 as unittest
    except ImportError:
        import unittest
    unittest.main()

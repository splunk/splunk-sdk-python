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

class UserTestCase(testlib.SDKTestCase):
    def check_user(self, user):
        self.check_entity(user)
        # Verify expected fields exist
        [user[f] for f in ['email', 'password', 'realname', 'roles']]
        
    def setUp(self):
        super(UserTestCase, self).setUp()
        self.username = testlib.tmpname()
        self.user = self.service.users.create(
            self.username,
            password='changeme!',
            roles=['power', 'user'])

    def tearDown(self):
        super(UserTestCase, self).tearDown()
        for user in self.service.users:
            if user.name.startswith('delete-me'):
                self.service.users.delete(user.name)

    def test_read(self):
        for user in self.service.users:
            self.check_user(user)
            for role in user.role_entities:
                self.assertTrue(isinstance(role, client.Entity))
                self.assertTrue(role.name in self.service.roles)
            self.assertEqual(user.roles,
                             [role.name for role in user.role_entities])

    def test_create(self):
        self.assertTrue(self.username in self.service.users)
        self.assertEqual(self.username, self.user.name)

    def test_delete(self):
        self.service.users.delete(self.username)
        self.assertFalse(self.username in self.service.users)
        with self.assertRaises(client.HTTPError):
            self.user.refresh()

    def test_update(self):
        self.assertTrue(self.user['email'] is None)
        self.user.update(email="foo@bar.com")
        self.user.refresh()
        self.assertTrue(self.user['email'] == "foo@bar.com")

    def test_in_is_case_insensitive(self):
        # Splunk lowercases user names, verify the casing works as expected
        users = self.service.users
        self.assertTrue(self.username in users)
        self.assertTrue(self.username.upper() in users)

    def test_username_in_create_is_case_insensitive(self):
        name = testlib.tmpname().lower()
        users = self.service.users
        user = users.create(name.upper(), password="changeme!", roles="power")
        self.assertTrue(user.name == name)
        self.assertTrue(name in users)

    def test_delete_is_case_insensitive(self):
        users = self.service.users
        users.delete(self.username.upper())
        self.assertFalse(self.username in users)
        self.assertFalse(self.username.upper() in users)

if __name__ == "__main__":
    try:
        import unittest2 as unittest
    except ImportError:
        import unittest
    unittest.main()
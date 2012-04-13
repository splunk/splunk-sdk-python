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
    def test(self):
        service = client.connect(**self.opts.kwargs)

        users = service.users
        roles = service.roles

        # Verify that we can read the users collection
        for user in users:
            for role in user.content.roles:
                self.assertTrue(roles.contains(role))

        if users.contains("sdk-user"): users.delete("sdk-user")
        self.assertFalse(users.contains("sdk-user"))

        user = users.create("sdk-user", password="changeme", roles="power")
        self.assertTrue(users.contains("sdk-user"))

        # Verify the new user has the expected attributes
        self.assertTrue('email' in user.content)
        self.assertTrue('password' in user.content)
        self.assertTrue('realname' in user.content)
        self.assertTrue('roles' in user.content)

        # Verify that we can update the user
        self.assertTrue(user['email'] is None)
        user.update(email="foo@bar.com")
        user.refresh()
        self.assertTrue(user['email'] == "foo@bar.com")

        # Verify that we can delete the user
        users.delete("sdk-user")
        self.assertFalse(users.contains("sdk-user"))

        # Splunk lowercases user names, verify the casing works as expected
        self.assertFalse(users.contains("sdk-user"))
        self.assertFalse(users.contains("SDK-User"))

        user = users.create("SDK-User", password="changeme", roles="power")
        self.assertTrue(user.name == "sdk-user")
        self.assertTrue(users.contains("SDK-User"))
        self.assertTrue(users.contains("sdk-user"))

        user = users['SDK-User']
        self.assertTrue(user.name == "sdk-user")

        users.delete("SDK-User")
        self.assertFalse(users.contains("SDK-User"))
        self.assertFalse(users.contains("sdk-user"))

if __name__ == "__main__":
    testlib.main()

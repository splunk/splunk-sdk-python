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

class RoleTestCase(testlib.SDKTestCase):
    def setUp(self):
        super(RoleTestCase, self).setUp()
        self.role_name = testlib.tmpname()
        self.role = self.service.roles.create(self.role_name)

    def tearDown(self):
        super(RoleTestCase, self).tearDown()
        for role in self.service.roles:
            if role.name.startswith('delete-me'):
                self.service.roles.delete(role.name)

    def check_role(self, role):
        self.check_entity(role)
        capabilities = role.service.capabilities
        for capability in role.content.capabilities:
            self.assertTrue(capability in capabilities)

    def test_read(self):
        for role in self.service.roles:
            self.check_role(role)
            role.refresh()
            self.check_role(role)

    def test_read_case_insensitive(self):
        for role in self.service.roles:
            a = self.service.roles[role.name.upper()]
            b = self.service.roles[role.name.lower()]
            self.assertEqual(a.name, b.name)

    def test_create(self):
        self.assertTrue(self.role_name in self.service.roles)
        self.check_entity(self.role)

    def test_delete(self):
        self.assertTrue(self.role_name in self.service.roles)
        self.service.roles.delete(self.role_name)
        self.assertFalse(self.role_name in self.service.roles)
        self.assertRaises(client.HTTPError, self.role.refresh)

    def test_grant_and_revoke(self):
        self.assertFalse('edit_user' in self.role.capabilities)
        self.role.grant('edit_user')
        self.role.refresh()
        self.assertTrue('edit_user' in self.role.capabilities)

        self.assertFalse('change_own_password' in self.role.capabilities)
        self.role.grant('change_own_password')
        self.role.refresh()
        self.assertTrue('edit_user' in self.role.capabilities)
        self.assertTrue('change_own_password' in self.role.capabilities)

        self.role.revoke('edit_user')
        self.role.refresh()
        self.assertFalse('edit_user' in self.role.capabilities)
        self.assertTrue('change_own_password' in self.role.capabilities)

        self.role.revoke('change_own_password')
        self.role.refresh()
        self.assertFalse('edit_user' in self.role.capabilities)
        self.assertFalse('change_own_password' in self.role.capabilities)

    def test_invalid_grant(self):
        self.assertRaises(client.NoSuchCapability, self.role.grant, 'i-am-an-invalid-capability')

    def test_invalid_revoke(self):
        self.assertRaises(client.NoSuchCapability, self.role.revoke, 'i-am-an-invalid-capability')

    def test_revoke_capability_not_granted(self):
        self.role.revoke('change_own_password')


    def test_update(self):
        kwargs = {}
        if 'user' in self.role['imported_roles']:
            kwargs['imported_roles'] = ''
        else:
            kwargs['imported_roles'] = ['user']
        if self.role['srchJobsQuota'] is not None:
            kwargs['srchJobsQuota'] = int(self.role['srchJobsQuota']) + 1
        self.role.update(**kwargs)
        self.role.refresh()
        self.assertEqual(self.role['imported_roles'], kwargs['imported_roles'])
        self.assertEqual(int(self.role['srchJobsQuota']), kwargs['srchJobsQuota'])

if __name__ == "__main__":
    try:
        import unittest2 as unittest
    except ImportError:
        import unittest
    unittest.main()

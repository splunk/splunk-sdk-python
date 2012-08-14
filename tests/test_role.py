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

import splunklib.client as client

class TestCase(testlib.TestCase):
    def setUp(self):
        testlib.TestCase.setUp(self)
        self.role_name = testlib.tmpname()
        self.role = self.service.roles.create(self.role_name)

    def tearDown(self):
        testlib.TestCase.tearDown(self)
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

    def test_create(self):
        self.assertTrue(self.role_name in self.service.roles)
        self.check_entity(self.role)

    def test_delete(self):
        self.assertTrue(self.role_name in self.service.roles)
        self.service.roles.delete(self.role_name)
        self.assertFalse(self.role_name in self.service.roles)
        self.assertRaises(client.EntityDeletedException, self.role.refresh)

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
    testlib.main()

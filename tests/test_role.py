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
    def check_role(self, role):
        role.name
        role.path
        role.metadata
        role.content

        service = role.service
        capabilities = service.capabilities
        for capability in role.content.capabilities:
            self.assertTrue(capability in capabilities)

    def test_read(self):
        service = client.connect(**self.opts.kwargs)

        for role in service.roles:
            self.check_role(role)
            role.refresh()
            self.check_role(role)

    def test_crud(self):
        service = client.connect(**self.opts.kwargs)

        roles = service.roles

        if roles.contains("sdk-tester"): roles.delete("sdk-tester")
        self.assertFalse(roles.contains("sdk-tester"))

        role = roles.create("sdk-tester")
        self.assertTrue(roles.contains("sdk-tester"))

        self.assertTrue(role.content.has_key('capabilities'))

        roles.delete("sdk-tester")
        self.assertFalse(roles.contains("sdk-tester"))

if __name__ == "__main__":
    testlib.main()

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

class TestCase(testlib.TestCase):
    def test_deployment_tenants(self):
        service = client.connect(**self.opts.kwargs)
        deployment_tenants = service.deployment_tenants
        self.assertEqual(len(deployment_tenants.list(count=1)), 1)

    def test_deployment_tenant(self):
        service = client.connect(**self.opts.kwargs)
        deployment_tenants = service.deployment_tenants
        dt = deployment_tenants.list(count=1)[0]
        self.assertTrue(isinstance(dt.disabled, bool))
        self.assertTrue(isinstance(dt.whitelist0, str))
        self.assertTrue(isinstance(dt.check_new, bool))
        
if __name__ == "__main__":
    testlib.main()

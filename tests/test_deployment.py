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
        self.assertTrue(isinstance(dt.name, str))

    def test_deployment_serverclass(self):
        name = 'pythonsdk_serverclass6'
        service = client.connect(**self.opts.kwargs)
        if not(name in service.serverclasses):
            sc = service.serverclasses.create(name, 
                                              filterType='blacklist',
                                              whitelist=['*.wanda.biz', 'ftw.*.leroy.ru'],
                                              blacklist=['*.gov', '*.ch'])
        else:
            sc = service.serverclasses[name]
        sc.refresh()
        self.assertRaises(client.NotSupportedError, client.DeploymentServerClass.delete, sc)
        self.assertEqual(sc.whitelist, ['*.wanda.biz', 'ftw.*.leroy.ru'])
        self.assertEqual(sc['whitelist'], ['*.wanda.biz', 'ftw.*.leroy.ru'])
        self.assertEqual(sc.blacklist, ['*.gov', '*.ch'])
        self.assertEqual(sc.filterType, 'blacklist')
        self.assertEqual(sc.endpoint, None)
        self.assertEqual(sc.tmpfolder, None)
        self.assertTrue(sc.repositoryLocation.endswith('etc/deployment-apps'))
        self.assertEqual(sc.continueMatching, None)
        
    def test_server(self):
        name = 'pythonsdk_server'
        service = client.connect(**self.opts.kwargs)
        self.assertRaises(client.NotSupportedError, 
                          client.DeploymentCollection.create,
                          service.deployment_servers, name, 
                          check_new=True, disabled=True)
        servers = service.deployment_servers.list()
        if len(servers) > 0:
            for s in servers:
                self.assertTrue(isinstance(s.whitelist, str))
                self.assertTrue(isinstance(s.check_new, bool) or s.check_new is None)
                print s.disabled
                self.assertTrue(isinstance(s.disabled, bool) or s.disabled is None)

    def test_client(self):
        service = client.connect(**self.opts.kwargs)
        clients = service.deployment_clients.list()
        self.assertRaises(client.NotSupportedError, service.deployment_clients.delete, 'asdf')
        if len(clients) > 0:
            for c in clients:
                self.assertTrue(c.disabled is None or isinstance(c.disabled, bool))
                self.assertTrue(isinstance(c.serverclasses, list))
                self.assertTrue(c.target_uri is None or isinstance(c.disabled, str))
        
if __name__ == "__main__":
    testlib.main()

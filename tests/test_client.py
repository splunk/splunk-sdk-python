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

from time import sleep

import splunklib.client as client
from splunklib.binding import HTTPError
import splunklib.results as results

import testlib

# Verify that we can instantiate and connect to a service, test basic 
# interaction with the service and make sure we can connect and interact 
# with a variety of namespace configurations.
class ServiceTestCase(testlib.TestCase):
    def test(self):
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

class ClientTestCase(testlib.TestCase):
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

    # UNDONE: Shouldnt the following assert something on exit?
    def check_properties(self, job, properties, secs = 10):
        while secs > 0 and len(properties) > 0:
            content = job.refresh().content

            # Try and check every property we specified. If we fail,
            # we'll try again later. If we succeed, delete it so we
            # don't check it again.
            for k, v in properties.items():
                try:
                    self.assertEqual(content[k], v)
                    
                    # Since we succeeded, delete it
                    del properties[k]
                except:
                    pass

            secs -= 1
            sleep(1)

    def test_jobs(self):
        service = client.connect(**self.opts.kwargs)

        jobs = service.jobs
        for job in jobs: job.refresh()

        if not service.indexes.contains("sdk-tests"):
            service.indexes.create("sdk-tests")
        service.indexes['sdk-tests'].clean()

        # Make sure we can create a job
        job = jobs.create("search index=sdk-tests")
        self.assertTrue(jobs.contains(job.sid))

        # Scan jobs and make sure the entities look familiar
        keys = [
            'cursorTime', 'delegate', 'diskUsage', 'dispatchState',
            'doneProgress', 'dropCount', 'earliestTime', 'eventAvailableCount',
            'eventCount', 'eventFieldCount', 'eventIsStreaming',
            'eventIsTruncated', 'eventSearch', 'eventSorting', 'isDone',
            'isFailed', 'isFinalized', 'isPaused', 'isPreviewEnabled',
            'isRealTimeSearch', 'isRemoteTimeline', 'isSaved', 'isSavedSearch',
            'isZombie', 'keywords', 'label', 'latestTime', 'messages',
            'numPreviews', 'priority', 'remoteSearch', 'reportSearch',
            'resultCount', 'resultIsStreaming', 'resultPreviewCount',
            'runDuration', 'scanCount', 'searchProviders', 'sid',
            'statusBuckets', 'ttl'
        ]
        for job in jobs:
            for key in keys: self.assertTrue(key in job.content)

        # Make sure we can cancel the job
        job.cancel()
        self.assertFalse(jobs.contains(job.sid))

        # Search for non-existant data
        job = jobs.create("search index=sdk-tests TERM_DOES_NOT_EXIST")
        testlib.wait(job, lambda job: job['isDone'] == '1')
        self.assertEqual(job['isDone'], '1')
        self.assertEqual(job['eventCount'], '0')
        job.finalize()
        
        # Create a new job
        job = jobs.create("search * | head 1 | stats count")
        self.assertTrue(jobs.contains(job.sid))

        # Set various properties on it
        job.disable_preview()
        job.pause()
        job.set_ttl(1000)
        job.set_priority(5)
        job.touch()
        job.refresh()

        # Assert that the properties got set properly
        self.check_properties(job, {
            'isPreviewEnabled': '0',
            'isPaused': '1',
            'ttl': '1000',
            'priority': '5'
        })

        # Set more properties
        job.enable_preview()
        job.unpause()
        job.finalize()
        job.refresh()

        # Assert that they got set properly
        self.check_properties(job, {
            'isPreviewEnabled': '1',
            'isPaused': '0',
            'isFinalized': '1'
        })

        # Run a new job to get the results, but we also make
        # sure that there is at least one event in the index already
        index = service.indexes['sdk-tests']
        old_event_count = int(index['totalEventCount'])
        if old_event_count == 0:
            index.submit("test event")
            testlib.wait(index, lambda index: index['totalEventCount'] == '1')

        job = jobs.create("search index=sdk-tests | head 1 | stats count")
        testlib.wait(job, lambda job: job['isDone'] == '1')
        self.assertEqual(job['isDone'], '1')

        # Fetch the results
        reader = results.ResultsReader(job.results())

        # The first one should always be RESULTS
        kind, result = reader.next()
        self.assertEqual(results.RESULTS, kind)
        self.assertEqual(int(result["preview"]), 0)

        # The second is always the actual result
        kind, result = reader.next()
        self.assertEqual(results.RESULT, kind)
        self.assertEqual(int(result["count"]), 1)

    def test_loggers(self):
        service = client.connect(**self.opts.kwargs)

        levels = ["INFO", "WARN", "ERROR", "DEBUG", "CRIT"]
        for logger in service.loggers:
            self.assertTrue(logger['level'] in levels)

        self.assertTrue(service.loggers.contains("AuditLogger"))
        logger = service.loggers['AuditLogger']

        saved = logger['level']
        for level in levels:
            logger.update(level=level)
            logger.refresh()
            self.assertEqual(service.loggers['AuditLogger']['level'], level)
        logger.update(level=saved)
        logger.refresh()
        self.assertEqual(service.loggers['AuditLogger']['level'], saved)

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

    def test_roles(self):
        service = client.connect(**self.opts.kwargs)

        roles = service.roles

        capabilities = service.capabilities
        for role in roles:
            for capability in role.content.capabilities:
                self.assertTrue(capability in capabilities)

        if roles.contains("sdk-tester"): roles.delete("sdk-tester")
        self.assertFalse(roles.contains("sdk-tester"))

        role = roles.create("sdk-tester")
        self.assertTrue(roles.contains("sdk-tester"))

        self.assertTrue(role.content.has_key('capabilities'))

        roles.delete("sdk-tester")
        self.assertFalse(roles.contains("sdk-tester"))

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

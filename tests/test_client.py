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

from os import path
from time import sleep

import splunklib.client as client
from splunklib.binding import HTTPError
import splunklib.results as results

import testlib

def delete_app(service, name):
    if (service.apps.contains(name)):
        service.apps.delete(name)
        testlib.restart(service)

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
        delete_app(service, appname)
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
        delete_app(service, appname)
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

    def test_confs(self):
        service = client.connect(**self.opts.kwargs)

        for conf in service.confs:
            for stanza in conf: stanza.refresh()
            break # no need to refresh every conf file for the test

        self.assertTrue(service.confs.contains('props'))
        props = service.confs['props']

        if 'sdk-tests' in props: props.delete('sdk-tests')
        self.assertFalse('sdk-tests' in props)

        stanza = props.create('sdk-tests')
        self.assertTrue(props.contains('sdk-tests'))
        self.assertEqual(stanza.name,'sdk-tests')
        self.assertTrue('maxDist' in stanza.content)
        value = int(stanza['maxDist'])
        stanza.update(maxDist=value+1)
        stanza.refresh()
        self.assertEqual(stanza['maxDist'], str(value + 1))
        stanza.update(maxDist=value)
        stanza.refresh()
        self.assertEqual(stanza['maxDist'], str(value))

        props.delete('sdk-tests')
        self.assertFalse(props.contains('sdk-tests')) 

    def test_info(self):
        service = client.connect(**self.opts.kwargs)

        info = service.info
        keys = [
            "build", "cpu_arch", "guid", "isFree", "isTrial", "licenseKeys",
            "licenseSignature", "licenseState", "master_guid", "mode", 
            "os_build", "os_name", "os_version", "serverName", "version" ]
        for key in keys: self.assertTrue(key in info.keys())

    def test_indexes(self):
        service = client.connect(**self.opts.kwargs)

        for index in service.indexes: index.refresh()

        if not service.indexes.contains("sdk-tests"):
            service.indexes.create("sdk-tests")
        self.assertTrue(service.indexes.contains("sdk-tests"))

        # Scan indexes and make sure the entities look familiar
        attrs = [
            'thawedPath', 'quarantineFutureSecs',
            'isInternal', 'maxHotBuckets', 'disabled', 'homePath',
            'compressRawdata', 'maxWarmDBCount', 'frozenTimePeriodInSecs',
            'memPoolMB', 'maxHotSpanSecs', 'minTime', 'blockSignatureDatabase',
            'serviceMetaPeriod', 'coldToFrozenDir', 'quarantinePastSecs',
            'maxConcurrentOptimizes', 'maxMetaEntries', 'minRawFileSyncSecs',
            'maxMemMB', 'maxTime', 'partialServiceMetaPeriod', 'maxHotIdleSecs',
            'coldToFrozenScript', 'thawedPath_expanded', 'coldPath_expanded',
            'defaultDatabase', 'throttleCheckPeriod', 'totalEventCount',
            'enableRealtimeSearch', 'indexThreads', 'maxDataSize',
            'currentDBSizeMB', 'homePath_expanded', 'blockSignSize',
            'syncMeta', 'assureUTF8', 'rotatePeriodInSecs', 'sync',
            'suppressBannerList', 'rawChunkSizeBytes', 'coldPath',
            'maxTotalDataSizeMB'
        ]
        for index in service.indexes:
            for attr in attrs: self.assertTrue(attr in index.content)

        index = service.indexes['sdk-tests']

        index.disable()
        index.refresh()
        self.assertEqual(index['disabled'], '1')

        index.enable()
        index.refresh()
        self.assertEqual(index['disabled'], '0')
            
        index.clean()
        index.refresh()
        self.assertEqual(index['totalEventCount'], '0')

        cn = index.attach()
        cn.write("Hello World!")
        cn.close()
        testlib.wait(index, lambda index: index['totalEventCount'] == '1')
        self.assertEqual(index['totalEventCount'], '1')

        index.submit("Hello again!!")
        testlib.wait(index, lambda index: index['totalEventCount'] == '2')
        self.assertEqual(index['totalEventCount'], '2')

        # The following test must run on machine where splunkd runs,
        # otherwise a failure is expected
        testpath = path.dirname(path.abspath(__file__))
        index.upload(path.join(testpath, "testfile.txt"))
        testlib.wait(index, lambda index: index['totalEventCount'] == '3')
        self.assertEqual(index['totalEventCount'], '3')

        index.clean()
        index.refresh()
        self.assertEqual(index['totalEventCount'], '0')

    def test_indexes_metadata(self):
        service = client.connect(**self.opts.kwargs)

        metadata = service.indexes.itemmeta()
        self.assertTrue(metadata.has_key('eai:acl'))
        self.assertTrue(metadata.has_key('eai:attributes'))
        for index in service.indexes:
            metadata = index.metadata
            self.assertTrue(metadata.has_key('eai:acl'))
            self.assertTrue(metadata.has_key('eai:attributes'))

    def test_inputs(self):
        service = client.connect(**self.opts.kwargs)
        inputs = service.inputs

        for input_ in inputs: input_.refresh()

        # Scan inputs and look for some common attributes
        # Note: The disabled flag appears to be the only common attribute, as
        # there are apparently cases where even index does not appear.
        attrs = ['disabled']
        for input_ in inputs:
            for attr in attrs:  
                self.assertTrue(attr in input_.content)

        for kind in inputs.kinds:
            for input_ in inputs.list(kind):
                self.assertEqual(input_.kind, kind)

        if inputs.contains('9999'): inputs.delete('9999')
        self.assertFalse(inputs.contains('9999'))
        inputs.create("tcp", "9999", host="sdk-test")
        self.assertTrue(inputs.contains('9999'))
        input_ = inputs['9999']
        self.assertEqual(input_.kind, "tcp")
        self.assertEqual(input_['host'], "sdk-test")
        input_.update(host="foo", sourcetype="bar")
        input_.refresh()
        self.assertEqual(input_['host'], "foo")
        self.assertEqual(input_['sourcetype'], "bar")
        inputs.delete('9999')
        self.assertFalse(inputs.contains('9999'))

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
        attrs = [
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
            for attr in attrs: self.assertTrue(attr in job.content)

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

    def test_messages(self):
        service = client.connect(**self.opts.kwargs)

        messages = service.messages

        if messages.contains('sdk-test-message1'):
            messages.delete('sdk-test-message1')
        if messages.contains('sdk-test-message2'):
            messages.delete('sdk-test-message2')
        self.assertFalse(messages.contains('sdk-test-message1'))
        self.assertFalse(messages.contains('sdk-test-message2'))

        messages.create('sdk-test-message1', value="Hello!")
        self.assertTrue(messages.contains('sdk-test-message1'))
        self.assertEqual(messages['sdk-test-message1'].value, "Hello!")

        messages.create('sdk-test-message2', value="World!")
        self.assertTrue(messages.contains('sdk-test-message2'))
        self.assertEqual(messages['sdk-test-message2'].value, "World!")

        messages.delete('sdk-test-message1')
        messages.delete('sdk-test-message2')
        self.assertFalse(messages.contains('sdk-test-message1'))
        self.assertFalse(messages.contains('sdk-test-message2'))

        # Verify that message names with spaces work correctly
        if messages.contains('sdk test message'):
            messages.delete('sdk test message')
        self.assertFalse(messages.contains('sdk test message'))
        messages.create('sdk test message', value="xyzzy")
        self.assertTrue(messages.contains('sdk test message'))
        self.assertEqual(messages['sdk test message'].value, "xyzzy")
        messages.delete('sdk test message')
        self.assertFalse(messages.contains('sdk test message'))

        # Verify that create raises a ValueError on invalid name args
        with self.assertRaises(ValueError):
            messages.create(None, value="What?")
            messages.create(42, value="Who, me?")
            messages.create([1, 2,  3], value="Who, me?")

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

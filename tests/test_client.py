#!/usr/bin/env python
#
# Copyright 2011 Splunk, Inc.
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
import sys
from time import sleep
import unittest

import splunklib.client as client
from splunklib.binding import HTTPError
import splunklib.results as results
from utils import parse

opts = None # Command line options

def create_app(service, name):
    service.apps.create(name)
    restart(service)

def create_user(service, name, password="changeme", roles="power"):
    service.users.create(name, password=password, roles=roles)

def delete_app(service, name):
    if (service.apps.contains(name)):
        service.apps.delete(name)
        restart(service)

def delete_user(service, name):
    if (service.users.contains(name)):
        service.users.delete(name)

def restart(service):
    """Restart the given service and wait for it to wake back up."""
    service.restart()
    sleep(5) # Wait for service to notice restart
    wait_for_restart(service)

# When an event is submitted to an index it takes a while before the event
# is registered by the index's totalEventCount.
def wait_event_count(index, count, secs):
    """Wait up to the given number of secs for the given index's
       totalEventCount to reach the given value."""
    done = False
    while not done and secs > 0:
        sleep(1)
        secs -= 1 # Approximate
        done = index['totalEventCount'] == count

def wait_for_restart(service):
    retry = 30
    while retry > 0:
        retry -= 1
        try:
            service.login() # Awake yet?
            return
        except:
            sleep(2)

# Verify that we can instantiate and connect to a service, test basic 
# interaction with the service and make sure we can connect and interact 
# with a variety of namespace configurations.
class ServiceTestCase(unittest.TestCase):
    def test(self):
        kwargs = opts.kwargs.copy()

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

        app = "sdk-tests"
        user = "sdk-user"
        delete_app(service, app)
        delete_user(service, user)
        self.assertFalse(service.apps.contains(app))
        self.assertFalse(service.users.contains(user))

        # App & owner dont exist, verify that the following errors
        kwargs.update({ 'app': app, 'owner': user })
        with self.assertRaises(HTTPError):
            service_ns = client.connect(**kwargs)
            service_ns.apps()

        # Validate namespace permutations with new app & user
        create_app(service, app)
        create_user(service, user)

        kwargs.update({ 'app': app, 'owner': None })
        service_ns = client.connect(**kwargs)
        service_ns.apps()

        kwargs.update({ 'app': app, 'owner': "-" })
        service_ns = client.connect(**kwargs)
        service_ns.apps()

        kwargs.update({ 'app': None, 'owner': user })
        service_ns = client.connect(**kwargs)
        service_ns.apps()

        kwargs.update({ 'app': "-", 'owner': user })
        service_ns = client.connect(**kwargs)
        service_ns.apps()

        kwargs.update({ 'app': app, 'owner': user })
        service_ns = client.connect(**kwargs)
        service_ns.apps()

        # Cleanup
        delete_app(service, app)
        delete_user(service, user)

        self.assertFalse(service.apps.contains(app))
        self.assertFalse(service.users.contains(user))

class ClientTestCase(unittest.TestCase):
    def setUp(self):
        self.service = client.connect(**opts.kwargs)

    def assertHttp(self, allowed_error_codes, fn, *args, **kwargs):
        # This is a special case of "assertRaises", where we want to check
        # that HTTP calls return the right status.
        try:
            returnVal = fn(*args, **kwargs)
            return returnVal
        except HTTPError as e:
            error_msg = "Unexpected error code: %d" % e.status
            if (isinstance(allowed_error_codes, list)):
                self.assertTrue(e.status in allowed_error_Codes, error_msg)
            else:
                self.assertTrue(e.status == allowed_error_codes, error_msg)
        except Exception as e:
            self.fail("HTTPError not raised, caught %s instead", str(type(e)))

    def tearDown(self):
        pass

    def test_apps(self):
        service = self.service

        for app in service.apps: app.read()

        delete_app(service, 'sdk-tests')
        self.assertFalse(service.apps.contains('sdk-tests'))

        create_app(service, 'sdk-tests')
        self.assertTrue(service.apps.contains('sdk-tests'))

        testapp = service.apps['sdk-tests']
        self.assertTrue(testapp['author'] != "Splunk")
        testapp.update(author="Splunk")
        self.assertTrue(testapp['author'] == "Splunk")

        delete_app(service, 'sdk-tests')
        self.assertFalse(service.apps.contains('sdk-tests'))

    def test_capabilities(self):
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
        capabilities = self.service.capabilities
        for item in expected: self.assertTrue(item in capabilities)

    def test_confs(self):
        service = self.service

        for conf in service.confs:
            for stanza in conf: stanza.read()
            # no need to read every conf file for the test
            break

        self.assertTrue(service.confs.contains('props'))
        props = service.confs['props']

        stanza = props.create('sdk-tests')
        self.assertTrue(props.contains('sdk-tests'))
        self.assertEqual(stanza.name,'sdk-tests')
        self.assertTrue('maxDist' in stanza.read().keys())
        value = int(stanza['maxDist'])
        stanza.update(maxDist = value+1)
        self.assertEqual(stanza['maxDist'], str(value+1))
        stanza['maxDist'] = value
        self.assertEqual(stanza['maxDist'], str(value))

        props.delete('sdk-tests')
        self.assertFalse(props.contains('sdk-tests')) 

    def test_info(self):
        info = self.service.info
        keys = [
            "build", "cpu_arch", "guid", "isFree", "isTrial", "licenseKeys",
            "licenseSignature", "licenseState", "master_guid", "mode", 
            "os_build", "os_name", "os_version", "serverName", "version" ]
        for key in keys: self.assertTrue(key in info.keys())

    def test_indexes(self):
        service = self.service

        for index in service.indexes: index.read()

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
            entity = index.read()
            for attr in attrs: self.assertTrue(attr in entity.keys())

        index = service.indexes['sdk-tests']

        entity = index.read()
        self.assertEqual(index['disabled'], entity.disabled)

        index.disable()
        self.assertEqual(index['disabled'], '1')

        index.enable()
        self.assertEqual(index['disabled'], '0')
            
        index.clean()
        self.assertEqual(index['totalEventCount'], '0')

        cn = index.attach()
        cn.write("Hello World!")
        cn.close()
        wait_event_count(index, '1', 30)
        self.assertEqual(index['totalEventCount'], '1')

        index.submit("Hello again!!")
        wait_event_count(index, '2', 30)
        self.assertEqual(index['totalEventCount'], '2')

        # test must run on machine where splunkd runs,
        # otherwise an failure is expected
        testpath = path.dirname(path.abspath(__file__))
        index.upload(path.join(testpath, "testfile.txt"))
        wait_event_count(index, '3', 30)
        self.assertEqual(index['totalEventCount'], '3')

        index.clean()
        self.assertEqual(index['totalEventCount'], '0')

    def test_indexes_metadata(self):
        metadata = self.service.indexes.itemmeta()
        self.assertTrue(metadata.has_key('eai:acl'))
        self.assertTrue(metadata.has_key('eai:attributes'))
        for index in self.service.indexes:
            metadata = index.readmeta()
            self.assertTrue(metadata.has_key('eai:acl'))
            self.assertTrue(metadata.has_key('eai:attributes'))

    def test_inputs(self):
        inputs = self.service.inputs

        for input_ in inputs: input_.read()

        # Scan inputs and look for some common attributes
        # Note: The disabled flag appears to be the only common attribute, as
        # there are apparently cases where even index does not appear.
        expected = ['disabled']
        for input_ in inputs:
            attrs = input_.read()
            for attr in expected:  
                self.assertTrue(attr in attrs.keys())

        for kind in inputs.kinds:
            for input_ in inputs.list(kind):
                self.assertEqual(input_.kind, kind)

        if inputs.contains('tcp:9999'): inputs.delete('tcp:9999')
        self.assertFalse(inputs.contains('tcp:9999'))
        inputs.create("tcp", "9999", host="sdk-test")
        self.assertTrue(inputs.contains('tcp:9999'))
        input_ = inputs['tcp:9999']
        self.assertEqual(input_['host'], "sdk-test")
        input_.update(host="foo", sourcetype="bar")
        self.assertEqual(input_['host'], "foo")
        self.assertEqual(input_['sourcetype'], "bar")
        inputs.delete('tcp:9999')
        self.assertFalse(inputs.contains('tcp:9999'))

    def runjob(self, query, secs):
        """Create a job to run the given search and wait up to (approximately)
           the given number of seconds for it to complete.""" 
        job = self.service.jobs.create(query)
        return self.wait_for_completion(job, secs = secs)

    def wait_for_completion(self, job, secs = 30):
        done = False
        while not done and secs > 0:
            sleep(1)
            secs -= 1 # Approximate
            done = bool(int(job['isDone']))
        return job

    def check_properties(self, job, properties, secs = 10):
        while secs > 0 and len(properties) > 0:
            read_props = job()
            asserted = []

            # Try and check every property we specified. If we fail,
            # we'll try again later. If we succeed, delete it so we
            # don't check it again.
            for prop_name in properties.keys():
                try:
                    expected_value = properties[prop_name]
                    self.assertEqual(read_props[prop_name], expected_value)
                    
                    # Since we succeeded, delete it
                    del properties[prop_name]
                except:
                    pass

            secs -= 1
            sleep(1)

    def test_jobs(self):
        jobs = self.service.jobs

        for job in jobs: job.read()

        if not self.service.indexes.contains("sdk-tests"):
            self.service.indexes.create("sdk-tests")
        self.service.indexes['sdk-tests'].clean()

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
            entity = job.read()
            for attr in attrs: self.assertTrue(attr in entity.keys())

        # Make sure we can cancel the job
        job.cancel()
        self.assertFalse(jobs.contains(job.sid))

        # Search for non-existant data
        job = self.runjob("search index=sdk-tests TERM_DOES_NOT_EXIST", 10)
        self.assertTrue(bool(int(job['isDone'])))
        self.assertEqual(int(job['eventCount']), 0)
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

        # Assert that they got set properly
        self.check_properties(job, {
            'isPreviewEnabled': '1',
            'isPaused': '0',
            'isFinalized': '1'
        })

        # Run a new job to get the results, but we also make
        # sure that there is at least one event in the index already
        index = self.service.indexes['sdk-tests']
        old_event_count = int(index['totalEventCount'])
        if old_event_count == 0:
            index.submit("test event")
            wait_event_count(index, 1, 10)

        job = self.runjob("search index=sdk-tests | head 1 | stats count", 10)

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
        service = self.service

        levels = ["INFO", "WARN", "ERROR", "DEBUG", "CRIT"]
        for logger in service.loggers:
            self.assertTrue(logger['level'] in levels)

        self.assertTrue(service.loggers.contains("AuditLogger"))
        logger = service.loggers['AuditLogger']

        saved = logger['level']
        for level in levels:
            logger['level'] = level
            self.assertEqual(service.loggers['AuditLogger']['level'], level)
        logger.update(level=saved)
        self.assertEqual(service.loggers['AuditLogger']['level'], saved)

    def test_parse(self):
        response = self.service.parse("search *")
        self.assertEqual(response.status, 200)

        response = self.service.parse("search index=twitter status_count=* | stats count(status_source) as count by status_source | sort -count | head 20")
        self.assertEqual(response.status, 200)

        self.assertHttp(400, self.service.parse, "xyzzy")

    def test_messages(self):
        messages = self.service.messages

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
            messages.create([1,2,3], value="Who, me?")

    def test_restart(self):
        restart(self.service)
        self.service.login() # Make sure we are awake

    def test_roles(self):
        roles = self.service.roles

        capabilities = self.service.capabilities
        for role in roles:
            entity = role.read()
            for capability in entity.capabilities:
                self.assertTrue(capability in capabilities)

        if roles.contains("sdk-tester"): roles.delete("sdk-tester")
        self.assertFalse(roles.contains("sdk-tester"))

        role = roles.create("sdk-tester")
        self.assertTrue(roles.contains("sdk-tester"))

        entity = role.read()
        self.assertTrue(entity.has_key('capabilities'))

        roles.delete("sdk-tester")
        self.assertFalse(roles.contains("sdk-tester"))

    def test_settings(self):
        settings = self.service.settings

        # Verify that settings contains the keys we expect
        keys = [
            "SPLUNK_DB", "SPLUNK_HOME", "enableSplunkWebSSL", "host",
            "httpport", "mgmtHostPort", "minFreeSpace", "pass4SymmKey",
            "serverName", "sessionTimeout", "startwebserver", "trustedIP"
        ]
        attrs = settings.read()
        for key in keys: self.assertTrue(key in attrs.keys())

        # Verify that we can update the settings
        original = settings['sessionTimeout']
        self.assertTrue(original != "42h")
        settings.update(sessionTimeout="42h")
        updated = settings['sessionTimeout']
        self.assertEquals(updated, "42h")

        # Restore (and verify) original value
        settings.update(sessionTimeout=original)
        updated = settings['sessionTimeout']
        self.assertEquals(updated, original)

    def test_users(self):
        users = self.service.users
        roles = self.service.roles

        # Verify that we can read the users collection
        for user in users:
            entity = user.read()
            for role in entity.roles:
                self.assertTrue(roles.contains(role))

        if users.contains("sdk-user"):  users.delete("sdk-user")
        self.assertFalse(users.contains("sdk-user"))

        user = users.create("sdk-user", password="changeme", roles="power")
        self.assertTrue(users.contains("sdk-user"))

        # Verify the new user has the expected attributes
        attrs = user.read()
        self.assertTrue(attrs.has_key('email'))
        self.assertTrue(attrs.has_key('password'))
        self.assertTrue(attrs.has_key('realname'))
        self.assertTrue(attrs.has_key('roles'))

        # Verify that we can update the user
        self.assertTrue(user['email'] is None)
        user.update(email="foo@bar.com")
        self.assertTrue(user['email'] == "foo@bar.com")

        # Verify that we can delete the user
        users.delete("sdk-user")
        self.assertFalse(users.contains("sdk-user"))

        # Splunk lowercases new users names, verify this works as expected
        self.assertFalse(users.contains("sdk-user"))
        self.assertFalse(users.contains("SDK-User"))

        user = users.create("SDK-User", password="changeme", roles="power")
        self.assertTrue(user.name == "sdk-user")
        self.assertFalse(users.contains("SDK-User"))
        self.assertTrue(users.contains("sdk-user"))

        users.delete("sdk-user")
        self.assertFalse(users.contains("sdk-user"))

# Runs the given named test, useful for debugging.
def runone(test):
    suite = unittest.TestSuite()
    suite.addTest(test)
    unittest.TextTestRunner().run(suite)
        
if __name__ == "__main__":
    opts = parse(sys.argv[1:], {}, ".splunkrc")
    #runone(ClientTestCase("test_inputs"))
    unittest.main(argv=sys.argv[:1])

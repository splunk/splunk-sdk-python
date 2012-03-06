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

import difflib
import os
from pprint import pprint
from subprocess import PIPE, Popen
import time
import unittest 
import sys

import splunk.client

from utils import parse

opts = None # Command line options

def assertMultiLineEqual(test, first, second, msg=None):
    """Assert that two multi-line strings are equal."""
    test.assertTrue(isinstance(first, basestring), 
        'First argument is not a string')
    test.assertTrue(isinstance(second, basestring), 
        'Second argument is not a string')
    # Unix-ize Windows EOL
    first = first.replace("\r", "")
    second = second.replace("\r", "")
    if first != second:
        test.fail("Multiline strings are not equal: %s" % msg)

# Run the given python script and return its exit code. 
def run(script, stdin=None, stdout=PIPE, stderr=None):
    process = start(script, stdin, stdout, stderr)
    process.communicate()
    return process.wait()

# Start the given python script and return the corresponding process object.
# The script can be specified as either a string or arg vector. In either case
# it will be prefixed to invoke python explicitly.
def start(script, stdin=None, stdout=PIPE, stderr=None):
    if isinstance(script, str):
        script = script.split()
    script = ["python"] + script
    return Popen(script, stdin=stdin, stdout=stdout, stderr=stderr)

# Rudimentary sanity check for each of the examples
class ExamplesTestCase(unittest.TestCase):
    def setUp(self):
        # Ignore result, it might already exist
        run("index.py create sdk-tests")
        run("index.py create sdk-tests-two")

    def tearDown(self):
        pass

    def test_binding1(self):
        result = run("binding1.py")
        self.assertEquals(result, 0)

    def test_conf(self):
        commands = [
            "conf.py --help",
            "conf.py",
            "conf.py viewstates",
            'conf.py --app=search --owner=admin viewstates',
            "conf.py create server SDK-STANZA",
            "conf.py create server SDK-STANZA testkey=testvalue",
            "conf.py delete server SDK-STANZA"
        ]
        for command in commands: self.assertEquals(run(command), 0)

    def test_async(self):
        result = run("async/async.py sync")
        self.assertEquals(result, 0)

        try:
            # Only try running the async version of the test if eventlet
            # is present on the system
            import eventlet
            result = run("async/async.py async")
            self.assertEquals(result, 0)
        except:
            pass

    def test_follow(self):
        result = run("follow.py --help")
        self.assertEquals(result, 0)

    def test_handlers(self):
        commands = [
            "handlers/handler_urllib2.py",
            "handlers/handler_debug.py",
            "handlers/handler_certs.py",
            "handlers/handler_certs.py --ca_file=handlers/cacert.pem",
            "handlers/handler_proxy.py --help",
        ]
        for command in commands: self.assertEquals(run(command), 0)

        # Run the cert handler example with a bad cert file, should error.
        result = run("handlers/handlers_certs.py --ca_file=handlers/cacert.bad.pem", stderr=PIPE)
        self.assertNotEquals(result, 0)

        # The proxy handler example requires that there be a proxy available
        # to relay requests, so we spin up a local proxy using the proxy
        # script included with the sample.

        # Assumes that tiny-proxy.py is in the same directory as the sample
        process = start("handlers/tiny-proxy.py -p 8080", stderr=PIPE)
        try:
            time.sleep(2) # Wait for proxy to finish initializing
            result = run("handlers/handler_proxy.py --proxy=localhost:8080")
            self.assertEquals(result, 0)
        finally:
            process.kill()

        # Run it again without the proxy and it should fail.
        result = run("handlers/handler_proxy.py --proxy=localhost:80801", stderr=PIPE)
        self.assertNotEquals(result, 0)

    def test_index(self):
        commands = [
            "index.py --help",
            "index.py",
            "index.py list",
            "index.py list sdk-tests-two",
            "index.py disable sdk-tests-two",
            "index.py enable sdk-tests-two",
            "index.py clean sdk-tests-two",
        ]
        for command in commands: self.assertEquals(run(command), 0)

    def test_info(self):
        result = run("info.py")
        self.assertEquals(result, 0)

    def test_inputs(self):
        commands = [
            "inputs.py --help",
            "inputs.py",
        ]
        for command in commands: self.assertEquals(run(command), 0)
        
    def test_job(self):
        commands = [
            "job.py --help",
            "job.py",
            "job.py list",
            "job.py list @0",
        ]
        for command in commands: self.assertEquals(run(command), 0)
        
    def test_loggers(self):
        commands = [
            "loggers.py --help",
            "loggers.py",
        ]
        for command in commands: self.assertEquals(run(command), 0)

    def test_oneshot(self):
        result = run(["oneshot.py", "search * | head 10"])
        self.assertEquals(result, 0)
        
    def test_search(self):
        commands = [
            "search.py --help",
            ["search.py", "search * | head 10"],
            ["search.py", "search * | head 10 | stats count", '--output_mode=csv']
        ]
        for command in commands: self.assertEquals(run(command), 0)

    def test_spcmd(self):
        result = run("spcmd.py --help")
        self.assertEquals(result, 0)

        result = run("spcmd.py -e\"get('authentication/users')\"")
        self.assertEquals(result, 0)

    def test_spurl(self):
        result = run("spurl.py")
        self.assertEquals(result, 0)

        result = run("spurl.py --help")
        self.assertEquals(result, 0)

        result = run("spurl.py /services")
        self.assertEquals(result, 0)

        result = run("spurl.py apps/local")
        self.assertEquals(result, 0)

    def test_submit(self):
        result = run("submit.py --help")
        self.assertEquals(result, 0)

    def test_upload(self):
        # Note: test must run on machine where splunkd runs,
        # or a failure is expected
        commands = [
            "upload.py --help",
            "upload.py --index=sdk-tests ./upload.py"
        ]
        for command in commands: self.assertEquals(run(command), 0)

    # The following tests are for the custom_search examples. The way
    # the tests work mirrors how Splunk would invoke them: they pipe in
    # a known good input file into the custom search python file, and then
    # compare the resulting output file to a known good one.
    def test_custom_search(self):

        def test_custom_search_command(script, input_path, baseline_path):
            output_base, _ = os.path.splitext(input_path)
            output_path = output_base + ".out"
            output_file = open(output_path, 'w')

            input_file = open(input_path, 'r')

            # Execute the command
            result = run(script, stdin=input_file, stdout=output_file)
            self.assertEquals(result, 0)

            input_file.close()
            output_file.close()

            # Make sure the test output matches the baseline
            baseline_file = open(baseline_path, 'r')
            baseline = baseline_file.read()

            output_file = open(output_path, 'r')
            output = output_file.read()

            message = "%s != %s" % (output_file.name, baseline_file.name)
            assertMultiLineEqual(self, baseline, output, message)

            # Cleanup
            baseline_file.close()
            output_file.close()
            os.remove(output_path)

        custom_searches = [ 
            {
                "script": "custom_search/bin/usercount.py",
                "input": "../tests/custom_search/usercount.in",
                "baseline": "../tests/custom_search/usercount.baseline"
            },
            { 
                "script": "twitted/twitted/bin/hashtags.py",
                "input": "../tests/custom_search/hashtags.in",
                "baseline": "../tests/custom_search/hashtags.baseline"
            },
            { 
                "script": "twitted/twitted/bin/tophashtags.py",
                "input": "../tests/custom_search/tophashtags.in",
                "baseline": "../tests/custom_search/tophashtags.baseline"
            }
        ]

        for custom_search in custom_searches:
            test_custom_search_command(
                custom_search['script'],
                custom_search['input'],
                custom_search['baseline'])

    # The following tests are for the Analytics example
    def test_analytics(self):
        # We have to add the current path to the PYTHONPATH,
        # otherwise the import doesn't work quite right
        sys.path.append(os.getcwd())
        import analytics

        # Create a tracker
        tracker = analytics.input.AnalyticsTracker("sdk-test", opts.kwargs, index = "sdk-test")

        service = splunk.client.connect(**opts.kwargs)

        # Before we start, we'll clean the index
        index = service.indexes["sdk-test"]
        index.clean()
        
        tracker.track("test_event", distinct_id="abc123", foo="bar", abc="123")
        tracker.track("test_event", distinct_id="123abc", abc="12345")

        # Wait until the events get indexed
        wait_event_count(index, 2, 10)

        # Now, we create a retriever to retrieve the events
        retriever = analytics.output.AnalyticsRetriever("sdk-test", opts.kwargs, index = "sdk-test")    
        
        # Assert applications
        applications = retriever.applications()
        self.assertEquals(len(applications), 1)
        self.assertEquals(applications[0]["name"], "sdk-test")
        self.assertEquals(applications[0]["count"], 2)

        # Assert events
        events = retriever.events()
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["name"], "test_event")
        self.assertEqual(events[0]["count"], 2)

        # Assert properties
        expected_properties = {
            "abc": 2,
            "foo": 1
        }
        properties = retriever.properties("test_event")
        self.assertEqual(len(properties), len(expected_properties))
        for prop in properties:
            name = prop["name"]
            count = prop["count"]
            self.assertTrue(name in expected_properties.keys())
            self.assertEqual(count, expected_properties[name])

        # Assert property values
        expected_property_values = {
            "123": 1,
            "12345": 1
        }
        values = retriever.property_values("test_event", "abc")
        self.assertEqual(len(values), len(expected_property_values))
        for value in values:
            name = value["name"]
            count = value["count"]
            self.assertTrue(name in expected_property_values.keys())
            self.assertEqual(count, expected_property_values[name])
            
        # Assert event over time
        over_time = retriever.events_over_time(time_range = analytics.output.TimeRange.MONTH)
        self.assertEquals(len(over_time), 1)
        self.assertEquals(len(over_time["test_event"]), 1)
        self.assertEquals(over_time["test_event"][0]["count"], 2)

        # Now that we're done, we'll clean the index 
        index.clean()
 
# When an event is submitted to an index it takes a while before the event
# is registered by the index's totalEventCount.
def wait_event_count(index, count, secs):
    """Wait up to the given number of secs for the given index's
       totalEventCount to reach the given value."""
    done = False
    while not done and secs > 0:
        time.sleep(1)
        secs -= 1 # Approximate
        done = index['totalEventCount'] == count

if __name__ == "__main__":
    opts = parse(sys.argv[1:], {}, ".splunkrc")
    os.chdir("../examples")
    # Don't pass the Splunk cmdline args to unittest
    unittest.main(argv=sys.argv[:1])

#!/usr/bin/env python
#
# Copyright 2011-2013 Splunk, Inc.
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

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from splunklib.searchcommands import Configuration, StreamingCommand
from cStringIO import StringIO


@Configuration()
class SearchCommand(StreamingCommand):

    def stream(self, records):
        value = 0
        for record in records:
            action = record['Action']
            if action == 'raise_error':
                raise RuntimeError('Testing')
            yield {'Data': value}
            value += 1
        return

class TestSearchCommandsCommand(unittest.TestCase):

    def setUp(self):
        super(TestSearchCommandsCommand, self).setUp()
        return

    def test_process(self):

        # Command.process should complain if supports_getinfo == False
        # We support dynamic configuration, not static

        expected = \
            'error_message=Command search appears to be statically configured and static configuration is unsupported by splunklib.searchcommands. Please ensure that default/commands.conf contains this stanza: [search] | filename = foo.py | supports_getinfo = true | supports_rawargs = true | outputheader = true\r\n' \
            '\r\n'

        command = SearchCommand()
        result = StringIO()
        command.process(['foo.py'], output_file=result)
        result.reset()
        observed = result.read()
        self.assertEqual(observed, expected)

        # Command.process should return configuration settings on Getinfo probe

        expected = \
            '\r\n' \
            'changes_colorder,clear_required_fields,enableheader,generating,local,maxinputs,needs_empty_results,outputheader,overrides_timeorder,passauth,perf_warn_limit,required_fields,requires_srinfo,retainsevents,run_in_preview,stderr_dest,streaming,supports_multivalues,supports_rawargs,__mv_changes_colorder,__mv_clear_required_fields,__mv_enableheader,__mv_generating,__mv_local,__mv_maxinputs,__mv_needs_empty_results,__mv_outputheader,__mv_overrides_timeorder,__mv_passauth,__mv_perf_warn_limit,__mv_required_fields,__mv_requires_srinfo,__mv_retainsevents,__mv_run_in_preview,__mv_stderr_dest,__mv_streaming,__mv_supports_multivalues,__mv_supports_rawargs\r\n' \
            '1,0,1,0,0,0,1,1,0,0,0,,0,1,1,log,1,1,1,,,,,,,,,,,,,,,,,,,\r\n'

        command = SearchCommand()
        result = StringIO()
        command.process(['foo.py', '__GETINFO__'], output_file=result)
        result.reset()
        observed = result.read()
        self.assertEqual(observed, expected)

        # Command.process should produce an error record on parser errors, if
        # invoked to get configuration settings

        expected = \
            '\r\n' \
            'ERROR,__mv_ERROR\r\n' \
            'Unrecognized option: undefined_option = value,\r\n'

        command = SearchCommand()
        result = StringIO()
        command.process(['foo.py', '__GETINFO__', 'undefined_option=value'], output_file=result)
        result.reset()
        observed = result.read()
        self.assertEqual(observed, expected)

        # Command.process should produce an error message and exit on parser
        # errors, if invoked to execute

        expected = \
            'error_message=Unrecognized option: undefined_option = value\r\n' \
            '\r\n'

        command = SearchCommand()
        result = StringIO()

        try:
            command.process(args=['foo.py', '__EXECUTE__', 'undefined_option=value'], input_file=StringIO('\r\n'), output_file=result)
        except SystemExit as e:
            result.reset()
            observed = result.read()
            self.assertEqual(e.code != 0)
            self.assertEqual(observed, expected)
        except BaseException as e:
            self.fail("Expected SystemExit, but caught %s" % type(e))
        else:
            self.fail("Expected SystemExit, but no exception was raised")

        # Command.process should exit on processing exceptions

        command = SearchCommand()
        result = StringIO()

        try:
            command.process(args=['foo.py', '__EXECUTE__'], input_file=StringIO('\r\nAction\r\nraise_error'), output_file=result)
        except SystemExit as e:
            result.reset()
            observed = result.read()
            self.assertEqual(e.code != 0)
            self.assertEqual(observed, expected)
        except BaseException as e:
            self.fail("Expected SystemExit, but caught %s" % type(e))
        else:
            self.fail("Expected SystemExit, but no exception was raised")

        return

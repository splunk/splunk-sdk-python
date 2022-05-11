#!/usr/bin/env python
# coding=utf-8
#
# Copyright 2011-2015 Splunk, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"): you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from json.encoder import encode_basestring as encode_string
from unittest import main, TestCase

import csv
import codecs
import os
import re

from io import TextIOWrapper

import pytest

from splunklib import six
from splunklib.searchcommands import Configuration, StreamingCommand
from splunklib.searchcommands.decorators import ConfigurationSetting, Option
from splunklib.searchcommands.search_command import SearchCommand
from splunklib.client import Service

from splunklib.six import StringIO, BytesIO


def build_command_input(getinfo_metadata, execute_metadata, execute_body):
    input = (f'chunked 1.0,{len(six.ensure_binary(getinfo_metadata))},0\n{getinfo_metadata}' +
             f'chunked 1.0,{len(six.ensure_binary(execute_metadata))},{len(six.ensure_binary(execute_body))}\n{execute_metadata}{execute_body}')

    ifile = BytesIO(six.ensure_binary(input))

    ifile = TextIOWrapper(ifile)

    return ifile


@Configuration()
class TestCommand(SearchCommand):
    required_option_1 = Option(require=True)
    required_option_2 = Option(require=True)

    def echo(self, records):
        for record in records:
            if record.get('action') == 'raise_exception':
                raise Exception(self)
            yield record

    def _execute(self, ifile, process):
        SearchCommand._execute(self, ifile, self.echo)

    class ConfigurationSettings(SearchCommand.ConfigurationSettings):

        # region SCP v1/v2 properties

        generating = ConfigurationSetting()
        required_fields = ConfigurationSetting()
        streaming_preop = ConfigurationSetting()

        # endregion

        # region SCP v1 properties

        clear_required_fields = ConfigurationSetting()
        generates_timeorder = ConfigurationSetting()
        overrides_timeorder = ConfigurationSetting()
        requires_preop = ConfigurationSetting()
        retainsevents = ConfigurationSetting()
        streaming = ConfigurationSetting()

        # endregion

        # region SCP v2 properties

        distributed = ConfigurationSetting()
        maxinputs = ConfigurationSetting()
        run_in_preview = ConfigurationSetting()
        type = ConfigurationSetting()

        # endregion


@Configuration()
class TestStreamingCommand(StreamingCommand):
    def stream(self, records):
        serial_number = 0
        for record in records:
            action = record['action']
            if action == 'raise_error':
                raise RuntimeError('Testing')
            value = self.search_results_info if action == 'get_search_results_info' else None
            yield {'_serial': serial_number, 'data': value}
            serial_number += 1


@pytest.mark.smoke
class TestSearchCommand(TestCase):
    def setUp(self):
        TestCase.setUp(self)

    def test_process_scpv1(self):

        # TestCommand.process should complain if supports_getinfo == False
        # We support dynamic configuration, not static

        # The exception line number may change, so we're using a regex match instead of a string match

        expected = re.compile(
            r'error_message=RuntimeError at ".+search_command\.py", line \d\d\d : Command test appears to be '
            r'statically configured for search command protocol version 1 and static configuration is unsupported by '
            r'splunklib.searchcommands. Please ensure that default/commands.conf contains this stanza:\n'
            r'\[test\]\n'
            r'filename = test.py\n'
            r'enableheader = true\n'
            r'outputheader = true\n'
            r'requires_srinfo = true\n'
            r'supports_getinfo = true\n'
            r'supports_multivalues = true\n'
            r'supports_rawargs = true')

        argv = ['test.py', 'not__GETINFO__or__EXECUTE__', 'option=value', 'fieldname']
        command = TestCommand()
        result = BytesIO()

        self.assertRaises(SystemExit, command.process, argv, ofile=result)
        six.assertRegex(self, result.getvalue().decode('UTF-8'), expected)

        # TestCommand.process should return configuration settings on Getinfo probe

        argv = ['test.py', '__GETINFO__', 'required_option_1=value', 'required_option_2=value']
        command = TestCommand()
        ifile = StringIO('\n')
        result = BytesIO()

        self.assertEqual(str(command.configuration), '')

        expected = (
            "[('clear_required_fields', None, [1]), ('distributed', None, [2]), ('generates_timeorder', None, [1]), "
            "('generating', None, [1, 2]), ('maxinputs', None, [2]), ('overrides_timeorder', None, [1]), "
            "('required_fields', None, [1, 2]), ('requires_preop', None, [1]), ('retainsevents', None, [1]), "
            "('run_in_preview', None, [2]), ('streaming', None, [1]), ('streaming_preop', None, [1, 2]), "
            "('type', None, [2])]")

        self.assertEqual(
            repr(command.configuration), expected)

        try:
            # noinspection PyTypeChecker
            command.process(argv, ifile, ofile=result)
        except BaseException as error:
            self.fail('{0}: {1}: {2}\n'.format(type(error).__name__, error, result.getvalue().decode('UTF-8')))

        self.assertEqual('\r\n\r\n\r\n',
                         result.getvalue().decode('UTF-8'))  # No message header and no configuration settings

        ifile = StringIO('\n')
        result = BytesIO()

        # We might also put this sort of code into our SearchCommand.prepare override ...

        configuration = command.configuration

        # SCP v1/v2 configuration settings
        configuration.generating = True
        configuration.required_fields = ['foo', 'bar']
        configuration.streaming_preop = 'some streaming command'

        # SCP v1 configuration settings
        configuration.clear_required_fields = True
        configuration.generates_timeorder = True
        configuration.overrides_timeorder = True
        configuration.requires_preop = True
        configuration.retainsevents = True
        configuration.streaming = True

        # SCP v2 configuration settings (SCP v1 requires that maxinputs and run_in_preview are set in commands.conf)
        configuration.distributed = True
        configuration.maxinputs = 50000
        configuration.run_in_preview = True
        configuration.type = 'streaming'

        expected = (
            'clear_required_fields="True", generates_timeorder="True", generating="True", overrides_timeorder="True", '
            'required_fields="[\'foo\', \'bar\']", requires_preop="True", retainsevents="True", streaming="True", '
            'streaming_preop="some streaming command"')
        self.assertEqual(str(command.configuration), expected)

        expected = (
            "[('clear_required_fields', True, [1]), ('distributed', True, [2]), ('generates_timeorder', True, [1]), "
            "('generating', True, [1, 2]), ('maxinputs', 50000, [2]), ('overrides_timeorder', True, [1]), "
            "('required_fields', ['foo', 'bar'], [1, 2]), ('requires_preop', True, [1]), "
            "('retainsevents', True, [1]), ('run_in_preview', True, [2]), ('streaming', True, [1]), "
            "('streaming_preop', 'some streaming command', [1, 2]), ('type', 'streaming', [2])]")

        self.assertEqual(
            repr(command.configuration), expected)

        try:
            # noinspection PyTypeChecker
            command.process(argv, ifile, ofile=result)
        except BaseException as error:
            self.fail('{0}: {1}: {2}\n'.format(type(error).__name__, error, result.getvalue().decode('UTF-8')))

        result.seek(0)
        reader = csv.reader(codecs.iterdecode(result, 'UTF-8'))
        self.assertEqual([], next(reader))
        observed = dict(list(zip(next(reader), next(reader))))
        self.assertRaises(StopIteration, lambda: next(reader))

        expected = {
            'clear_required_fields': '1', '__mv_clear_required_fields': '',
            'generating': '1', '__mv_generating': '',
            'generates_timeorder': '1', '__mv_generates_timeorder': '',
            'overrides_timeorder': '1', '__mv_overrides_timeorder': '',
            'requires_preop': '1', '__mv_requires_preop': '',
            'required_fields': 'foo,bar', '__mv_required_fields': '',
            'retainsevents': '1', '__mv_retainsevents': '',
            'streaming': '1', '__mv_streaming': '',
            'streaming_preop': 'some streaming command', '__mv_streaming_preop': '',
        }

        self.assertDictEqual(expected, observed)  # No message header and no configuration settings

        for action in '__GETINFO__', '__EXECUTE__':
            # TestCommand.process should produce an error record on parser errors

            argv = [
                'test.py', action, 'required_option_1=value', 'required_option_2=value', 'undefined_option=value',
                'fieldname_1', 'fieldname_2']

            command = TestCommand()
            ifile = StringIO('\n')
            result = BytesIO()

            self.assertRaises(SystemExit, command.process, argv, ifile, ofile=result)
            self.assertTrue(
                'error_message=Unrecognized test command option: undefined_option="value"\r\n\r\n',
                result.getvalue().decode('UTF-8'))

            # TestCommand.process should produce an error record when required options are missing

            argv = ['test.py', action, 'required_option_2=value', 'fieldname_1']
            command = TestCommand()
            ifile = StringIO('\n')
            result = BytesIO()

            self.assertRaises(SystemExit, command.process, argv, ifile, ofile=result)

            self.assertTrue(
                'error_message=A value for test command option required_option_1 is required\r\n\r\n',
                result.getvalue().decode('UTF-8'))

            argv = ['test.py', action, 'fieldname_1']
            command = TestCommand()
            ifile = StringIO('\n')
            result = BytesIO()

            self.assertRaises(SystemExit, command.process, argv, ifile, ofile=result)

            self.assertTrue(
                'error_message=Values for these test command options are required: required_option_1, required_option_2'
                '\r\n\r\n',
                result.getvalue().decode('UTF-8'))

        # TestStreamingCommand.process should exit on processing exceptions

        ifile = StringIO('\naction\r\nraise_error\r\n')
        argv = ['test.py', '__EXECUTE__']
        command = TestStreamingCommand()
        result = BytesIO()

        try:
            # noinspection PyTypeChecker
            command.process(argv, ifile, ofile=result)
        except SystemExit as error:
            self.assertNotEqual(error.code, 0)
            six.assertRegex(
                self,
                result.getvalue().decode('UTF-8'),
                r'^error_message=RuntimeError at ".+", line \d+ : Testing\r\n\r\n$')
        except BaseException as error:
            self.fail('Expected SystemExit, but caught {}: {}'.format(type(error).__name__, error))
        else:
            self.fail('Expected SystemExit, but no exception was raised')

        # Command.process should provide access to search results info
        info_path = os.path.join(
            self._package_directory, 'recordings', 'scpv1', 'Splunk-6.3', 'countmatches.execute.dispatch_dir',
            'externSearchResultsInfo.csv')

        ifile = StringIO('infoPath:' + info_path + '\n\naction\r\nget_search_results_info\r\n')
        argv = ['test.py', '__EXECUTE__']
        command = TestStreamingCommand()
        result = BytesIO()

        try:
            # noinspection PyTypeChecker
            command.process(argv, ifile, ofile=result)
        except BaseException as error:
            self.fail(f'Expected no exception, but caught {type(error).__name__}: {error}')
        else:
            six.assertRegex(
                self,
                result.getvalue().decode('UTF-8'),
                r'^\r\n'
                r'('
                r'data,__mv_data,_serial,__mv__serial\r\n'
                r'\"\{.*u\'is_summary_index\': 0, .+\}\",,0,'
                r'|'
                r'_serial,__mv__serial,data,__mv_data\r\n'
                r'0,,\"\{.*\'is_summary_index\': 0, .+\}\",'
                r')'
                r'\r\n$'
            )

        # TestStreamingCommand.process should provide access to a service object when search results info is available

        self.assertIsInstance(command.service, Service)

        self.assertEqual(command.service.authority,
                         command.search_results_info.splunkd_uri)

        self.assertEqual(command.service.scheme,
                         command.search_results_info.splunkd_protocol)

        self.assertEqual(command.service.port,
                         command.search_results_info.splunkd_port)

        self.assertEqual(command.service.token,
                         command.search_results_info.auth_token)

        self.assertEqual(command.service.namespace.app,
                         command.search_results_info.ppc_app)

        self.assertEqual(command.service.namespace.owner,
                         None)
        self.assertEqual(command.service.namespace.sharing,
                         None)

        # Command.process should not provide access to search results info or a service object when the 'infoPath'
        # input header is unavailable

        ifile = StringIO('\naction\r\nget_search_results_info')
        argv = ['teststreaming.py', '__EXECUTE__']
        command = TestStreamingCommand()

        # noinspection PyTypeChecker
        command.process(argv, ifile, ofile=result)

        self.assertIsNone(command.search_results_info)
        self.assertIsNone(command.service)

    def test_process_scpv2(self):

        # SearchCommand.process should

        # 1. Recognize all standard options:

        metadata = (
            '{{'
            '"action": "getinfo", "preview": false, "searchinfo": {{'
            '"latest_time": "0",'
            '"splunk_version": "20150522",'
            '"username": "admin",'
            '"app": "searchcommands_app",'
            '"args": ['
            '"logging_configuration={logging_configuration}",'
            '"logging_level={logging_level}",'
            '"record={record}",'
            '"show_configuration={show_configuration}",'
            '"required_option_1=value_1",'
            '"required_option_2=value_2"'
            '],'
            '"search": "Ａ%7C%20inputlookup%20tweets%20%7C%20countmatches%20fieldname%3Dword_count%20pattern%3D%22%5Cw%2B%22%20text%20record%3Dt%20%7C%20export%20add_timestamp%3Df%20add_offset%3Dt%20format%3Dcsv%20segmentation%3Draw",'
            '"earliest_time": "0",'
            '"session_key": "0JbG1fJEvXrL6iYZw9y7tmvd6nHjTKj7ggaE7a4Jv5R0UIbeYJ65kThn^3hiNeoqzMT_LOtLpVR3Y8TIJyr5bkHUElMijYZ8l14wU0L4n^Oa5QxepsZNUIIQCBm^",'
            '"owner": "admin",'
            '"sid": "1433261372.158",'
            '"splunkd_uri": "https://127.0.0.1:8089",'
            '"dispatch_dir": {dispatch_dir},'
            '"raw_args": ['
            '"logging_configuration={logging_configuration}",'
            '"logging_level={logging_level}",'
            '"record={record}",'
            '"show_configuration={show_configuration}",'
            '"required_option_1=value_1",'
            '"required_option_2=value_2"'
            '],'
            '"maxresultrows": 10,'
            '"command": "countmatches"'
            '}}'
            '}}')

        basedir = self._package_directory

        default_logging_configuration = os.path.join(basedir, 'apps', 'app_with_logging_configuration', 'default',
                                                     'logging.conf')
        dispatch_dir = os.path.join(basedir, 'recordings', 'scpv2', 'Splunk-6.3', 'countmatches.dispatch_dir')
        logging_configuration = os.path.join(basedir, 'apps', 'app_with_logging_configuration', 'logging.conf')
        logging_level = 'ERROR'
        record = False
        show_configuration = True

        getinfo_metadata = metadata.format(
            dispatch_dir=encode_string(dispatch_dir),
            logging_configuration=encode_string(logging_configuration)[1:-1],
            logging_level=logging_level,
            record=('true' if record is True else 'false'),
            show_configuration=('true' if show_configuration is True else 'false'))

        execute_metadata = '{"action":"execute","finished":true}'
        execute_body = 'test\r\ndata\r\n测试\r\n'

        ifile = build_command_input(getinfo_metadata, execute_metadata, execute_body)

        command = TestCommand()
        result = BytesIO()
        argv = ['some-external-search-command.py']

        self.assertEqual(command.logging_level, 'WARNING')
        self.assertIs(command.record, None)
        self.assertIs(command.show_configuration, None)

        try:
            # noinspection PyTypeChecker
            command.process(argv, ifile, ofile=result)
        except SystemExit as error:
            self.fail('Unexpected exception: {}: {}'.format(type(error).__name__, error))

        self.assertEqual(command.logging_configuration, logging_configuration)
        self.assertEqual(command.logging_level, 'ERROR')
        self.assertEqual(command.record, record)
        self.assertEqual(command.show_configuration, show_configuration)
        self.assertEqual(command.required_option_1, 'value_1')
        self.assertEqual(command.required_option_2, 'value_2')

        expected = (
            'chunked 1.0,68,0\n'
            '{"inspector":{"messages":[["INFO","test command configuration: "]]}}\n'
            'chunked 1.0,17,32\n'
            '{"finished":true}test,__mv_test\r\n'
            'data,\r\n'
            '测试,\r\n'
        )

        self.assertEqual(
            expected,
            result.getvalue().decode('utf-8'))

        self.assertEqual(command.protocol_version, 2)

        # 2. Provide access to these properties:
        #   fieldnames
        #   input_header
        #   metadata
        #   search_results_info
        #   service

        self.assertEqual([], command.fieldnames)

        command_metadata = command.metadata
        input_header = command.input_header

        self.assertIsNone(input_header['allowStream'])
        self.assertEqual(input_header['infoPath'], os.path.join(command_metadata.searchinfo.dispatch_dir, 'info.csv'))
        self.assertIsNone(input_header['keywords'])
        self.assertEqual(input_header['preview'], command_metadata.preview)
        self.assertIs(input_header['realtime'], False)
        self.assertEqual(input_header['search'], command_metadata.searchinfo.search)
        self.assertEqual(input_header['sid'], command_metadata.searchinfo.sid)
        self.assertEqual(input_header['splunkVersion'], command_metadata.searchinfo.splunk_version)
        self.assertIsNone(input_header['truncated'])

        self.assertEqual(command_metadata.preview, input_header['preview'])
        self.assertEqual(command_metadata.searchinfo.app, 'searchcommands_app')
        self.assertEqual(command_metadata.searchinfo.args,
                         ['logging_configuration=' + logging_configuration, 'logging_level=ERROR', 'record=false',
                          'show_configuration=true', 'required_option_1=value_1', 'required_option_2=value_2'])
        self.assertEqual(command_metadata.searchinfo.dispatch_dir, os.path.dirname(input_header['infoPath']))
        self.assertEqual(command_metadata.searchinfo.earliest_time, 0.0)
        self.assertEqual(command_metadata.searchinfo.latest_time, 0.0)
        self.assertEqual(command_metadata.searchinfo.owner, 'admin')
        self.assertEqual(command_metadata.searchinfo.raw_args, command_metadata.searchinfo.args)
        self.assertEqual(command_metadata.searchinfo.search,
                         'Ａ| inputlookup tweets | countmatches fieldname=word_count pattern="\\w+" text record=t | export add_timestamp=f add_offset=t format=csv segmentation=raw')
        self.assertEqual(command_metadata.searchinfo.session_key,
                         '0JbG1fJEvXrL6iYZw9y7tmvd6nHjTKj7ggaE7a4Jv5R0UIbeYJ65kThn^3hiNeoqzMT_LOtLpVR3Y8TIJyr5bkHUElMijYZ8l14wU0L4n^Oa5QxepsZNUIIQCBm^')
        self.assertEqual(command_metadata.searchinfo.sid, '1433261372.158')
        self.assertEqual(command_metadata.searchinfo.splunk_version, '20150522')
        self.assertEqual(command_metadata.searchinfo.splunkd_uri, 'https://127.0.0.1:8089')
        self.assertEqual(command_metadata.searchinfo.username, 'admin')
        self.assertEqual(command_metadata.searchinfo.maxresultrows, 10)
        self.assertEqual(command_metadata.searchinfo.command, 'countmatches')

        command.search_results_info.search_metrics = command.search_results_info.search_metrics.__dict__
        command.search_results_info.optional_fields_json = command.search_results_info.optional_fields_json.__dict__

        self.maxDiff = None

        self.assertDictEqual(command.search_results_info.__dict__, {
            'is_summary_index': 0,
            'bs_thread_count': 1,
            'rt_backfill': 0,
            'rtspan': '',
            'search_StartTime': 1433261392.934936,
            'read_raw': 1,
            'root_sid': '',
            'field_rendering': '',
            'query_finished': 1,
            'optional_fields_json': {},
            'group_list': '',
            'remoteServers': '',
            'rt_latest': '',
            'remote_log_download_mode': 'disabled',
            'reduce_search': '',
            'request_finalization': 0,
            'auth_token': 'UQZSgWwE2f9oIKrj1QG^kVhW^T_cR4H5Z65bPtMhwlHytS5jFrFYyH^dGzjTusDjVTgoBNeR7bvIzctHF7DrLJ1ANevgDOWEWRvABNj6d_k0koqxw9Io',
            'indexed_realtime': 0,
            'ppc_bs': '$SPLUNK_HOME/etc',
            'drop_count': 0,
            'datamodel_map': '',
            'search_can_be_event_type': 0,
            'search_StartUp_Spent': 0,
            'realtime': 0,
            'splunkd_uri': 'https://127.0.0.1:8089',
            'columnOrder': '',
            'kv_store_settings': 'hosts;127.0.0.1:8191\\;;local;127.0.0.1:8191;read_preference;958513E3-8716-4ABF-9559-DA0C9678437F;replica_set_name;958513E3-8716-4ABF-9559-DA0C9678437F;status;ready;',
            'label': '',
            'summary_maxtimespan': '',
            'indexed_realtime_offset': 0,
            'sid': 1433261392.159,
            'msg': [],
            'internal_only': 0,
            'summary_id': '',
            'orig_search_head': '',
            'ppc_app': 'chunked_searchcommands',
            'countMap': {
                'invocations.dispatch.writeStatus': '1',
                'duration.dispatch.writeStatus': '2',
                'duration.startup.handoff': '79',
                'duration.startup.configuration': '34',
                'invocations.startup.handoff': '1',
                'invocations.startup.configuration': '1'},
            'is_shc_mode': 0,
            'shp_id': '958513E3-8716-4ABF-9559-DA0C9678437F',
            'timestamp': 1433261392.936374, 'is_remote_sorted': 0,
            'remote_search': '',
            'splunkd_protocol': 'https',
            'site': '',
            'maxevents': 0,
            'keySet': '',
            'summary_stopped': 0,
            'search_metrics': {
                'ConsideredEvents': 0,
                'ConsideredBuckets': 0,
                'TotalSlicesInBuckets': 0,
                'EliminatedBuckets': 0,
                'DecompressedSlices': 0},
            'summary_mode': 'all', 'now': 1433261392.0,
            'splunkd_port': 8089, 'is_saved_search': 0,
            'rtoptions': '',
            'search': '| inputlookup random_data max=50000 | sum total=total value1 record=t | export add_timestamp=f add_offset=t format=csv segmentation=raw',
            'bundle_version': 0,
            'generation_id': 0,
            'bs_thread_id': 0,
            'is_batch_mode': 0,
            'scan_count': 0,
            'rt_earliest': '',
            'default_group': '*',
            'tstats_reduce': '',
            'kv_store_additional_settings': 'hosts_guids;958513E3-8716-4ABF-9559-DA0C9678437F\\;;',
            'enable_event_stream': 0,
            'is_remote': 0,
            'is_scheduled': 0,
            'sample_ratio': 1,
            'ppc_user': 'admin',
            'sample_seed': 0})

        self.assertIsInstance(command.service, Service)

        self.assertEqual(command.service.authority, command_metadata.searchinfo.splunkd_uri)
        self.assertEqual(command.service.scheme, command.search_results_info.splunkd_protocol)
        self.assertEqual(command.service.port, command.search_results_info.splunkd_port)
        self.assertEqual(command.service.token, command_metadata.searchinfo.session_key)
        self.assertEqual(command.service.namespace.app, command.metadata.searchinfo.app)
        self.assertIsNone(command.service.namespace.owner)
        self.assertIsNone(command.service.namespace.sharing)

        self.assertEqual(command.protocol_version, 2)

        # 3. Produce an error message, log a debug message, and exit when invalid standard option values are encountered

        # Note on loggers
        # Loggers are global and can't be removed once they're created. We create loggers that are keyed by class name
        # Each instance of a class thus created gets access to the same logger. We created one in the prior test and
        # set it's level to ERROR. That level is retained in this test.

        logging_configuration = 'non-existent-logging.conf'
        logging_level = 'NON-EXISTENT-LOGGING-LEVEL'
        record = 'Non-boolean value'
        show_configuration = 'Non-boolean value'

        getinfo_metadata = metadata.format(
            dispatch_dir=encode_string(dispatch_dir),
            logging_configuration=encode_string(logging_configuration)[1:-1],
            logging_level=logging_level,
            record=record,
            show_configuration=show_configuration)

        execute_metadata = '{"action":"execute","finished":true}'
        execute_body = 'test\r\ndata\r\n测试\r\n'

        ifile = build_command_input(getinfo_metadata, execute_metadata, execute_body)

        command = TestCommand()
        result = BytesIO()
        argv = ['test.py']

        # noinspection PyTypeChecker
        self.assertRaises(SystemExit, command.process, argv, ifile, ofile=result)
        self.assertEqual(command.logging_level, 'ERROR')
        self.assertEqual(command.record, False)
        self.assertEqual(command.show_configuration, False)
        self.assertEqual(command.required_option_1, 'value_1')
        self.assertEqual(command.required_option_2, 'value_2')

        self.assertEqual(
            'chunked 1.0,287,0\n'
            '{"inspector":{"messages":[["ERROR","Illegal value: logging_configuration=non-existent-logging.conf"],'
            '["ERROR","Illegal value: logging_level=NON-EXISTENT-LOGGING-LEVEL"],'
            '["ERROR","Illegal value: record=Non-boolean value"],'
            '["ERROR","Illegal value: show_configuration=Non-boolean value"]]}}\n',
            result.getvalue().decode('utf-8'))

        self.assertEqual(command.protocol_version, 2)

        # 4. Produce an error message, log an error message that includes a traceback, and exit when an exception is
        #    raised during command execution.

        logging_configuration = os.path.join(basedir, 'apps', 'app_with_logging_configuration', 'logging.conf')
        logging_level = 'WARNING'
        record = False
        show_configuration = False

        getinfo_metadata = metadata.format(
            dispatch_dir=encode_string(dispatch_dir),
            logging_configuration=encode_string(logging_configuration)[1:-1],
            logging_level=logging_level,
            record=('true' if record is True else 'false'),
            show_configuration=('true' if show_configuration is True else 'false'))

        execute_metadata = '{"action":"execute","finished":true}'
        execute_body = 'action\r\nraise_exception\r\n测试\r\n'

        ifile = build_command_input(getinfo_metadata, execute_metadata, execute_body)

        command = TestCommand()
        result = BytesIO()
        argv = ['test.py']

        try:
            command.process(argv, ifile, ofile=result)
        except SystemExit as error:
            self.assertNotEqual(0, error.code)
        except BaseException as error:
            self.fail('{0}: {1}: {2}\n'.format(type(error).__name__, error, result.getvalue().decode('utf-8')))
        else:
            self.fail('Expected SystemExit, not a return from TestCommand.process: {}\n'.format(
                result.getvalue().decode('utf-8')))

        self.assertEqual(command.logging_configuration, logging_configuration)
        self.assertEqual(command.logging_level, logging_level)
        self.assertEqual(command.record, record)
        self.assertEqual(command.show_configuration, show_configuration)
        self.assertEqual(command.required_option_1, 'value_1')
        self.assertEqual(command.required_option_2, 'value_2')

        finished = r'\"finished\":true'

        inspector = \
            r'\"inspector\":\{\"messages\":\[\[\"ERROR\",\"Exception at \\\".+\\\", line \d+ : test ' \
            r'logging_configuration=\\\".+\\\" logging_level=\\\"WARNING\\\" record=\\\"f\\\" ' \
            r'required_option_1=\\\"value_1\\\" required_option_2=\\\"value_2\\\" show_configuration=\\\"f\\\"\"\]\]\}'

        six.assertRegex(
            self,
            result.getvalue().decode('utf-8'),
            r'^chunked 1.0,2,0\n'
            r'\{\}\n'
            r'chunked 1.0,\d+,0\n'
            r'\{(' + inspector + r',' + finished + r'|' + finished + r',' + inspector + r')\}')

        self.assertEqual(command.protocol_version, 2)

        # 5. Different scenarios with allow_empty_input flag, default is True
        # Test preparation
        dispatch_dir = os.path.join(basedir, 'recordings', 'scpv2', 'Splunk-6.3', 'countmatches.dispatch_dir')
        logging_configuration = os.path.join(basedir, 'apps', 'app_with_logging_configuration', 'logging.conf')
        logging_level = 'ERROR'
        record = False
        show_configuration = True

        getinfo_metadata = metadata.format(
            dispatch_dir=encode_string(dispatch_dir),
            logging_configuration=encode_string(logging_configuration)[1:-1],
            logging_level=logging_level,
            record=('true' if record is True else 'false'),
            show_configuration=('true' if show_configuration is True else 'false'))

        execute_metadata = '{"action":"execute","finished":true}'
        command = TestCommand()
        result = BytesIO()
        argv = ['some-external-search-command.py']

        # Scenario a) Empty body & allow_empty_input=False ==> Assert Error

        execute_body = ''  # Empty body
        input_file = build_command_input(getinfo_metadata, execute_metadata, execute_body)
        try:
            command.process(argv, input_file, ofile=result, allow_empty_input=False)  # allow_empty_input=False
        except SystemExit as error:
            self.assertNotEqual(0, error.code)
            self.assertTrue(result.getvalue().decode("UTF-8").__contains__("No records found to process. Set "
                                                                           "allow_empty_input=True in dispatch "
                                                                           "function to move forward with empty "
                                                                           "records."))
        else:
            self.fail('Expected SystemExit, not a return from TestCommand.process: {}\n'.format(
                result.getvalue().decode('utf-8')))

        # Scenario b) Empty body & allow_empty_input=True ==> Assert Success

        execute_body = ''  # Empty body
        input_file = build_command_input(getinfo_metadata, execute_metadata, execute_body)
        result = BytesIO()

        try:
            command.process(argv, input_file, ofile=result)  # By default allow_empty_input=True
        except SystemExit as error:
            self.fail('Unexpected exception: {}: {}'.format(type(error).__name__, error))

        expected = (
            'chunked 1.0,68,0\n'
            '{"inspector":{"messages":[["INFO","test command configuration: "]]}}\n'
            'chunked 1.0,17,0\n'
            '{"finished":true}'
        )

        self.assertEqual(result.getvalue().decode("UTF-8"), expected)

    _package_directory = os.path.dirname(os.path.abspath(__file__))


TestCommand.__test__ = False
TestStreamingCommand.__test__ = False

if __name__ == "__main__":
    main()

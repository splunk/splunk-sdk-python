#!/usr/bin/env python
# coding=utf-8
#
# Copyright © 2011-2024 Splunk, Inc.
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
import logging

from io import TextIOWrapper
from unittest.mock import MagicMock, patch

import pytest

import splunklib
from splunklib.searchcommands import Configuration, StreamingCommand
from splunklib.searchcommands.decorators import ConfigurationSetting, Option
from splunklib.searchcommands.internals import ObjectView
from splunklib.searchcommands.search_command import SearchCommand
from splunklib.client import Service
from splunklib.utils import ensure_binary

from io import StringIO, BytesIO


def build_command_input(getinfo_metadata, execute_metadata, execute_body):
    input = (
        f"chunked 1.0,{len(ensure_binary(getinfo_metadata))},0\n{getinfo_metadata}"
        + f"chunked 1.0,{len(ensure_binary(execute_metadata))},{len(ensure_binary(execute_body))}\n{execute_metadata}{execute_body}"
    )

    ifile = BytesIO(ensure_binary(input))

    ifile = TextIOWrapper(ifile)

    return ifile


@Configuration()
class TestCommand(SearchCommand):
    __test__ = False

    required_option_1 = Option(require=True)
    required_option_2 = Option(require=True)

    def echo(self, records):
        for record in records:
            if record.get("action") == "raise_exception":
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
    __test__ = False

    def stream(self, records):
        serial_number = 0
        for record in records:
            action = record["action"]
            if action == "raise_error":
                raise RuntimeError("Testing")
            value = (
                self.search_results_info
                if action == "get_search_results_info"
                else None
            )
            yield {"_serial": serial_number, "data": value}
            serial_number += 1


@pytest.mark.smoke
class TestSearchCommand(TestCase):
    def setUp(self):
        TestCase.setUp(self)

    def test_process_scpv2(self):
        # SearchCommand.process should

        # 1. Recognize all standard options:

        metadata = (
            "{{"
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
            "],"
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
            "],"
            '"maxresultrows": 10,'
            '"command": "countmatches"'
            "}}"
            "}}"
        )

        basedir = self._package_directory

        logging_configuration = os.path.join(
            basedir, "apps", "app_with_logging_configuration", "logging.conf"
        )
        logging_level = "ERROR"
        record = False
        show_configuration = True

        getinfo_metadata = metadata.format(
            dispatch_dir=encode_string(""),
            logging_configuration=encode_string(logging_configuration)[1:-1],
            logging_level=logging_level,
            record=("true" if record is True else "false"),
            show_configuration=("true" if show_configuration is True else "false"),
        )

        execute_metadata = '{"action":"execute","finished":true}'
        execute_body = "test\r\ndata\r\n测试\r\n"

        ifile = build_command_input(getinfo_metadata, execute_metadata, execute_body)

        command = TestCommand()
        result = BytesIO()
        argv = ["some-external-search-command.py"]

        self.assertEqual(command.logging_level, "WARNING")
        self.assertIs(command.record, None)
        self.assertIs(command.show_configuration, None)

        try:
            # noinspection PyTypeChecker
            command.process(argv, ifile, ofile=result)
        except SystemExit as error:
            self.fail(
                "Unexpected exception: {}: {}".format(type(error).__name__, error)
            )

        self.assertEqual(command.logging_configuration, logging_configuration)
        self.assertEqual(command.logging_level, "ERROR")
        self.assertEqual(command.record, record)
        self.assertEqual(command.show_configuration, show_configuration)
        self.assertEqual(command.required_option_1, "value_1")
        self.assertEqual(command.required_option_2, "value_2")

        expected = (
            "chunked 1.0,68,0\n"
            '{"inspector":{"messages":[["INFO","test command configuration: "]]}}'
            "chunked 1.0,17,32\n"
            '{"finished":true}test,__mv_test\r\n'
            "data,\r\n"
            "测试,\r\n"
        )

        self.assertEqual(expected, result.getvalue().decode("utf-8"))

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

        self.assertIsNone(input_header["allowStream"])
        self.assertEqual(
            input_header["infoPath"],
            os.path.join(command_metadata.searchinfo.dispatch_dir, "info.csv"),
        )
        self.assertIsNone(input_header["keywords"])
        self.assertEqual(input_header["preview"], command_metadata.preview)
        self.assertIs(input_header["realtime"], False)
        self.assertEqual(input_header["search"], command_metadata.searchinfo.search)
        self.assertEqual(input_header["sid"], command_metadata.searchinfo.sid)
        self.assertEqual(
            input_header["splunkVersion"], command_metadata.searchinfo.splunk_version
        )
        self.assertIsNone(input_header["truncated"])

        self.assertEqual(command_metadata.preview, input_header["preview"])
        self.assertEqual(command_metadata.searchinfo.app, "searchcommands_app")
        self.assertEqual(
            command_metadata.searchinfo.args,
            [
                "logging_configuration=" + logging_configuration,
                "logging_level=ERROR",
                "record=false",
                "show_configuration=true",
                "required_option_1=value_1",
                "required_option_2=value_2",
            ],
        )
        self.assertEqual(
            command_metadata.searchinfo.dispatch_dir,
            os.path.dirname(input_header["infoPath"]),
        )
        self.assertEqual(command_metadata.searchinfo.earliest_time, 0.0)
        self.assertEqual(command_metadata.searchinfo.latest_time, 0.0)
        self.assertEqual(command_metadata.searchinfo.owner, "admin")
        self.assertEqual(
            command_metadata.searchinfo.raw_args, command_metadata.searchinfo.args
        )
        self.assertEqual(
            command_metadata.searchinfo.search,
            'Ａ| inputlookup tweets | countmatches fieldname=word_count pattern="\\w+" text record=t | export add_timestamp=f add_offset=t format=csv segmentation=raw',
        )
        self.assertEqual(
            command_metadata.searchinfo.session_key,
            "0JbG1fJEvXrL6iYZw9y7tmvd6nHjTKj7ggaE7a4Jv5R0UIbeYJ65kThn^3hiNeoqzMT_LOtLpVR3Y8TIJyr5bkHUElMijYZ8l14wU0L4n^Oa5QxepsZNUIIQCBm^",
        )
        self.assertEqual(command_metadata.searchinfo.sid, "1433261372.158")
        self.assertEqual(command_metadata.searchinfo.splunk_version, "20150522")
        self.assertEqual(
            command_metadata.searchinfo.splunkd_uri, "https://127.0.0.1:8089"
        )
        self.assertEqual(command_metadata.searchinfo.username, "admin")
        self.assertEqual(command_metadata.searchinfo.maxresultrows, 10)
        self.assertEqual(command_metadata.searchinfo.command, "countmatches")

        self.maxDiff = None

        self.assertIsInstance(command.service, Service)

        self.assertEqual(
            command.service.authority, command_metadata.searchinfo.splunkd_uri
        )
        self.assertEqual(command.service.token, command_metadata.searchinfo.session_key)
        self.assertEqual(command.service.namespace.app, command.metadata.searchinfo.app)
        self.assertIsNone(command.service.namespace.owner)
        self.assertIsNone(command.service.namespace.sharing)

        self.assertEqual(command.protocol_version, 2)

    _package_directory = os.path.dirname(os.path.abspath(__file__))


class TestSearchCommandService(TestCase):
    def setUp(self):
        TestCase.setUp(self)
        self.command = SearchCommand()
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        self.command.logger.addHandler(console_handler)

    def test_service_exists(self):
        self.command._service = Service()
        self.assertIsNotNone(self.command.service)

    def test_service_not_exists(self):
        self.assertIsNone(self.command.service)

    def test_missing_metadata(self):
        with self.assertLogs(self.command.logger, level="WARNING") as log:
            service = self.command.service
            self.assertIsNone(service)
        self.assertTrue(
            any(
                "Missing metadata for service creation." in message
                for message in log.output
            )
        )

    def test_missing_searchinfo(self):
        with self.assertLogs(self.command.logger, level="WARNING") as log:
            self.command._metadata = ObjectView({})
            self.assertIsNone(self.command.service)
        self.assertTrue(
            any(
                "Missing searchinfo in metadata for service creation." in message
                for message in log.output
            )
        )

    def test_missing_splunkd_uri(self):
        with self.assertLogs(self.command.logger, level="WARNING") as log:
            metadata = ObjectView({"searchinfo": ObjectView({"splunkd_uri": ""})})
            self.command._metadata = metadata
            self.assertIsNone(self.command.service)
        self.assertTrue(
            any(
                "Incorrect value for Splunkd URI: '' in metadata" in message
                for message in log.output
            )
        )

    def test_service_returns_valid_service_object(self):
        metadata = ObjectView(
            {
                "searchinfo": ObjectView(
                    {
                        "splunkd_uri": "https://127.0.0.1:8089",
                        "session_key": "mock_session_key",
                        "app": "search",
                    }
                )
            }
        )
        self.command._metadata = metadata
        self.assertIsInstance(self.command.service, Service)


if __name__ == "__main__":
    main()

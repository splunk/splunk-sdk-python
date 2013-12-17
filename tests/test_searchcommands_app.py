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

from subprocess import Popen
import base64
import os
import shutil
import testlib

from splunklib.searchcommands import \
    StreamingCommand, Configuration, Option, validators

@Configuration()
class StubbedCommand(StreamingCommand):
    fieldname = Option(
        doc='''
        **Syntax:** **fieldname=***<fieldname>*
        **Description:** Name of the field that will hold the match count''',
        require=True, validate=validators.Fieldname())

    pattern = Option(
        doc='''
        **Syntax:** **pattern=***<regular-expression>*
        **Description:** Regular expression pattern to match''',
        require=True, validate=validators.RegularExpression())

    def stream(self, records):
        pass


class TestSearchCommandsApp(testlib.SDKTestCase):

    def setUp(self):
        super(TestSearchCommandsApp, self).setUp()
        for directory in 'log', 'output':
            path = TestSearchCommandsApp._data_file(directory)
            if os.path.exists(path):
                shutil.rmtree(path)
            os.mkdir(path)
        return

    def test_command_parser(self):
        from splunklib.searchcommands.search_command_internals import \
            SearchCommandParser

        parser = SearchCommandParser()
        command = StubbedCommand()

        parser.parse(
            [
                'fieldname=word_count',
                'pattern="\\\\w+"',
                'text_field_1',
                'text_field_2'
            ],
            command)

        command_line = str(command)
        self.assertEqual('stubbed fieldname="word_count" pattern="\\\\w+" text_field_1 text_field_2', command_line)
        return

    def test_option_show_configuration(self):
        self._run(
            'simulate', [
                'csv=%s' % TestSearchCommandsApp._data_file("input/population.csv"),
                'duration=00:00:10',
                'interval=00:00:01',
                'rate=200',
                'seed=%s' % TestSearchCommandsApp._seed,
                'show_configuration=true'],
            __GETINFO__=(
                'input/population.csv',
                'output/samples.csv',
                'log/test_show_configuration.log'))
        return

    def test_generating_command_in_isolation(self):
        self._run(
            'simulate', [
                'csv=%s' % TestSearchCommandsApp._data_file("input/population.csv"),
                'duration=00:00:10',
                'interval=00:00:01',
                'rate=200',
                'seed=%s' % TestSearchCommandsApp._seed],
            __GETINFO__=(
                'input/population.csv',
                'output/samples.csv',
                'log/test_generating_command_in_isolation.log'),
            __EXECUTE__=(
                'input/population.csv',
                'output/samples.csv',
                'log/test_generating_command_in_isolation.log'))
        return

    def test_generating_command_on_server(self):
        pass

    def test_reporting_command_in_isolation(self):
        self._run(
            'sum', [
                '__map__', 'total=total', 'count'],
            __GETINFO__=(
                'input/counts.csv',
                'output/subtotals.csv',
                'log/test_reporting_command_in_isolation.log'),
            __EXECUTE__=(
                'input/counts.csv',
                'output/subtotals.csv',
                'log/test_reporting_command_in_isolation.log'))
        self._run(
            'sum', [
                'total=total', 'count'],
            __GETINFO__=(
                'input/subtotals.csv',
                'output/totals.csv',
                'log/test_reporting_command_in_isolation.log'),
            __EXECUTE__=(
                'input/subtotals.csv',
                'output/totals.csv',
                'log/test_reporting_command_in_isolation.log'))
        return

    def test_reporting_command_on_server(self):
        pass

    def test_streaming_command_in_isolation(self):
        self._run(
            'countmatches', [
                'fieldname=word_count',
                'pattern=\\w+',
                'text'],
            __GETINFO__=(
                'input/tweets.csv',
                'output/tweets_with_word_count.csv',
                'log/test_streaming_command.log'),
            __EXECUTE__=(
                'input/tweets.csv',
                'output/tweets_with_word_count.csv',
                'log/test_generating_command_in_isolation.log'))
        return

    def test_streaming_command_on_server(self):
        pass

    def _run(self, command, args, **kwargs):
        for operation in ['__GETINFO__', '__EXECUTE__']:
            if operation not in kwargs:
                continue
            files = kwargs[operation]
            process = TestSearchCommandsApp._start_process(
                ['python', command + '.py', operation] + args,
                TestSearchCommandsApp._open_data_file(files[0], 'r'),
                TestSearchCommandsApp._open_data_file(files[1], 'w'),
                TestSearchCommandsApp._open_data_file(files[2], 'a'))
            process.communicate()
            status = process.wait()
            self.assertEqual(status, 0, "%s status: %d" % (operation, status))
        return

    @classmethod
    def _data_file(cls, relative_path):
        return os.path.join(cls.data_directory, relative_path)

    @classmethod
    def _open_data_file(cls, relative_path, mode):
        return open(cls._data_file(relative_path), mode)

    @classmethod
    def _start_process(cls, args, stdin, stdout, stderr):
        return Popen(args, stdin=stdin, stdout=stdout, stderr=stderr, cwd=cls.app_bin)

    package_directory = os.path.dirname(__file__)
    data_directory = os.path.join(package_directory, 'searchcommands_data')
    app_bin = os.path.join(
        os.path.dirname(package_directory), "examples/searchcommands_app/bin")

    _seed = base64.encodestring(
        '\xcd{\xf8\xc4\x1c8=\x88\nc\xe2\xc4\xee\xdb\xcal')

if __name__ == "__main__":
    unittest.main()

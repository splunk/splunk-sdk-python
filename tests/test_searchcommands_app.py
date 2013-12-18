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
import os
import shutil
import testlib

from splunklib.searchcommands import \
    StreamingCommand, Configuration, Option, validators


@Configuration()
class StubbedCommand(StreamingCommand):
    boolean = Option(
        doc='''
        **Syntax:** **boolean=***<value>*
        **Description:** A boolean value''',
        require=False, validate=validators.Boolean())

    duration = Option(
        doc='''
        **Syntax:** **duration=***<value>*
        **Description:** A length of time''',
        require=False, validate=validators.Duration())

    fieldname = Option(
        doc='''
        **Syntax:** **fieldname=***<value>*
        **Description:** Name of a field''',
        require=True, validate=validators.Fieldname())

    file = Option(
        doc='''
        **Syntax:** **file=***<value>*
        **Description:** Name of a file''',
        validate=validators.File(mode='r'))

    integer = Option(
        doc='''
        **Syntax:** **integer=***<value>*
        **Description:** An integer value''',
        validate=validators.Integer())

    optionname = Option(
        doc='''
        **Syntax:** **optionname=***<value>*
        **Description:** The name of an option (used internally)''',
        validate=validators.OptionName())

    regularexpression = Option(
        doc='''
        **Syntax:** **regularexpression=***<value>*
        **Description:** Regular expression pattern to match''',
        validate=validators.RegularExpression())

    set = Option(
        doc='''
        **Syntax:** **set=***<value>*
        **Description:** Regular expression pattern to match''',
        validate=validators.Set("foo", "bar", "test"))

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
        file_path = TestSearchCommandsApp._data_file('input/counts.csv')
        parser.parse(
            [
                'boolean=true',
                'duration=00:00:10',
                'fieldname=word_count',
                'file=%s' % file_path,
                'integer=10',
                'optionname=foo_bar',
                'regularexpression="\\\\w+"',
                'set=foo',
                'field_1',
                'field_2',
                'field_3'
            ],
            command)
        command_line = str(command)
        self.assertEqual(
            'stubbed boolean=true duration=10 fieldname="word_count" file="%s" integer=10 optionname="foo_bar" regularexpression="\\\\w+" set="foo" field_1 field_2 field_3' % file_path,
            command_line)
        return

    def test_option_show_configuration(self):
        self._run(
            'simulate', [
                'csv=%s' % TestSearchCommandsApp._data_file(
                    "input/population.csv"),
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
                'csv=%s' % TestSearchCommandsApp._data_file(
                    "input/population.csv"),
                'duration=00:00:02',
                'interval=00:00:01',
                'rate=200',
                'seed=%s' % TestSearchCommandsApp._seed],
            __GETINFO__=(
                'input/population.csv',
                'output/test_generating_command_in_isolation.csv',
                'log/test_generating_command_in_isolation.log'),
            __EXECUTE__=(
                'input/population.csv',
                'output/test_generating_command_in_isolation.csv',
                'log/test_generating_command_in_isolation.log'))
        self._check_output_file('test_generating_command_in_isolation.csv')
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
        self._check_output_file('test_reporting_command_in_isolation.csv')
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
                'output/test_streaming_command_in_isolation.csv',
                'log/test_streaming_command.log'),
            __EXECUTE__=(
                'input/tweets.csv',
                'output/test_streaming_command_in_isolation.csv',
                'log/test_generating_command_in_isolation.log'))
        self._check_output_file('test_streaming_command_in_isolation.csv')
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
            self.assertEqual(status, 0, '%s status: %d' % (operation, status))
        return

    def _check_output_file(self, name):
        expected = os.path.join('_expected_results', name)
        actual = os.path.join('output', name)
        with \
            TestSearchCommandsApp._open_data_file(expected, 'r') as expected, \
            TestSearchCommandsApp._open_data_file(actual, 'r') as actual:
            expected = ''.join(expected.readlines())
            actual = ''.join(actual.readlines())
            self.assertMultiLineEqual(expected, actual)
        return

    @classmethod
    def _data_file(cls, relative_path):
        return os.path.join(cls.data_directory, relative_path)

    @classmethod
    def _open_data_file(cls, relative_path, mode):
        return open(cls._data_file(relative_path), mode)

    @classmethod
    def _start_process(cls, args, stdin, stdout, stderr):
        return Popen(args, stdin=stdin, stdout=stdout, stderr=stderr,
                     cwd=cls.app_bin)

    package_directory = os.path.dirname(__file__)
    data_directory = os.path.join(package_directory, 'searchcommands_data')
    app_bin = os.path.join(
        os.path.dirname(package_directory), "examples/searchcommands_app/bin")

    _seed = '5708bef4-6782-11e3-97ed-10ddb1b57bc3'


if __name__ == "__main__":
    unittest.main()

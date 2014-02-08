#!/usr/bin/env python
#
# Copyright 2011-2014 Splunk, Inc.
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

from json import JSONEncoder
from subprocess import Popen
import os
import shutil
from tests import testlib

from splunklib.results import \
    Message, ResultsReader

from splunklib.searchcommands import \
    GeneratingCommand, ReportingCommand, StreamingCommand, Configuration, Option, validators


@Configuration()
class StubbedGeneratingCommand(GeneratingCommand):
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

    def generate(self):
        pass


@Configuration()
class StubbedReportingCommand(ReportingCommand):
    boolean = Option(
        doc='''
        **Syntax:** **boolean=***<value>*
        **Description:** A boolean value''',
        require=False, validate=validators.Boolean())

    duration = Option(
        doc='''
        **Syntax:** **duration=***<value>*
        **Description:** A length of time''',
        validate=validators.Duration())

    fieldname = Option(
        doc='''
        **Syntax:** **fieldname=***<value>*
        **Description:** Name of a field''',
        validate=validators.Fieldname())

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

    @Configuration()
    def map(self, records):
        pass

    def reduce(self, records):
        pass


@Configuration()
class StubbedStreamingCommand(StreamingCommand):
    boolean = Option(
        doc='''
        **Syntax:** **boolean=***<value>*
        **Description:** A boolean value''',
        require=True, validate=validators.Boolean())

    duration = Option(
        doc='''
        **Syntax:** **duration=***<value>*
        **Description:** A length of time''',
        require=True, validate=validators.Duration())

    fieldname = Option(
        doc='''
        **Syntax:** **fieldname=***<value>*
        **Description:** Name of a field''',
        require=True, validate=validators.Fieldname())

    file = Option(
        doc='''
        **Syntax:** **file=***<value>*
        **Description:** Name of a file''',
        require=True, validate=validators.File(mode='r'))

    integer = Option(
        doc='''
        **Syntax:** **integer=***<value>*
        **Description:** An integer value''',
        require=True, validate=validators.Integer())

    optionname = Option(
        doc='''
        **Syntax:** **optionname=***<value>*
        **Description:** The name of an option (used internally)''',
        require=True, validate=validators.OptionName())

    regularexpression = Option(
        doc='''
        **Syntax:** **regularexpression=***<value>*
        **Description:** Regular expression pattern to match''',
        require=True, validate=validators.RegularExpression())

    set = Option(
        doc='''
        **Syntax:** **set=***<value>*
        **Description:** Regular expression pattern to match''',
        require=True, validate=validators.Set("foo", "bar", "test"))

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
        self.maxDiff = 2 * 65535
        return

    def disable_test_option_logging_configuration(self):
        self._run(
            'simulate', [
                'csv=population.csv',
                'duration=00:00:10',
                'interval=00:00:01',
                'rate=200',
                'seed=%s' % TestSearchCommandsApp._seed,
                'logging_configuration=logging.conf'],
            __GETINFO__=(
                os.path.join('input', '_empty.csv'),
                os.path.join('output', 'test_option_logging_configuration.csv'),
                os.path.join('log', 'test_option_logging_configuration.log')))
        return

    def disable_test_option_logging_level(self):
        self._run(
            'simulate', [
                'csv=population.csv',
                'duration=00:00:10',
                'interval=00:00:01',
                'rate=200',
                'seed=%s' % TestSearchCommandsApp._seed,
                'logging_level=ERROR'],
            __GETINFO__=(
                os.path.join('input', 'population.csv'),
                os.path.join('output', 'test_option_logging_level.csv'),
                os.path.join('log', 'test_option_logging_level.log')))
        return

    def test_option_show_configuration(self):
        self._run(
            'simulate', [
                'csv=population.csv',
                'duration=00:00:10',
                'interval=00:00:01',
                'rate=200',
                'seed=%s' % TestSearchCommandsApp._seed,
                'show_configuration=true'],
            __EXECUTE__=(
                os.path.join('input', '_empty.csv'),
                os.path.join('output', 'test_option_show_configuration.csv'),
                os.path.join('log', 'test_option_show_configuration.log')))
        return

    # TODO, use a generating command that doesn't do random sampling because
    # a seed is no guarantee that the same sample is produced on every platform
    # and all versions of python

    def test_generating_command_configuration(self):
        self._assertCorrectConfiguration(
            StubbedGeneratingCommand(), 'test_generating_command_configuration')

    def test_generating_command_in_isolation(self):
        self._run(
            'simulate', [
                'csv=population.csv',
                'duration=00:00:02',
                'interval=00:00:01',
                'rate=50',
                'seed=%s' % TestSearchCommandsApp._seed],
            __GETINFO__=(
                os.path.join('input', '_empty.csv'),
                os.path.join('output', 'test_generating_command_in_isolation.getinfo.csv'),
                os.path.join('log', 'test_generating_command_in_isolation.log')),
            __EXECUTE__=(
                os.path.join('input', '_empty.csv'),
                os.path.join('output', 'test_generating_command_in_isolation.execute.csv'),
                os.path.join('log', 'test_generating_command_in_isolation.log')))
        self._assertCorrectOutputFile('test_generating_command_in_isolation.getinfo.csv')
        # self._assertCorrectOutputFile('test_generating_command_in_isolation.execute.csv')
        return

    def test_generating_command_on_server(self):
        expected, actual = self._getOneshotResults(
            '| simulate csv=population.csv rate=200 interval=00:00:01 duration=00:00:02 seed=%s' % TestSearchCommandsApp._seed,
            'test_generating_command_on_server')
        # self.assertMultilLineEqual(expected, actual)
        return

    def test_reporting_command_configuration(self):
        self._assertCorrectConfiguration(
            StubbedReportingCommand(), 'test_reporting_command_configuration')
        return

    def test_reporting_command_in_isolation(self):
        self._run(
            'sum', [
                '__map__', 'total=subtotal', 'count'],
            __GETINFO__=(
                os.path.join('input', 'counts.csv'),
                os.path.join('output', 'test_reporting_command_in_isolation.map.getinfo.csv'),
                os.path.join('log', 'test_reporting_command_in_isolation.log')),
            __EXECUTE__=(
                os.path.join('input', 'counts.csv'),
                os.path.join('output', 'test_reporting_command_in_isolation.map.execute.csv'),
                os.path.join('log', 'test_reporting_command_in_isolation.log')))
        self._assertCorrectOutputFile('test_reporting_command_in_isolation.map.getinfo.csv')
        self._assertCorrectOutputFile('test_reporting_command_in_isolation.map.execute.csv')
        self._run(
            'sum', [
                'total=total', 'count'],
            __GETINFO__=(
                os.path.join('input', 'subtotals.csv'),
                os.path.join('output', 'test_reporting_command_in_isolation.reduce.getinfo.csv'),
                os.path.join('log', 'test_reporting_command_in_isolation.log')),
            __EXECUTE__=(
                os.path.join('input', 'subtotals.csv'),
                os.path.join('output', 'test_reporting_command_in_isolation.reduce.execute.csv'),
                os.path.join('log', 'test_reporting_command_in_isolation.log')))
        self._assertCorrectOutputFile('test_reporting_command_in_isolation.reduce.getinfo.csv')
        self._assertCorrectOutputFile('test_reporting_command_in_isolation.reduce.execute.csv')
        return

    def test_reporting_command_on_server(self):
        expected, actual = self._getOneshotResults(
            '| inputcsv tweets_with_word_counts.csv | sum total=total word_count',
            'test_reporting_command_on_server')
        self.assertMultiLineEqual(expected, actual)
        return

    def test_streaming_command_configuration(self):
        self._assertCorrectConfiguration(
            StubbedStreamingCommand(), 'test_streaming_command_configuration')

    def test_streaming_command_in_isolation(self):
        self._run(
            'countmatches', [
                'fieldname=word_count',
                'pattern=\\w+',
                'text'],
            __GETINFO__=(
                os.path.join('input', 'tweets.csv'),
                os.path.join('output', 'test_streaming_command_in_isolation.getinfo.csv'),
                os.path.join('log', 'test_streaming_command.log')),
            __EXECUTE__=(
                os.path.join('input', 'tweets.csv'),
                os.path.join('output', 'test_streaming_command_in_isolation.execute.csv'),
                os.path.join('log', 'test_generating_command_in_isolation.log')))
        self._assertCorrectOutputFile('test_streaming_command_in_isolation.getinfo.csv')
        self._assertCorrectOutputFile('test_streaming_command_in_isolation.execute.csv')
        return

    def test_streaming_command_on_server(self):
        expected, actual = self._getOneshotResults(
            '| inputcsv tweets.csv | countmatches fieldname=word_count pattern="\\\\w+" text',
            'test_streaming_command_on_server')
        self.assertMultiLineEqual(expected, actual)
        return

    def _assertCorrectConfiguration(self, command, test_name):
        expected_file_location = os.path.join('_expected_results', test_name + '.txt')
        output_file_location = os.path.join('output', test_name + '.csv')
        file_path = JSONEncoder().encode(TestSearchCommandsApp._data_file(os.path.join('input', 'counts.csv')))
        with TestSearchCommandsApp._open_data_file(os.path.join('input', '_empty.csv'), 'r') as input_file:
            with TestSearchCommandsApp._open_data_file(output_file_location, 'w') as output_file:
                command.process(
                    [
                        command.name,
                        '__GETINFO__',
                        'boolean=false',
                        'duration=00:00:10',
                        'fieldname=foo',
                        'file=%s' % file_path,
                        'integer=10',
                        'optionname=foo_bar',
                        'regularexpression="\\\\w+"',
                        'set=foo'
                    ],
                    input_file,
                    output_file)
        actual = str(command.configuration)
        with TestSearchCommandsApp._open_data_file(expected_file_location, 'r') as input_file:
            expected = ''.join(input_file.readlines()).replace("{file}", file_path)
        self.assertMultiLineEqual(expected, actual)

    def _assertCorrectOutputFile(self, name):
        expected = os.path.join('_expected_results', name)
        actual = os.path.join('output', name)
        with TestSearchCommandsApp._open_data_file(expected, 'r') as expected:
            with TestSearchCommandsApp._open_data_file(actual, 'r') as actual:
                for actual_line, expected_line in zip(actual, expected):
                    self.assertTrue(actual_line == expected_line)
        return

    def _getOneshotResults(self, query, test_name):
        response = self.service.jobs.oneshot(query, app="searchcommands_app")
        reader = ResultsReader(response)
        actual = []
        for result in reader:
            if isinstance(result, dict):
                actual += [u'Results: %s' % result]
            elif isinstance(result, Message):
                actual += [u'Message: %s' % result]
        actual = actual + [u'is_preview = %s' % reader.is_preview]
        actual = u'\n'.join(actual)
        with TestSearchCommandsApp._open_data_file('_expected_results/%s.txt' % test_name, 'r') as expected_file:
            expected = u''.join(expected_file.readlines())
        return actual, expected

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

    @classmethod
    def _data_file(cls, relative_path):
        return os.path.join(cls.data_directory, relative_path)

    @classmethod
    def _open_data_file(cls, relative_path, mode):
        import codecs
        return codecs.open(cls._data_file(relative_path), mode, encoding='utf-8')

    @classmethod
    def _start_process(cls, args, stdin, stdout, stderr):
        return Popen(args, stdin=stdin, stdout=stdout, stderr=stderr, cwd=cls.app_bin)

    package_directory = os.path.dirname(__file__)
    data_directory = os.path.join(package_directory, 'data')
    app_bin = os.path.abspath(os.path.join(package_directory, "../../examples/searchcommands_app/bin"))

    _seed = '5708bef4-6782-11e3-97ed-10ddb1b57bc3'


if __name__ == "__main__":
    unittest.main()

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

import imp
from json import JSONEncoder
from subprocess import Popen
import os
import io
import shutil
from tests import testlib

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

try:
    from collections import OrderedDict
except:
    from ordereddict import OrderedDict

from splunklib.results import \
    Message, ResultsReader

from splunklib.searchcommands import \
    GeneratingCommand, ReportingCommand, StreamingCommand, Configuration, Option, validators, dispatch


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


def get_searchcommand_example(filename):
    return os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "examples",
        "searchcommands_app", "bin", filename)


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

    # TODO: DVPL-5869 - use a generating command that doesn't do random sampling because
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
                os.path.join('output',
                             'test_generating_command_in_isolation.getinfo.csv'),
                os.path.join('log',
                             'test_generating_command_in_isolation.log')),
            __EXECUTE__=(
                os.path.join('input', '_empty.csv'),
                os.path.join('output',
                             'test_generating_command_in_isolation.execute.csv'),
                os.path.join('log',
                             'test_generating_command_in_isolation.log')))
        self._assertCorrectOutputFile('test_generating_command_in_isolation.getinfo.csv')
        self._assertCorrectOutputFile('test_generating_command_in_isolation.execute.csv')
        return

    def test_generating_command_as_unit(self):
        simulate_path = get_searchcommand_example("simulate.py")
        self.assertTrue(os.path.isfile(simulate_path))

        # Copy population.csv to the $SPLUNK_HOME/var/run/splunk/ directory
        population_file = os.path.join(os.path.dirname(simulate_path),
                                       "population.csv")
        shutil.copy(population_file, validators.File._var_run_splunk)

        # load the SimulateCommand class from simulate.py
        simulate = imp.load_source('searchcommands_app', simulate_path)

        instream = StringIO()
        outstream = StringIO()
        cli_args = [
            "simulate.py",
            "__GETINFO__",
            "duration=00:00:10",
            "csv=population.csv",
            "rate=1",
            "interval=00:00:01"]
        # Run the process
        dispatch(simulate.SimulateCommand, cli_args, instream, outstream,
                 "__main__")
        expected_info_path = os.path.join(os.path.dirname(__file__), 'data/_expected_results/test_generating_command_in_isolation.getinfo.csv')
        self.assertEqual(io.open(os.path.abspath(expected_info_path), newline='').read(), outstream.getvalue())

        instream = StringIO()
        outstream = StringIO()
        cli_args = [
            "simulate.py",
            "__EXECUTE__",
            "duration=00:00:10",
            "csv=population.csv",
            "rate=1",
            "interval=00:00:01"]
        # Run the process
        dispatch(simulate.SimulateCommand, cli_args, instream, outstream,
                 "__main__")

        rows = outstream.getvalue().split("\r\n")[1:-1]

        found_fields = rows[0].split(",")
        expected_fields = [
            '_time',
            '_serial',
            'text',
            '__mv__time',
            '__mv__serial',
            '__mv_text',
        ]
        self.assertEqual(len(expected_fields), len(found_fields))
        self.assertEqual(expected_fields, found_fields)

        # did we get the field names and at least 2 events?
        self.assertTrue(3 < len(rows))

        return

    def test_helloworld_generating_command_as_unit(self):
        helloworld_path = get_searchcommand_example("generatehello.py")
        self.assertTrue(os.path.isfile(helloworld_path))
        helloworld = imp.load_source('searchcommands_app', helloworld_path)

        instream = StringIO()
        outstream = StringIO()
        cli_args = [
            "generatehello.py",
            "__GETINFO__",
            "count=5",
        ]
        # Run the process
        dispatch(helloworld.GenerateHelloCommand, cli_args, instream, outstream,
                 "__main__")
        expected_info_path = os.path.join(os.path.dirname(__file__), 'data/_expected_results/test_generating_command_in_isolation.getinfo.csv')
        self.assertEqual(io.open(os.path.abspath(expected_info_path), newline='').read(), outstream.getvalue())

        # Overwrite the existing StringIO objects
        instream = StringIO()
        outstream = StringIO()
        cli_args = [
            "generatehello.py",
            "__EXECUTE__",
            "count=5",
        ]
        # Run the process
        dispatch(helloworld.GenerateHelloCommand, cli_args, instream, outstream,
                 "__main__")

        # Trim the blank lines at either end of the list
        rows = outstream.getvalue().split("\r\n")[1:-1]

        found_fields = rows[0].split(",")
        expected_fields = [
            '_time',
            'event_no',
            '_raw',
            '__mv__time',
            '__mv_event_no',
            '__mv__raw',
        ]

        self.assertEqual(len(expected_fields), len(found_fields))
        self.assertEqual(expected_fields, found_fields)

        # Trim the field names
        events = rows[1:]
        self.assertEqual(5, len(events))

        for i in range(1, len(events)):
            event = events[i].split(",")
            self.assertEqual(i + 1, int(event[1]))
            self.assertEqual(i + 1, int(event[2][-1]))
        return

    def test_generating_command_on_server(self):
        # TODO: DVPL-5870 - this test has inconsistent results due to random sampling
        expected, actual = self._getOneshotResults(
            '| simulate csv=population.csv rate=200 interval=00:00:01 duration=00:00:02 seed=%s' % TestSearchCommandsApp._seed,
            'test_generating_command_on_server')
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
                os.path.join('output',
                             'test_reporting_command_in_isolation.map.getinfo.csv'),
                os.path.join('log', 'test_reporting_command_in_isolation.log')),
            __EXECUTE__=(
                os.path.join('input', 'counts.csv'),
                os.path.join('output',
                             'test_reporting_command_in_isolation.map.execute.csv'),
                os.path.join('log', 'test_reporting_command_in_isolation.log')))
        self._assertCorrectOutputFile(
            'test_reporting_command_in_isolation.map.getinfo.csv')
        self._assertCorrectOutputFile(
            'test_reporting_command_in_isolation.map.execute.csv')
        self._run(
            'sum', [
                'total=total', 'count'],
            __GETINFO__=(
                os.path.join('input', 'subtotals.csv'),
                os.path.join('output',
                             'test_reporting_command_in_isolation.reduce.getinfo.csv'),
                os.path.join('log', 'test_reporting_command_in_isolation.log')),
            __EXECUTE__=(
                os.path.join('input', 'subtotals.csv'),
                os.path.join('output',
                             'test_reporting_command_in_isolation.reduce.execute.csv'),
                os.path.join('log', 'test_reporting_command_in_isolation.log')))

        self._assertCorrectOutputFile('test_reporting_command_in_isolation.reduce.getinfo.csv')
        self._assertCorrectOutputFile('test_reporting_command_in_isolation.reduce.execute.csv')
        return

    def test_reporting_command_on_server(self):
        tweets_file = os.path.join(os.path.dirname(__file__), "data", "input", "tweets_with_word_counts.csv")
        shutil.copy(tweets_file, validators.File._var_run_splunk)
        expected, actual = self._getOneshotResults(
            '| inputcsv tweets_with_word_counts.csv | sum total=total word_count',
            'test_reporting_command_on_server')
        self.assertEqual(expected, actual)
        self.assertMultiLineEqual(expected, actual)
        return

    def test_reporting_command_as_unit(self):
        sum_path = get_searchcommand_example("sum.py")
        self.assertTrue(os.path.isfile(sum_path))
        sum_module = imp.load_source('searchcommands_app', sum_path)

        # Map tests

        instream = StringIO(io.open(os.path.join(os.path.dirname(__file__), "data", "input", "counts.csv"), newline='').read())
        outstream = StringIO()
        cli_args = [
            "sum.py",
            "__GETINFO__",
            "__map__",
            "total=subtotal",
            "count"
            ]
        # Run the process
        dispatch(sum_module.SumCommand, cli_args, instream, outstream, "__main__")
        expected_info_path = os.path.join(os.path.dirname(__file__), 'data/_expected_results/test_reporting_command_in_isolation.map.getinfo.csv')
        self.assertEqual(io.open(expected_info_path, newline='').read(), outstream.getvalue())

        # Overwrite the existing StringIO objects
        instream = StringIO(open(os.path.join(os.path.dirname(__file__), "data", "input",
                                     "counts.csv")).read())
        outstream = StringIO()
        cli_args = [
            "sum.py",
            "__EXECUTE__",
            "__map__",
            "total=subtotal",
            "count"
        ]
        # Run the process
        dispatch(sum_module.SumCommand, cli_args, instream, outstream,
                 "__main__")

        expected_exec_path = os.path.join(os.path.dirname(__file__), 'data/_expected_results/test_reporting_command_in_isolation.map.execute.csv')
        self.assertEqual(io.open(expected_exec_path, newline='').read(), outstream.getvalue())

        # Trim the blank lines at either end of the list
        rows = outstream.getvalue().split("\r\n")[1:-1]

        found_fields = rows[0].split(",")
        expected_fields = [
            'subtotal',
            '__mv_subtotal',
        ]

        self.assertEqual(len(expected_fields), len(found_fields))
        self.assertEqual(expected_fields, found_fields)

        self.assertEqual(['6.0', ''], rows[1:][0].split(","))

        # Reduce tests

        instream = StringIO(open(os.path.join(os.path.dirname(__file__), "data", "input", "subtotals.csv")).read())
        outstream = StringIO()
        cli_args = [
            "sum.py",
            "__GETINFO__",
            "total=total",
            "count"
            ]
        # Run the process
        dispatch(sum_module.SumCommand, cli_args, instream, outstream, "__main__")
        expected_info_path = os.path.join(os.path.dirname(__file__), 'data/_expected_results/test_reporting_command_in_isolation.reduce.getinfo.csv')

        self.assertEqual(io.open(expected_info_path, newline='').read(), outstream.getvalue())

        # Overwrite the existing StringIO objects
        instream = StringIO(open(os.path.join(os.path.dirname(__file__), "data", "input",
                                     "subtotals.csv")).read())

        outstream = StringIO()
        cli_args = [
            "sum.py",
            "__EXECUTE__",
            "total=total",
            "count"
        ]
        # Run the process
        dispatch(sum_module.SumCommand, cli_args, instream, outstream,
                 "__main__")
        expected_exec_path = os.path.join(os.path.dirname(__file__), 'data/_expected_results/test_reporting_command_in_isolation.reduce.execute.csv')
        self.assertEqual(io.open(expected_exec_path, newline='').read(), outstream.getvalue())

        # Trim the blank lines at either end of the list
        rows = outstream.getvalue().split("\r\n")[1:-1]

        found_fields = rows[0].split(",")
        expected_fields = [
            'total',
            '__mv_total',
        ]

        self.assertEqual(len(expected_fields), len(found_fields))
        self.assertEqual(expected_fields, found_fields)

        self.assertEqual(['6.0', ''], rows[1:][0].split(","))
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
                os.path.join('output',
                             'test_streaming_command_in_isolation.getinfo.csv'),
                os.path.join('log', 'test_streaming_command.log')),
            __EXECUTE__=(
                os.path.join('input', 'tweets.csv'),
                os.path.join('output',
                             'test_streaming_command_in_isolation.execute.csv'),
                os.path.join('log',
                             'test_generating_command_in_isolation.log')))
        self._assertCorrectOutputFile('test_streaming_command_in_isolation.getinfo.csv')
        self._assertCorrectOutputFile('test_streaming_command_in_isolation.execute.csv')
        return

    def test_streaming_command_on_server(self):
        tweets_file = os.path.join(os.path.dirname(__file__), "data", "input", "tweets.csv")
        shutil.copy(tweets_file, validators.File._var_run_splunk)
        expected, actual = self._getOneshotResults(
            '| inputcsv tweets.csv | countmatches fieldname=word_count pattern="\\\\w+" text',
            'test_streaming_command_on_server')

        self.assertMultiLineEqual(expected, actual)
        return

    def _assertCorrectConfiguration(self, command, test_name):
        expected_file_location = os.path.join('_expected_results',
                                              test_name + '.txt')
        output_file_location = os.path.join('output', test_name + '.csv')
        file_path = JSONEncoder().encode(TestSearchCommandsApp._data_file(
            os.path.join('input', 'counts.csv')))
        with TestSearchCommandsApp._open_data_file(
                os.path.join('input', '_empty.csv'), 'r') as input_file:
            with TestSearchCommandsApp._open_data_file(output_file_location,
                                                       'w') as output_file:
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
        with TestSearchCommandsApp._open_data_file(expected_file_location,
                                                   'r') as input_file:
            expected = ''.join(input_file.readlines()).replace("{file}",
                                                               file_path)
        self.assertMultiLineEqual(expected, actual)

    def _assertCorrectOutputFile(self, name):
        expected = os.path.join('_expected_results', name)
        actual = os.path.join('output', name)
        with TestSearchCommandsApp._open_data_file(expected, 'r') as expected:
            with TestSearchCommandsApp._open_data_file(actual, 'r') as actual:
                for actual_line, expected_line in zip(actual, expected):
                    self.assertEqual(expected_line, actual_line)
        return

    def _getOneshotResults(self, query, test_name):
        response = self.service.jobs.oneshot(query, app="searchcommands_app")
        reader = ResultsReader(response)
        actual = []
        for result in reader:
            if isinstance(result, dict):
                actual += [u'Results: %s' % OrderedDict(sorted(result.iteritems()))]
            elif isinstance(result, Message):
                actual += [u'Message: %s' % result]
        actual += [u'is_preview = %s' % reader.is_preview]
        actual = (os.linesep).join(actual)
        with TestSearchCommandsApp._open_data_file(
                        '_expected_results/%s.txt' % test_name,
                        'r') as expected_file:
            expected = u''.join(expected_file.readlines())
        return expected, actual

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

        return codecs.open(cls._data_file(relative_path), mode,
                           encoding='utf-8')

    @classmethod
    def _start_process(cls, args, stdin, stdout, stderr):
        # TODO: DVPL-5871 - make a shell script to run some of these separately, check results there
        return Popen(args, stdin=stdin, stdout=stdout, stderr=stderr,
                     cwd=cls.app_bin)

    package_directory = os.path.dirname(__file__)
    data_directory = os.path.join(package_directory, 'data')
    app_bin = os.path.abspath(os.path.join(package_directory,
                                           "../../examples/searchcommands_app/bin"))

    _seed = '5708bef4-6782-11e3-97ed-10ddb1b57bc3'


if __name__ == "__main__":
    unittest.main()

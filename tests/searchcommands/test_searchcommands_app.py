#!/usr/bin/env python
# coding=utf-8
#
# Copyright © 2011-2015 Splunk, Inc.
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

# P2 [ ] TODO: Add integration tests that, for example, verify we can use the SearchCommand.service object.
# We verify that the service object is constructed correctly, but we've got no automated tests that verify we can use
# the service object.

# P2 [ ] TODO: Use saved dispatch dir to mock tests that depend on its contents (?)
# To make records more generally useful to application developers we should provide/demonstrate how to mock
# self.metadata, self.search_results_info, and self.service. Such mocks might be based on archived dispatch directories.


from collections import namedtuple
from datetime import datetime

from subprocess import PIPE, Popen

from unittest import main, skipUnless, TestCase

import gzip
import json
import csv
import io
import os
import sys
import pytest

from splunklib.six.moves import cStringIO as StringIO
from splunklib import six

from tests.searchcommands import project_root


def pypy():
    try:
        process = Popen(['pypy', '--version'], stderr=PIPE, stdout=PIPE)
    except OSError:
        return False
    else:
        process.communicate()
        return process.returncode == 0


class Recording:

    def __init__(self, path):

        self._dispatch_dir = path + '.dispatch_dir'
        self._search = None

        if os.path.exists(self._dispatch_dir):
            with io.open(os.path.join(self._dispatch_dir, 'request.csv')) as ifile:
                reader = csv.reader(ifile)
                for name, value in zip(next(reader), next(reader)):
                    if name == 'search':
                        self._search = value
                        break
            assert self._search is not None

        splunk_cmd = path + '.splunk_cmd'

        try:
            with io.open(splunk_cmd, 'r') as f:
                self._args = f.readline().encode().split(None, 5)  # ['splunk', 'cmd', <filename>, <action>, <args>]
        except IOError as error:
            if error.errno != 2:
                raise
            self._args = ['splunk', 'cmd', 'python', None]

        self._input_file = path + '.input.gz'

        self._output_file = path + '.output'

        if six.PY3 and os.path.isfile(self._output_file + '.py3'):
            self._output_file = self._output_file + '.py3'

        # Remove the "splunk cmd" portion
        self._args = self._args[2:]

    def get_args(self, command_path):
        self._args[1] = command_path
        return self._args

    @property
    def dispatch_dir(self):
        return self._dispatch_dir

    @property
    def input_file(self):
        return self._input_file

    @property
    def output_file(self):
        return self._output_file

    @property
    def search(self):
        return self._search


class Recordings:

    def __init__(self, name, action, phase, protocol_version):
        basedir = Recordings._prefix + six.text_type(protocol_version)

        if not os.path.isdir(basedir):
            raise ValueError(
                f'Directory "{protocol_version}" containing recordings for protocol version {basedir} does not exist')

        self._basedir = basedir
        self._name = '.'.join([part for part in (name, action, phase) if part is not None])

    def __iter__(self):
        basedir = self._basedir
        name = self._name

        iterator = [Recording(os.path.join(basedir, directory, name)) for directory in
                    [filename for filename in os.listdir(basedir) if os.path.isdir(os.path.join(basedir, filename))]]

        return iterator

    _prefix = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'recordings', 'scpv')


@pytest.mark.smoke
class TestSearchCommandsApp(TestCase):
    app_root = os.path.join(project_root, 'examples', 'searchcommands_app', 'build', 'searchcommands_app')

    def setUp(self):
        if not os.path.isdir(TestSearchCommandsApp.app_root):
            build_command = os.path.join(project_root, 'examples', 'searchcommands_app', 'setup.py build')
            self.skipTest("You must build the searchcommands_app by running " + build_command)
        TestCase.setUp(self)

    @pytest.mark.skipif(six.PY3,
                        reason="Python 2 does not treat Unicode as words for regex, so Python 3 has broken fixtures")
    def test_countmatches_as_unit(self):
        expected, output, errors, exit_status = self._run_command('countmatches', action='getinfo', protocol=1)
        self.assertEqual(0, exit_status, msg=six.text_type(errors))
        self.assertEqual('', errors, msg=six.text_type(errors))
        self._compare_csv_files_time_sensitive(expected, output)

        expected, output, errors, exit_status = self._run_command('countmatches', action='execute', protocol=1)
        self.assertEqual(0, exit_status, msg=six.text_type(errors))

        self.assertEqual('', errors, msg=six.text_type(errors))
        self._compare_csv_files_time_sensitive(expected, output)

        expected, output, errors, exit_status = self._run_command('countmatches')
        self.assertEqual(0, exit_status, msg=six.text_type(errors))
        self.assertEqual('', errors, msg=six.text_type(errors))
        self._compare_chunks(expected, output)

    def test_generatehello_as_unit(self):

        expected, output, errors, exit_status = self._run_command('generatehello', action='getinfo', protocol=1)
        self.assertEqual(0, exit_status, msg=six.text_type(errors))
        self.assertEqual('', errors, msg=six.text_type(errors))
        self._compare_csv_files_time_sensitive(expected, output)

        expected, output, errors, exit_status = self._run_command('generatehello', action='execute', protocol=1)
        self.assertEqual(0, exit_status, msg=six.text_type(errors))
        self.assertEqual('', errors, msg=six.text_type(errors))
        self._compare_csv_files_time_insensitive(expected, output)

        expected, output, errors, exit_status = self._run_command('generatehello')
        self.assertEqual(0, exit_status, msg=six.text_type(errors))
        self.assertEqual('', errors, msg=six.text_type(errors))
        self._compare_chunks(expected, output, time_sensitive=False)

    def test_sum_as_unit(self):

        expected, output, errors, exit_status = self._run_command('sum', action='getinfo', phase='reduce', protocol=1)
        self.assertEqual(0, exit_status, msg=six.text_type(errors))
        self.assertEqual('', errors, msg=six.text_type(errors))
        self._compare_csv_files_time_sensitive(expected, output)

        expected, output, errors, exit_status = self._run_command('sum', action='getinfo', phase='map', protocol=1)
        self.assertEqual(0, exit_status, msg=six.text_type(errors))
        self.assertEqual('', errors, msg=six.text_type(errors))
        self._compare_csv_files_time_sensitive(expected, output)

        expected, output, errors, exit_status = self._run_command('sum', action='execute', phase='map', protocol=1)
        self.assertEqual(0, exit_status, msg=six.text_type(errors))
        self.assertEqual('', errors, msg=six.text_type(errors))
        self._compare_csv_files_time_sensitive(expected, output)

        expected, output, errors, exit_status = self._run_command('sum', action='execute', phase='reduce', protocol=1)
        self.assertEqual(0, exit_status, msg=six.text_type(errors))
        self.assertEqual('', errors, msg=six.text_type(errors))
        self._compare_csv_files_time_sensitive(expected, output)

        expected, output, errors, exit_status = self._run_command('sum', phase='map')
        self.assertEqual(0, exit_status, msg=six.text_type(errors))
        self.assertEqual('', errors, msg=six.text_type(errors))
        self._compare_chunks(expected, output)

        expected, output, errors, exit_status = self._run_command('sum', phase='reduce')
        self.assertEqual(0, exit_status, msg=six.text_type(errors))
        self.assertEqual('', errors, msg=six.text_type(errors))
        self._compare_chunks(expected, output)

    def assertInfoEqual(self, output, expected):
        reader = csv.reader(StringIO(output))
        self.assertEqual([], next(reader))
        fields = next(reader)
        values = next(reader)
        self.assertRaises(StopIteration, reader.__next__)
        output = dict(list(zip(fields, values)))

        reader = csv.reader(StringIO(expected))
        self.assertEqual([], next(reader))
        fields = next(reader)
        values = next(reader)
        self.assertRaises(StopIteration, reader.__next__)
        expected = dict(list(zip(fields, values)))

        self.assertDictEqual(expected, output)

    def _compare_chunks(self, expected, output, time_sensitive=True):
        expected = expected.strip()
        output = output.strip()

        if time_sensitive:
            compare_csv_files = self._compare_csv_files_time_sensitive
        else:
            compare_csv_files = self._compare_csv_files_time_insensitive

        chunks_1 = self._load_chunks(StringIO(expected))
        chunks_2 = self._load_chunks(StringIO(output))

        self.assertEqual(len(chunks_1), len(chunks_2))
        n = 0

        for chunk_1, chunk_2 in zip(chunks_1, chunks_2):
            self.assertDictEqual(
                chunk_1.metadata, chunk_2.metadata,
                f'Chunk {n}: metadata error: "{chunk_1.metadata}" != "{chunk_2.metadata}"')
            compare_csv_files(chunk_1.body, chunk_2.body)
            n += 1

    def _compare_csv_files_time_insensitive(self, expected, output):

        skip_first_row = expected[0:2] == '\r\n'
        expected = StringIO(expected)
        output = StringIO(output)
        line_number = 1

        if skip_first_row:
            self.assertEqual(expected.readline(), output.readline())
            line_number += 1

        expected = csv.DictReader(expected)
        output = csv.DictReader(output)

        for expected_row in expected:
            output_row = next(output)

            try:
                timestamp = float(output_row['_time'])
                datetime.fromtimestamp(timestamp)
            except BaseException as error:
                self.fail(error)
            else:
                output_row['_time'] = expected_row['_time']

            self.assertDictEqual(
                expected_row, output_row, f'Error on line {line_number}: expected {expected_row}, not {output_row}')

            line_number += 1

    def _compare_csv_files_time_sensitive(self, expected, output):
        self.assertEqual(len(expected), len(output))

        skip_first_row = expected[0:2] == '\r\n'
        expected = StringIO(expected)
        output = StringIO(output)
        line_number = 1

        if skip_first_row:
            self.assertEqual(expected.readline(), output.readline())
            line_number += 1

        expected = csv.DictReader(expected)
        output = csv.DictReader(output)

        for expected_row in expected:
            output_row = next(output)
            self.assertDictEqual(
                expected_row, output_row, f'Error on line {line_number}: expected {expected_row}, not {output_row}')
            line_number += 1

    def _get_search_command_path(self, name):
        path = os.path.join(
            project_root, 'examples', 'searchcommands_app', 'build', 'searchcommands_app', 'bin', name + '.py')
        self.assertTrue(os.path.isfile(path))
        return path

    def _load_chunks(ifile):
        import re

        pattern = re.compile(r'chunked 1.0,(?P<metadata_length>\d+),(?P<body_length>\d+)(\n)?')
        decoder = json.JSONDecoder()

        chunks = []

        while True:

            line = ifile.readline()

            if len(line) == 0:
                break

            match = pattern.match(line)
            if match is None:
                continue

            metadata_length = int(match.group('metadata_length'))
            metadata = ifile.read(metadata_length)
            metadata = decoder.decode(metadata)

            body_length = int(match.group('body_length'))
            body = ifile.read(body_length) if body_length > 0 else ''

            chunks.append(TestSearchCommandsApp._Chunk(metadata, body))

        return chunks

    def _run_command(self, name, action=None, phase=None, protocol=2):

        command = self._get_search_command_path(name)

        # P2 [ ] TODO: Test against the version of Python that ships with the version of Splunk used to produce each
        # recording
        # At present we use whatever version of splunk, if any, happens to be on PATH

        # P2 [ ] TODO: Examine the contents of the app and splunklib log files (?)

        expected, output, errors, process = None, None, None, None

        for recording in Recordings(name, action, phase, protocol):
            compressed_file = recording.input_file
            uncompressed_file = os.path.splitext(recording.input_file)[0]
            try:
                with gzip.open(compressed_file, 'rb') as ifile:
                    with io.open(uncompressed_file, 'wb') as ofile:
                        b = bytearray(io.DEFAULT_BUFFER_SIZE)
                        n = len(b)
                        while True:
                            count = ifile.readinto(b)
                            if count == 0:
                                break
                            if count < n:
                                ofile.write(b[:count])
                                break
                            ofile.write(b)

                with io.open(uncompressed_file, 'rb') as ifile:
                    env = os.environ.copy()
                    env['PYTHONPATH'] = os.pathsep.join(sys.path)
                    process = Popen(recording.get_args(command), stdin=ifile, stderr=PIPE, stdout=PIPE, env=env)
                    output, errors = process.communicate()

                with io.open(recording.output_file, 'rb') as ifile:
                    expected = ifile.read()
            finally:
                os.remove(uncompressed_file)

        return six.ensure_str(expected), six.ensure_str(output), six.ensure_str(errors), process.returncode

    _Chunk = namedtuple('Chunk', 'metadata body')


if __name__ == "__main__":
    main()

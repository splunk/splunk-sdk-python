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


from __future__ import absolute_import, division, print_function, unicode_literals

from collections import namedtuple
from cStringIO import StringIO
from datetime import datetime
from itertools import ifilter, imap, izip
from subprocess import PIPE, Popen
from unittest import main, skipUnless, TestCase

import gzip
import json
import csv
import io
import os

from tests.searchcommands import project_root


def pypy():
    try:
        process = Popen(['pypy', '--version'], stderr=PIPE, stdout=PIPE)
    except OSError:
        return False
    else:
        process.communicate()
        return process.returncode == 0


class Recording(object):

    def __init__(self, path):

        self._dispatch_dir = path + '.dispatch_dir'
        self._search = None

        if os.path.exists(self._dispatch_dir):
            with io.open(os.path.join(self._dispatch_dir, 'request.csv')) as ifile:
                reader = csv.reader(ifile)
                for name, value in izip(reader.next(), reader.next()):
                    if name == 'search':
                        self._search = value
                        break
            assert self._search is not None

        splunk_cmd = path + '.splunk_cmd'

        try:
            with io.open(splunk_cmd, 'rb') as f:
                self._args = f.readline().encode().split(None, 5)  # ['splunk', 'cmd', <filename>, <action>, <args>]
        except IOError as error:
            if error.errno != 2:
                raise
            self._args = ['splunk', 'cmd', 'python', None]

        self._input_file = path + '.input.gz'
        self._output_file = path + '.output'

    def get_args(self, command_path):
        self._args[3] = command_path
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


class Recordings(object):

    def __init__(self, name, action, phase, protocol_version):

        basedir = Recordings._prefix + unicode(protocol_version)

        if not os.path.isdir(basedir):
            raise ValueError('Directory "{}" containing recordings for protocol version {} does not exist'.format(
                protocol_version, basedir))

        self._basedir = basedir
        self._name = '.'.join(ifilter(lambda part: part is not None, (name, action, phase)))

    def __iter__(self):

        basedir = self._basedir
        name = self._name

        iterator = imap(
            lambda directory: Recording(os.path.join(basedir, directory, name)), ifilter(
                lambda filename: os.path.isdir(os.path.join(basedir, filename)), os.listdir(basedir)))

        return iterator

    _prefix = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'recordings', 'scpv')


class TestSearchCommandsApp(TestCase):

    app_root = os.path.join(project_root, 'examples', 'searchcommands_app', 'build', 'searchcommands_app')

    def setUp(self):
        if not os.path.isdir(TestSearchCommandsApp.app_root):
            build_command = os.path.join(project_root, 'examples', 'searchcommands_app', 'setup.py build')
            self.skipTest("You must build the searchcommands_app by running " + build_command)
        TestCase.setUp(self)

    def test_countmatches_as_unit(self):

        expected, output, errors, exit_status = self._run_command('countmatches', action='getinfo', protocol=1)
        self.assertEqual(0, exit_status, msg=unicode(errors))
        self.assertEqual('', errors)
        self._compare_csv_files_time_sensitive(expected, output)

        expected, output, errors, exit_status = self._run_command('countmatches', action='execute', protocol=1)
        self.assertEqual(0, exit_status, msg=unicode(errors))
        self.assertEqual('', errors)
        self._compare_csv_files_time_sensitive(expected, output)

        expected, output, errors, exit_status = self._run_command('countmatches')
        self.assertEqual(0, exit_status, msg=unicode(errors))
        self.assertEqual('', errors)
        self._compare_chunks(expected, output)

        return

    def test_generatehello_as_unit(self):

        expected, output, errors, exit_status = self._run_command('generatehello', action='getinfo', protocol=1)
        self.assertEqual(0, exit_status, msg=unicode(errors))
        self.assertEqual('', errors)
        self._compare_csv_files_time_sensitive(expected, output)

        expected, output, errors, exit_status = self._run_command('generatehello', action='execute', protocol=1)
        self.assertEqual(0, exit_status, msg=unicode(errors))
        self.assertEqual('', errors)
        self._compare_csv_files_time_insensitive(expected, output)

        expected, output, errors, exit_status = self._run_command('generatehello')
        self.assertEqual(0, exit_status, msg=unicode(errors))
        self.assertEqual('', errors)
        self._compare_chunks(expected, output, time_sensitive=False)

        return

    @skipUnless(pypy(), 'Skipping TestSearchCommandsApp.test_pypygeneratetext_as_unit because pypy is not on PATH.')
    def test_pypygeneratetext_as_unit(self):

        expected, output, errors, exit_status = self._run_command('pypygeneratetext', action='getinfo', protocol=1)
        self.assertEqual(0, exit_status, msg=unicode(errors))
        self.assertEqual('', errors)
        self._compare_csv_files_time_sensitive(expected, output)

        expected, output, errors, exit_status = self._run_command('pypygeneratetext', action='execute', protocol=1)
        self.assertEqual(0, exit_status, msg=unicode(errors))
        self.assertEqual('', errors)
        self._compare_csv_files_time_insensitive(expected, output)

        expected, output, errors, exit_status = self._run_command('pypygeneratetext')
        self.assertEqual(0, exit_status, msg=unicode(errors))
        self.assertEqual('', errors)
        self._compare_chunks(expected, output, time_sensitive=False)

        return

    def test_sum_as_unit(self):

        expected, output, errors, exit_status = self._run_command('sum', action='getinfo', phase='reduce', protocol=1)
        self.assertEqual(0, exit_status, msg=unicode(errors))
        self.assertEqual('', errors)
        self._compare_csv_files_time_sensitive(expected, output)

        expected, output, errors, exit_status = self._run_command('sum', action='getinfo', phase='map', protocol=1)
        self.assertEqual(0, exit_status, msg=unicode(errors))
        self.assertEqual('', errors)
        self._compare_csv_files_time_sensitive(expected, output)

        expected, output, errors, exit_status = self._run_command('sum', action='execute', phase='map', protocol=1)
        self.assertEqual(0, exit_status, msg=unicode(errors))
        self.assertEqual('', errors)
        self._compare_csv_files_time_sensitive(expected, output)

        expected, output, errors, exit_status = self._run_command('sum', action='execute', phase='reduce', protocol=1)
        self.assertEqual(0, exit_status, msg=unicode(errors))
        self.assertEqual('', errors)
        self._compare_csv_files_time_sensitive(expected, output)

        expected, output, errors, exit_status = self._run_command('sum', phase='map')
        self.assertEqual(0, exit_status, msg=unicode(errors))
        self.assertEqual('', errors)
        self._compare_chunks(expected, output)

        expected, output, errors, exit_status = self._run_command('sum', phase='reduce')
        self.assertEqual(0, exit_status, msg=unicode(errors))
        self.assertEqual('', errors)
        self._compare_chunks(expected, output)

        return

    def assertInfoEqual(self, output, expected):
        reader = csv.reader(StringIO(output))
        self.assertEqual([], reader.next())
        fields = reader.next()
        values = reader.next()
        self.assertRaises(StopIteration, reader.next)
        output = dict(izip(fields, values))

        reader = csv.reader(StringIO(expected))
        self.assertEqual([], reader.next())
        fields = reader.next()
        values = reader.next()
        self.assertRaises(StopIteration, reader.next)
        expected = dict(izip(fields, values))

        self.assertDictEqual(expected, output)

    def _compare_chunks(self, expected, output, time_sensitive = True):

        if time_sensitive:
            self.assertEqual(len(expected), len(output))
            compare_csv_files = self._compare_csv_files_time_sensitive
        else:
            compare_csv_files = self._compare_csv_files_time_insensitive

        chunks_1 = self._load_chunks(StringIO(expected))
        chunks_2 = self._load_chunks(StringIO(output))

        self.assertEqual(len(chunks_1), len(chunks_2))
        n = 0

        for chunk_1, chunk_2 in izip(chunks_1, chunks_2):
            self.assertDictEqual(
                chunk_1.metadata, chunk_2.metadata,
                'Chunk {0}: metadata error: "{1}" != "{2}"'.format(n, chunk_1.metadata, chunk_2.metadata))
            compare_csv_files(chunk_1.body, chunk_2.body)
            n += 1

        return

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
            output_row = output.next()

            try:
                timestamp = float(output_row['_time'])
                datetime.fromtimestamp(timestamp)
            except BaseException as error:
                self.fail(error)
            else:
                output_row['_time'] = expected_row['_time']

            self.assertDictEqual(
                expected_row, output_row, 'Error on line {0}: expected {1}, not {2}'.format(
                    line_number, expected_row, output_row))

            line_number += 1

        self.assertRaises(StopIteration, output.next)
        return

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
            output_row = output.next()
            self.assertDictEqual(
                expected_row, output_row, 'Error on line {0}: expected {1}, not {2}'.format(
                    line_number, expected_row, output_row))
            line_number += 1

        self.assertRaises(StopIteration, output.next)
        return

    def _get_search_command_path(self, name):
        path = os.path.join(
            project_root, 'examples', 'searchcommands_app', 'build', 'searchcommands_app', 'bin', name + '.py')
        self.assertTrue(os.path.isfile(path))
        return path

    def _load_chunks(self, ifile):
        import re

        pattern = re.compile(r'chunked 1.0,(?P<metadata_length>\d+),(?P<body_length>\d+)\n')
        decoder = json.JSONDecoder()

        chunks = []

        while True:

            line = ifile.readline()

            if len(line) == 0:
                break

            match = pattern.match(line)
            self.assertIsNotNone(match)

            metadata_length = int(match.group('metadata_length'))
            metadata = ifile.read(metadata_length)
            metadata = decoder.decode(metadata)

            body_length = int(match.group('body_length'))
            body = ifile.read(body_length) if body_length > 0 else ''

            if len(chunks) == 0:
                self.assertEqual(ifile.readline(), '\n')  # the getinfo exchange protocol requires this

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
                with gzip.open(compressed_file, 'rb') as ifile, io.open(uncompressed_file, 'wb') as ofile:
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
                    process = Popen(recording.get_args(command), stdin=ifile, stderr=PIPE, stdout=PIPE)
                    output, errors = process.communicate()
                with io.open(recording.output_file, 'rb') as ifile:
                    expected = ifile.read()
            finally:
                os.remove(uncompressed_file)

        return expected, output, errors, process.returncode

    _Chunk = namedtuple('Chunk', (b'metadata', b'body'))


if __name__ == "__main__":
    main()

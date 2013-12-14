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
import shutil
import os
import testlib


class TestSearchCommandsApp(testlib.SDKTestCase):

    def setUp(self):
        super(TestSearchCommandsApp, self).setUp()
        for directory in 'error', 'output':
            path = TestSearchCommandsApp._data_file(directory)
            if os.path.exists(path):
                shutil.rmtree(path)
            os.mkdir(path)
        return

    def test_generating_command(self):
        self._run(
            'simulate', [
                'csv=%s' % TestSearchCommandsApp._data_file("input/population.csv"),
                'duration=00:00:10',
                'interval=00:00:01',
                'rate=200'],
            __GETINFO__=(
                'input/population.csv',
                'output/samples.csv',
                'error/test_generating_command.log'),
            __EXECUTE__=(
                'input/population.csv',
                'output/samples.csv',
                'error/test_generating_command.log')
            )
        return

    def test_reporting_command(self):
        self._run(
            'sum', [
                '__map__', 'total=total', 'count'],
            __GETINFO__=(
                'input/counts.csv',
                'output/subtotals.csv',
                'error/test_reporting_command.log'),
            __EXECUTE__=(
                'input/counts.csv',
                'output/subtotals.csv',
                'error/test_reporting_command.log')
            )
        self._run(
            'sum', [
                'total=total', 'count'],
            __GETINFO__=(
                'input/subtotals.csv',
                'output/totals.csv',
                'error/test_reporting_command.log'),
            __EXECUTE__=(
                'input/subtotals.csv',
                'output/totals.csv',
                'error/test_reporting_command.log')
            )
        return

    def test_streaming_command(self, m):
        self._run(
            'countmatches', [
                'fieldname=word_count',
                'pattern=\\w+',
                'text'],
            __GETINFO__=(
                'input/tweets.csv',
                'output/tweet_and_word_counts.csv',
                'error/test_streaming_command.log'),
            __EXECUTE__=(
                'input/tweets.csv',
                'output/tweet_and_word_counts.csv',
                'error/test_generating_command.log')
            )
        return

    def _run(self, command, args, **kwargs):
        for operation in ['__GETINFO__', '__EXECUTE__']:
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
    app_bin = os.path.join(os.path.dirname(package_directory), "examples/searchcommands_app/bin")

if __name__ == "__main__":
    unittest.main()

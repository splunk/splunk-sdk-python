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

from splunklib.searchcommands import validators
import os


class TestSearchCommandsValidators(unittest.TestCase):

    def setUp(self):
        super(TestSearchCommandsValidators, self).setUp()
        return

    def test_file(self):

        # Create a file on $SPLUNK_HOME/var/run/splunk

        file_name = 'TestSearchCommandsValidators.test_file'
        full_path = os.path.join(validators.File._var_run_splunk, file_name)

        with open(full_path, 'w') as f:
            f.write('some text')

        # Verify that you can read the file from $SPLUNK_HOME/var/run/splunk
        # using an absolute or relative path

        validator = validators.File()

        for path in file_name, full_path:
            with validator(path) as f:
                self.assertEqual(f.read(), 'some text')
            self.assertEqual(f.name, full_path)

        # Verify that a ValueError is raised when the file does not exist

        os.unlink(full_path)

        for path in file_name, full_path:
            self.assertRaises(ValueError, validator, path)

        return

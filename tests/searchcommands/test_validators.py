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

from splunklib.searchcommands import validators
import os


class TestValidators(unittest.TestCase):

    def setUp(self):
        super(TestValidators, self).setUp()
        return

    def test_duration(self):

        # Duration validator should parse and format time intervals of the form
        # HH:MM:SS

        validator = validators.Duration()

        for seconds in range(0, 25 * 60 * 60, 59):
            value = str(seconds)
            self.assertEqual(validator(value), seconds)
            self.assertEqual(validator(validator.format(seconds)), seconds)
            value = '%d:%02d' % (seconds / 60, seconds % 60)
            self.assertEqual(validator(value), seconds)
            self.assertEqual(validator(validator.format(seconds)), seconds)
            value = '%d:%02d:%02d' % (seconds / 3600, (seconds / 60) % 60, seconds % 60)
            self.assertEqual(validator(value), seconds)
            self.assertEqual(validator(validator.format(seconds)), seconds)

        self.assertEqual(validator('230:00:00'), 230 * 60 * 60)
        self.assertEqual(validator('23:00:00'), 23 * 60 * 60)
        self.assertEqual(validator('00:59:00'), 59 * 60)
        self.assertEqual(validator('00:00:59'), 59)

        self.assertEqual(validator.format(230 * 60 * 60), '230:00:00')
        self.assertEqual(validator.format(23 * 60 * 60), '23:00:00')
        self.assertEqual(validator.format(59 * 60), '00:59:00')
        self.assertEqual(validator.format(59), '00:00:59')

        self.assertRaises(ValueError, validator, '-1')
        self.assertRaises(ValueError, validator, '00:-1')
        self.assertRaises(ValueError, validator, '-1:00')
        self.assertRaises(ValueError, validator, '00:00:-1')
        self.assertRaises(ValueError, validator, '00:-1:00')
        self.assertRaises(ValueError, validator, '-1:00:00')
        self.assertRaises(ValueError, validator, '00:00:60')
        self.assertRaises(ValueError, validator, '00:60:00')

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

if __name__ == "__main__":
    unittest.main()

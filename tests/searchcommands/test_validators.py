#!/usr/bin/env python
# coding=utf-8
#
# Copyright 2011-2015 Splunk, Inc.
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

from __future__ import absolute_import, division, print_function, unicode_literals

from splunklib.searchcommands import validators
from random import randint
from unittest import main, TestCase

import os
import re
import sys
import tempfile

# P2 [ ] TODO: Verify that all format methods produce 'None' when value is None


class TestValidators(TestCase):

    def setUp(self):
        TestCase.setUp(self)

    def test_boolean(self):

        truth_values = {
            '1': True, '0': False,
            't': True, 'f': False,
            'true': True, 'false': False,
            'y': True, 'n': False,
            'yes': True, 'no': False
        }

        validator = validators.Boolean()

        for value in truth_values:
            for variant in value, value.capitalize(), value.upper():
                for s in unicode(variant), bytes(variant):
                    self.assertEqual(validator.__call__(s), truth_values[value])

        self.assertIsNone(validator.__call__(None))
        self.assertRaises(ValueError, validator.__call__, 'anything-else')

        return

    def test_duration(self):

        # Duration validator should parse and format time intervals of the form
        # HH:MM:SS

        validator = validators.Duration()

        for seconds in range(0, 25 * 60 * 60, 59):
            for value in unicode(seconds), bytes(seconds):
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

    def test_fieldname(self):
        pass

    def test_file(self):

        # Create a file on $SPLUNK_HOME/var/run/splunk

        file_name = 'TestValidators.test_file'
        tempdir = tempfile.gettempdir()
        full_path = os.path.join(tempdir, file_name)

        try:
            validator = validators.File(mode='w', buffering=4096, directory=tempdir)

            with validator(file_name) as f:
                f.write('some text')

            validator = validators.File(mode='a', directory=tempdir)

            with validator(full_path) as f:
                f.write('\nmore text')

            # Verify that you can read the file from a file using an absolute or relative path

            validator = validators.File(directory=tempdir)

            for path in file_name, full_path:
                with validator(path) as f:
                    self.assertEqual(f.read(), 'some text\nmore text')
                self.assertEqual(f.name, full_path)

            # Verify that a ValueError is raised, if the file does not exist

            os.unlink(full_path)

            for path in file_name, full_path:
                self.assertRaises(ValueError, validator, path)
        finally:
            if os.path.exists(full_path):
                os.unlink(full_path)

        return

    def test_integer(self):

        # Point of interest:
        #
        # On all *nix operating systems an int is 32-bits long on 32-bit systems and 64-bits long on 64-bit systems so
        # that you can count on this equality:
        #
        #   sys.maxint == sys.maxsize
        #
        # On Windows an int is always 32-bits long and you cannot count on the same equality. Specifically, on 64-bit
        # systems:
        #
        #   sys.maxint != sys.maxsize

        maxsize = sys.maxsize
        minsize = -(sys.maxsize - 1)

        # The Integer validator should convert values in the range of a Python long which has unlimited precision
        # Anecdotal evidence: This portion of the test checks 5-10 K integer values and runs for less than 2-3 seconds

        validator = validators.Integer()

        def test(integer):
            for s in str(integer), unicode(integer):
                value = validator.__call__(s)
                self.assertEqual(value, integer)
                self.assertIsInstance(value, long)
            self.assertEqual(validator.format(integer), unicode(integer))

        test(2L * minsize)
        test(minsize)
        test(-1)
        test(0)
        test(1)
        test(2L * maxsize)

        for i in xrange(0, 10000):
            test(randint(minsize, maxsize))

        # The Integer validator can impose a range restriction

        validator = validators.Integer(minimum=0)
        self.assertEqual(validator.__call__(0), 0)
        self.assertEqual(validator.__call__(2L * maxsize), 2L * maxsize)
        self.assertRaises(ValueError, validator.__call__, -1)

        validator = validators.Integer(minimum=1, maximum=maxsize)
        self.assertEqual(validator.__call__(1), 1)
        self.assertEqual(validator.__call__(maxsize), maxsize)
        self.assertRaises(ValueError, validator.__call__, 0)
        self.assertRaises(ValueError, validator.__call__, maxsize + 1)

        validator = validators.Integer(minimum=minsize, maximum=maxsize)
        self.assertEqual(validator.__call__(minsize), minsize)
        self.assertEqual(validator.__call__(0), 0)
        self.assertEqual(validator.__call__(maxsize), maxsize)
        self.assertRaises(ValueError, validator.__call__, minsize - 1L)
        self.assertRaises(ValueError, validator.__call__, maxsize + 1L)

        return

    def test_list(self):

        validator = validators.List()
        self.assertEqual(validator.__call__(''), [])
        self.assertEqual(validator.__call__('a,b,c'), ['a', 'b', 'c'])
        self.assertRaises(ValueError, validator.__call__, '"a,b,c')

        self.assertEqual(validator.__call__([]), [])
        self.assertEqual(validator.__call__(None), None)

        validator = validators.List(validators.Integer(1, 10))
        self.assertEqual(validator.__call__(''), [])
        self.assertEqual(validator.__call__('1,2,3'), [1,2,3])
        self.assertRaises(ValueError, validator.__call__, '1,2,0')

        self.assertEqual(validator.__call__([]), [])
        self.assertEqual(validator.__call__(None), None)

    def test_map(self):

        validator = validators.Map(a=1, b=2, c=3)
        self.assertEqual(validator.__call__('a'), 1)
        self.assertEqual(validator.__call__('b'), 2)
        self.assertEqual(validator.__call__('c'), 3)
        self.assertRaises(ValueError, validator.__call__, 'd')

        self.assertEqual(validator.__call__(None), None)

    def test_match(self):

        validator = validators.Match('social security number', r'\d{3}-\d{2}-\d{4}')
        self.assertEqual(validator.__call__('123-45-6789'), '123-45-6789')
        self.assertRaises(ValueError, validator.__call__, 'foo')

        self.assertEqual(validator.__call__(None), None)
        self.assertEqual(validator.format(None), None)
        self.assertEqual(validator.format('123-45-6789'), '123-45-6789')

    def test_option_name(self):
        pass

    def test_regular_expression(self):

        validator = validators.RegularExpression()
        self.assertIsInstance(validator.__call__('a'), re._pattern_type)
        self.assertEqual(validator.__call__(None), None)
        self.assertRaises(ValueError, validator.__call__, '(a')

    def test_set(self):

        validator = validators.Set('a', 'b', 'c')
        self.assertEqual(validator.__call__('a'), 'a')
        self.assertEqual(validator.__call__('b'), 'b')
        self.assertEqual(validator.__call__('c'), 'c')
        self.assertEqual(validator.__call__(None), None)
        self.assertRaises(ValueError, validator.__call__, 'd')


if __name__ == "__main__":
    main()

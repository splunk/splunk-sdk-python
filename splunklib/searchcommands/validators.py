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

import re
import sys


class Validator(object):
    """ TODO: Documentation
    """
    def __call__(self, value):
        raise NotImplementedError()


class Boolean(Validator):
    """ TODO: Documentation
    """
    truth_values = {
        '1': True, '0': False,
        't': True, 'f': False,
        'true': True, 'false': False,
        'y': True, 'n': False,
        'yes': True, 'No': False
    }

    def __call__(self, value):
        if not isinstance(value, bool):
            value = str(value).lower()
            if value not in Boolean.truth_values:
                raise ValueError('Unrecognized truth value: %s' % value)
            value = Boolean.truth_values[value]
        return value


class Duration(Validator):
    """ TODO: Documentation
    """
    from time import strptime

    def __call__(self, value):
        try:
            value = strptime(value, '%H:%M:%S')
        except ValueError as e:
            raise ValueError(str(e).capitalize())
        return 3600 * value.tm_hour + 60 * value.tm_min + value.tm_sec


class Fieldname(Validator):
    """ TODO: Documentation
    """
    import re
    pattern = re.compile(r'''[_.a-zA-Z-][_.a-zA-Z0-9-]*$''')

    def __call__(self, value):
        value = str(value)
        if Fieldname.pattern.match(value) is None:
            raise ValueError('Illegal characters in fieldname: %s' % value)
        return value


class File(Validator):
    """ TODO: Documentation

    """
    def __init__(self, mode='r', buffering=-1):
        self.mode = mode
        self.buffering = buffering

    def __call__(self, value):
        try:
            value = open(str(value), self.mode, self.buffering)
        except IOError as e:
            raise ValueError('Cannot open %s with mode=%s and buffering=%s: %s'
                             % (value, self.mode, self.buffering, e))
        return value


class Integer(Validator):
    """ TODO: Documentation

    """
    def __init__(self, minimum=-sys.maxint-1, maximum=sys.maxint):
        self.minimum = minimum
        self.maximum = maximum

    def __call__(self, value):
        value = int(value)
        if not (self.minimum <= value <= self.maximum):
            raise ValueError('Expected integer in the range [%d,%d]: %d' %
                             (self.minimum, self.maximum, value))
        return value


class OptionName(Validator):
    """ TODO: Documentation

    """
    import re
    pattern = re.compile(r'''[a-zA-Z][_a-zA-Z0-9]*$''')

    def __call__(self, value):
        value = str(value)
        if OptionName.pattern.match(value) is None:
            raise ValueError('Illegal characters in option name: %s' % value)
        return value


class RegularExpression(Validator):
    """ TODO: Documentation

    """
    def __call__(self, value):
        value = str(value)
        try:
            value = re.compile(value)
        except re.error as e:
            raise ValueError('%s: %s' % (str(e).capitalize(), value))
        return RegularExpression.Pattern(value)

    class Pattern(object):

        def __init__(self, regex):
            self.regex = regex

        def __repr__(self):
            return 'RegularExpression.Pattern(%s)' % self.regex

        def __str__(self):
            return self.regex.pattern

        @property
        def flags(self):
            return self.regex.flags

        @property
        def groups(self):
            return self.regex.groups

        @property
        def groupindex(self):
            return self.regex.groupindex

        @property
        def pattern(self):
            return self.regex.pattern

        def findall(self, string, pos=0, end=-1):
            return self.regex.findall(string, pos, end)

        def finditer(self, string, pos=0, end=-1):
            return self.regex.finditer(string, pos, end)

        def match(self, string, pos=0, end=-1):
            return self.regex.match(string, pos, end)

        def search(self, string, pos=0, end=-1):
            return self.regex.search(string, pos, end)

        def split(self, string, max_split=0):
            return self.regex.split(string, max_split)

        def sub(self, repl, string, count=0):
            return self.regex.sub(string, repl, string, count)

        def subn(self, repl, string, count=0):
            return self.regex.subn(string, repl, string, count)


class Set(Validator):
    """ TODO: Documentation

    """
    def __init__(self, *args):
        self.membership = args

    def __call__(self, value):
        value = str(value)
        if value not in self.membership:
            raise ValueError('Unrecognized value: %s' % value)
        return value

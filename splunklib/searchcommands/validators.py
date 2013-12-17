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

from time import strptime
import re
import sys


class Validator(object):
    """ TODO: Documentation

    """
    def __call__(self, value):
        raise NotImplementedError()

    def format(self, value):
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
    def __call__(self, value):
        if value is not None:
            try:
                value = strptime(value, '%H:%M:%S')
            except ValueError as e:
                raise ValueError(str(e).capitalize())
            value = 3600 * value.tm_hour + 60 * value.tm_min + value.tm_sec
        return value


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
        if value is not None:
            try:
                value = open(str(value), self.mode, self.buffering)
            except IOError as e:
                raise ValueError(
                    'Cannot open %s with mode=%s and buffering=%s: %s'
                    % (value, self.mode, self.buffering, e))
        return value

    def format(self, value):
        return value.name


class Integer(Validator):
    """ TODO: Documentation

    """
    def __init__(self, minimum=-sys.maxint-1, maximum=sys.maxint):
        self.minimum = minimum
        self.maximum = maximum

    def __call__(self, value):
        if value is not None:
            value = int(value)
            if not (self.minimum <= value <= self.maximum):
                raise ValueError(
                    'Expected integer in the range [%d,%d]: %d'
                    % (self.minimum, self.maximum, value))
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
        return value

    def format(self, value):
        return value.pattern


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


class String(Validator):
    """ TODO: Documentation

    """
    def __call__(self, value):
        return str(value)

    def format(self, value):
        return str(value)

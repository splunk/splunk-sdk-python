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

import os
import re
import sys


class Validator(object):
    """ Base class for validators that check and format search command options.

    You must inherit from this class and override :code:`Validator.__call__` and
    :code:`Validator.format`. :code:`Validator.__call__` should convert the
    value it receives as argument and then return it or raise a
    :code:`ValueError`, if the value will not convert.

    :code:`Validator.format` should return a human readable version of the value
    it receives as argument the same way :code:`str` does.

    """
    def __call__(self, value):
        raise NotImplementedError()

    def format(self, value):
        raise NotImplementedError()


class Boolean(Validator):
    """ Validates Boolean option values.

    """
    truth_values = {
        '1': True, '0': False,
        't': True, 'f': False,
        'true': True, 'false': False,
        'y': True, 'n': False,
        'yes': True, 'no': False
    }

    def __call__(self, value):
        if not (value is None or isinstance(value, bool)):
            value = str(value).lower()
            if value not in Boolean.truth_values:
                raise ValueError('Unrecognized truth value: %s' % value)
            value = Boolean.truth_values[value]
        return value


class Fieldname(Validator):
    """ Validates field name option values.

    """
    pattern = re.compile(r'''[_.a-zA-Z-][_.a-zA-Z0-9-]*$''')

    def __call__(self, value):
        value = str(value)
        if Fieldname.pattern.match(value) is None:
            raise ValueError('Illegal characters in fieldname: %s' % value)
        return value


class File(Validator):
    """ Validates file option values.

    """
    def __init__(self, mode='r', buffering=-1):
        self.mode = mode
        self.buffering = buffering

    def __call__(self, value):
        if value is not None:
            try:
                path = str(value)
                if not os.path.isabs(path):
                    path = os.path.join(File._var_run_splunk, path)
                value = open(path, self.mode, self.buffering)
            except IOError as e:
                raise ValueError(
                    'Cannot open %s with mode=%s and buffering=%s: %s'
                    % (value, self.mode, self.buffering, e))
        return value

    def format(self, value):
        return value.name

    _var_run_splunk = os.path.join(
        os.environ['SPLUNK_HOME'], "var", "run", "splunk")


class Integer(Validator):
    """ Validates integer option values.

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


class Duration(Validator):
    """ Validates duration option values.

    """
    def __call__(self, value):

        if value is None:
            return None

        try:
            p = value.split(':', 2)
            _60 = Duration._60
            _unsigned = Duration._unsigned
            if len(p) == 1:
                result = _unsigned(p[0])
            if len(p) == 2:
                result = 60 * _unsigned(p[0]) + _60(p[1])
            if len(p) == 3:
                result = 3600 * _unsigned(p[0]) + 60 * _60(p[1]) + _60(p[2])
        except ValueError:
            raise ValueError("Invalid duration value: %s", value)

        return result

    def format(self, value):

        value = int(value)

        s = value % 60
        m = value / 60 % 60
        h = value / (60 * 60)

        return '%02d:%02d:%02d' % (h, m, s)

    _60 = Integer(0, 59)
    _unsigned = Integer(0)


class OptionName(Validator):
    """ Validates option names.

    """
    pattern = re.compile(r'''[a-zA-Z][_a-zA-Z0-9]*$''')

    def __call__(self, value):
        value = str(value)
        if OptionName.pattern.match(value) is None:
            raise ValueError('Illegal characters in option name: %s' % value)
        return value


class RegularExpression(Validator):
    """ Validates regular expression option values.

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
    """ Validates set option values.

    """
    def __init__(self, *args):
        self.membership = args

    def __call__(self, value):
        if value is not None:
            value = str(value)
            if value not in self.membership:
                raise ValueError('Unrecognized value: %s' % value)
        return value

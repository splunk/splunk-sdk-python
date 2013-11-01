# coding=utf-8
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

import sys

# BFR: Fix this bug: sys.stdin and sys.stdout must be opened in binary,  not
# text mode to ensure we read/write carriage returns correctly on all platforms.
# The newlines argument to open() can be used to select the line terminators
# recognized. Study the csv code. It reads/writes lines correctly; pass for now

import collections
import urllib2 as urllib


class InputHeader(object):
    def __init__(self):
        self._settings = collections.OrderedDict()

    def __getitem__(self, name):
        return self._settings[name]

    def __iter__(self):
        for item in self._settings.items():
            yield item

    def __repr__(self):
        return ''.join(
            [InputHeader.__name__, '(', repr(self._settings.items()), ')'])

    def read(self, input_file):
        """ Reads an InputHeader from sys.stdin

        The input header is read as a sequence of *<name>***:***<value>* pairs
        separated by a newline. The end of the input header is signalled by an
        empty line or an end-of-file.

        """
        name = None
        for line in input_file:
            if line[-1] == '\n':
                line = line[:-1]
            if len(line) == 0:
                break
            value = line.split(':', 1)
            if len(value) == 2:
                name, value = value
                self._settings[name] = urllib.unquote(value)
            elif name is not None:
                # add new line to multi-line value
                self._settings[name] = '\n'.join(
                    [self._settings[name], urllib.unquote(line)])
            else:
                pass  # on unnamed multi-line value
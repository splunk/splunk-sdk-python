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

from __future__ import absolute_import
import csv


class DictReader(csv.DictReader, object):
    """ Splunk multi-value-aware CSV dictionary reader. """

    def __init__(self, input_file):
        super(DictReader, self).__init__(
            input_file, dialect='splunklib.searchcommands')
        self.__fieldnames = None
        self.__mv_fieldnames = None

    @csv.DictReader.fieldnames.getter
    def fieldnames(self):
        if self._fieldnames is None:
            try:
                self._fieldnames = self.reader.next()
            except StopIteration:
                pass
            self.line_num = self.reader.line_num
            self.__mv_fieldnames = []
            self.__fieldnames = []
            for name in self._fieldnames:
                if name.startswith('__mv_'):
                    # Store this pair: <fieldname>, __mv_<fieldname>
                    self.__mv_fieldnames.append((name[len('__mv_'):], name))
                else:
                    self.__fieldnames.append(name)
        return self.__fieldnames

    def next(self):
        row = super(DictReader, self).next()
        self.fieldnames  # for side effects
        for fieldname, mv_fieldname in self.__mv_fieldnames:
            # Decode, store and then delete all `__mv_` fields in `row`
            list_value = DictReader._decode_list(row[mv_fieldname])
            if list_value is not None:
                row[fieldname] = list_value if len(list_value) > 1 else list[0]
            del row[mv_fieldname]
        return row

    @staticmethod
    def _decode_list(mv):
        if len(mv) == 0:
            return None
        in_value = False
        value = ''
        i = 0
        l = []
        while i < len(mv):
            if not in_value:
                if mv[i] == '$':
                    in_value = True
                elif mv[i] != ';':
                    return None
            else:
                if mv[i] == '$' and i + 1 < len(mv) and mv[i + 1] == '$':
                    value += '$'
                    i += 1
                elif mv[i] == '$':
                    in_value = False
                    l.append(value)
                    value = ''
                else:
                    value += mv[i]
            i += 1
        return l

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

from numbers import Number
import csv


class DictWriter(csv.DictWriter, object):
    """ Splunk multi-value-aware CSV dictionary writer. """

    def __init__(self, f, command, fieldnames=None, mv_delimiter='\n'):
        super(DictWriter, self).__init__(
            f, fieldnames, dialect='splunklib.searchcommands')
        self._command = command
        self._fieldnames = None
        self._mv_delimiter = mv_delimiter
        self._output_file = f

    def writeheader(self):

        if self._header_written():
            return

        _fieldnames = self.fieldnames + ['__mv_' + fn for fn in self.fieldnames]
        save_fieldnames = self.fieldnames
        self.fieldnames = _fieldnames

        try:
            self._command.messages.write(self._output_file)
            self.writer.writerow(_fieldnames)
        finally:
            self.fieldnames = save_fieldnames

        self._fieldnames = _fieldnames

    def writerow(self, record):
        self._writeheader(record)
        self._writerow(record)

    def writerows(self, records):
        self._writeheader(records[0])
        for record in records:
            self._writerow(record)

    def _encode_list(self, value):
        if len(value) == 0:
            return None, None
        if len(value) == 1:
            return value[0], None
        multi_value = ';'.join(
            ['$' + DictWriter._to_string(item).replace('$', '$$') + '$' for item
             in value])
        value = self._mv_delimiter.join([DictWriter._to_string(item) for item in value])
        return value, multi_value

    def _header_written(self):
        return self._fieldnames is not None

    @staticmethod
    def _to_string(item):
        if isinstance(item, bool):
            return 't' if item else 'f'
        if isinstance(item, basestring):
            return item.decode('utf-8')
        if isinstance(item, Number):
            return str(item)
        return repr(item)

    def _writeheader(self, record):
        if self.fieldnames is None:
            self.fieldnames = record.keys()
        self.writeheader()

    def _writerow(self, record):
        row = {}

        for fieldname in self.fieldnames:
            try:
                value = record[fieldname]
                if isinstance(value, list):
                    value, multi_value = self._encode_list(value)
                    row[fieldname] = value
                    if multi_value is not None:
                        row['__mv_' + fieldname] = multi_value
                elif isinstance(value, bool):
                    row[fieldname] = int(value)
                else:
                    row[fieldname] = value
            except KeyError:
                row[fieldname] = ''

        save_fieldnames = self.fieldnames
        self.fieldnames = self._fieldnames

        try:
            result = super(DictWriter, self).writerow(row)
        finally:
            self.fieldnames = save_fieldnames

        return result

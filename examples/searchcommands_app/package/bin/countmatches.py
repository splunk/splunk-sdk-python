#!/usr/bin/env python
# coding=utf-8
#
# Copyright © 2011-2015 Splunk, Inc.
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
import app

from splunklib.searchcommands import dispatch, StreamingCommand, Configuration, Option, validators
import sys


@Configuration()
class CountMatchesCommand(StreamingCommand):
    """ Counts the number of non-overlapping matches to a regular expression in a set of fields.

    ##Syntax

    .. code-block::
        countmatches fieldname=<field> pattern=<regular_expression> <field-list>

    ##Description

    A count of the number of non-overlapping matches to the regular expression specified by `pattern` is computed for
    each record processed. The result is stored in the field specified by `fieldname`. If `fieldname` exists, its value
    is replaced. If `fieldname` does not exist, it is created. Event records are otherwise passed through to the next
    pipeline processor unmodified.

    ##Example

    Count the number of words in the `text` of each tweet in tweets.csv and store the result in `word_count`.

    .. code-block::
        | inputlookup tweets | countmatches fieldname=word_count pattern="\\w+" text

    """
    fieldname = Option(
        doc='''
        **Syntax:** **fieldname=***<fieldname>*
        **Description:** Name of the field that will hold the match count''',
        require=True, validate=validators.Fieldname())

    pattern = Option(
        doc='''
        **Syntax:** **pattern=***<regular-expression>*
        **Description:** Regular expression pattern to match''',
        require=True, validate=validators.RegularExpression())

    def stream(self, records):
        self.logger.debug('CountMatchesCommand: %s', self)  # logs command line
        pattern = self.pattern
        for record in records:
            count = 0L
            for fieldname in self.fieldnames:
                matches = pattern.findall(unicode(record[fieldname]))
                count += len(matches)
            record[self.fieldname] = count
            yield record

dispatch(CountMatchesCommand, sys.argv, sys.stdin, sys.stdout, __name__)

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
import app

from splunklib.searchcommands import dispatch, EventingCommand, Configuration, Option
from splunklib.searchcommands.validators import Code

import sys


@Configuration()
class FilterCommand(EventingCommand):
    """ Filters, augments, and updates records on the events stream.

    ##Syntax

    .. code-block::
        filter predicate=<expression> update=<statements>

    ##Description

    The :code:`filter` command filters records from the events stream returning only those for which the
    :code:`predicate` is true after applying :code:`update` statements. If no :code:`predicate` is specified, all
    records are returned. If no :code:`update` is specified, records are returned unmodified.

    The :code:`predicate` and :code:`update` operations execute in a restricted scope that includes the standard Python
    built-in module and the current record. Within this scope fields are accessible by name as local variables.

    ##Example

    Excludes odd-numbered records and replaces all occurrences of "world" with "Splunk" in the _raw field produced by
    the :code:`generatetext` command.

    .. code-block::
        | generatetext text="Hello world! How the heck are you?" count=6
        | filter predicate="(long(_serial) & 1) == 0" update="_raw = _raw.replace('world', 'Splunk')"

    """
    predicate = Option(doc='''
        **Syntax:** **predicate=***<expression>*
        **Description:** Filters records from the events stream returning only those for which the predicate is True.

        ''', validate=Code('eval'))

    update = Option(doc='''
        **Syntax:** **map=***<statements>*
        **Description:** Augments or modifies records for which the predicate is True before they are returned.

        ''', validate=Code('exec'))

    def transform(self, records):
        predicate = self.predicate
        update = self.update

        if predicate and update:
            predicate = predicate.object
            update = update.object

            for record in records:
                if eval(predicate, FilterCommand._globals, record):
                    exec(update, FilterCommand._globals, record)
                    yield record
            return

        if predicate:
            predicate = predicate.object
            for record in records:
                if eval(predicate, FilterCommand._globals, record):
                    yield record
            return

        if update:
            update = update.object
            for record in records:
                exec(update, FilterCommand._globals, record)
                yield record
            return

        for record in records:
            yield record

    _globals = {'__builtins__': __builtins__}


dispatch(FilterCommand, sys.argv, sys.stdin, sys.stdout, __name__)

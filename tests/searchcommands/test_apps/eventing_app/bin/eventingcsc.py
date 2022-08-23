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

import os,sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))
from splunklib.searchcommands import dispatch, EventingCommand, Configuration, Option, validators


@Configuration()
class EventingCSC(EventingCommand):
    """
    The eventingapp command filters records from the events stream returning only those for which the status is same
    as search query.

    Example:

    ``index="_internal" | head 4000 | eventingcsc status=200``

    Returns records having status 200 as mentioned in search query.
    """

    status = Option(
        doc='''**Syntax:** **status=***<value>*
        **Description:** record having same status value will be returned.''',
        require=True)

    def transform(self, records):
        for record in records:
            if str(self.status) == record["status"]:
                yield record


dispatch(EventingCSC, sys.argv, sys.stdin, sys.stdout, __name__)

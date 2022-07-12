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

import os,sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))
from splunklib.searchcommands import dispatch, StreamingCommand, Configuration, Option, validators


@Configuration()
class StreamingCSC(StreamingCommand):
    """
    The streamingapp command returns events with a one new field 'fahrenheit'.

    Example:

    ``| makeresults count=5 | eval celsius = random()%100 | streamingcsc``

    returns a records with one new filed 'fahrenheit'.
    """

    def stream(self, records):
        for record in records:
            record["fahrenheit"] = (float(record["celsius"]) * 1.8) + 32
            yield record


dispatch(StreamingCSC, sys.argv, sys.stdin, sys.stdout, __name__)

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

from splunklib.searchcommands import dispatch, GeneratingCommand, Configuration, Option, validators
import sys
import time


@Configuration()
class GenerateHelloCommand(GeneratingCommand):

    count = Option(require=True, validate=validators.Integer(0))
 
    def generate(self):
        for i in range(1, self.count + 1):
            text = 'Hello World %d' % i
            yield {'_time': time.time(), 'event_no': i, '_raw': text}
 
dispatch(GenerateHelloCommand, sys.argv, sys.stdin, sys.stdout, __name__)

#!/usr/bin/env python
#
# Copyright 2011-2012 Splunk, Inc.
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
import unittest

import splunklib.client as client
from utils import parse

opts = None # Command line options

class TestCase(unittest.TestCase):
    def test(self):
        fired_alerts = client.connect(**opts.kwargs).fired_alerts

        for fired_alert in fired_alerts:
            fired_alert.content

if __name__ == "__main__":
    opts = parse(sys.argv[1:], {}, ".splunkrc")
    unittest.main(argv=sys.argv[:1])

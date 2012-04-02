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

def read_baseline(filename):
    fd = open(filename, "r")
    baseline = fd.read().replace("\n", "")
    fd.close()
    return baseline

class TestCase(unittest.TestCase):
    def check_module(self, modulename):
        __import__(modulename)
        module = sys.modules[modulename]
        names = str(dir(module))
        baseline = read_baseline(modulename + ".baseline")
        self.assertEqual(names, baseline)

    def test_splunklib(self):
        self.check_module("splunklib")

    def test_binding(self):
        self.check_module("splunklib.binding")

    def test_client(self):
        self.check_module("splunklib.client")

    def test_data(self):
        self.check_module("splunklib.data")

    def test_results(self):
        self.check_module("splunklib.results")

if __name__ == "__main__":
    unittest.main()

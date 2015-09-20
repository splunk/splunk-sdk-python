#!/usr/bin/env python
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

from tests.modularinput.modularinput_testlib import unittest, data_open
from splunklib.modularinput.validation_definition import ValidationDefinition

class ValidationDefinitionTestCase(unittest.TestCase):
    def test_validation_definition_parse(self):
        """Check that parsing produces expected result"""
        found = ValidationDefinition.parse(data_open("data/validation.xml"))

        expected = ValidationDefinition()
        expected.metadata = {
            "server_host": "tiny",
            "server_uri": "https://127.0.0.1:8089",
            "checkpoint_dir": "/opt/splunk/var/lib/splunk/modinputs",
            "session_key": "123102983109283019283",
            "name": "aaa"
        }
        expected.parameters = {
            "param1": "value1",
            "param2": "value2",
            "disabled": "0",
            "index": "default",
            "multiValue": ["value1", "value2"],
            "multiValue2": ["value3", "value4"]
        }

        self.assertEqual(expected, found)

if __name__ == "__main__":
    unittest.main()
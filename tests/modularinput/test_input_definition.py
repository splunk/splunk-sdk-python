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
from splunklib.modularinput.input_definition import InputDefinition

class InputDefinitionTestCase(unittest.TestCase):

    def test_parse_inputdef_with_zero_inputs(self):
        """Check parsing of XML that contains only metadata"""

        found = InputDefinition.parse(data_open("data/conf_with_0_inputs.xml"))

        expectedDefinition = InputDefinition()
        expectedDefinition.metadata = {
            "server_host": "tiny",
            "server_uri": "https://127.0.0.1:8089",
            "checkpoint_dir": "/some/dir",
            "session_key": "123102983109283019283"
        }

        self.assertEqual(found, expectedDefinition)

    def test_parse_inputdef_with_two_inputs(self):
        """Check parsing of XML that contains 2 inputs"""

        found = InputDefinition.parse(data_open("data/conf_with_2_inputs.xml"))

        expectedDefinition = InputDefinition()
        expectedDefinition.metadata = {
            "server_host": "tiny",
            "server_uri": "https://127.0.0.1:8089",
            "checkpoint_dir": "/some/dir",
            "session_key": "123102983109283019283"
        }
        expectedDefinition.inputs["foobar://aaa"] = {
            "param1": "value1",
            "param2": "value2",
            "disabled": "0",
            "index": "default"
        }
        expectedDefinition.inputs["foobar://bbb"] = {
            "param1": "value11",
            "param2": "value22",
            "disabled": "0",
            "index": "default",
            "multiValue": ["value1", "value2"],
            "multiValue2": ["value3", "value4"]
        }

        self.assertEqual(expectedDefinition, found)

    def test_attempt_to_parse_malformed_input_definition_will_throw_exception(self):
        """Does malformed XML cause the expected exception."""

        with self.assertRaises(ValueError):
            found = InputDefinition.parse(data_open("data/conf_with_invalid_inputs.xml"))

if __name__ == "__main__":
    unittest.main()
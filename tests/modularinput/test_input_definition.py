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

try:
    import unittest2 as unittest
except ImportError:
    import unittest
import sys
from splunklib.modularinput.input_definition import InputDefinition
from splunklib.modularinput.malformed_data_exception import MalformedDataException

sys.path.insert(0, "../..")

class InputDefinitionTestCase(unittest.TestCase):

    def setUp(self):
        super(InputDefinitionTestCase, self).setUp()

    def test_parse_inputdef_with_zero_inputs(self):
        found = InputDefinition().parse_definition(open("data/conf_with_0_inputs.xml"))

        expectedDefinition = InputDefinition()
        expectedDefinition.metadata = {
            "server_host": "tiny",
            "server_uri": "https://127.0.0.1:8089",
            "checkpoint_dir": "/some/dir",
            "session_key": "123102983109283019283"
        }

        self.assertEqual(found, expectedDefinition)

    def test_parse_inputdef_with_two_inputs(self):
        found = InputDefinition().parse_definition(open("data/conf_with_2_inputs.xml"))

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
        """
        Check that parsing an InputDefinition from malformed XML produces the expected exception.
        """
        with self.assertRaises(MalformedDataException):
            found = InputDefinition().parse_definition(open("data/conf_with_invalid_inputs.xml"))


if __name__ == "__main__":
    unittest.main()
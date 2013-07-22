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
from splunklib.modularinput.validation_definition import ValidationDefinition

sys.path.insert(0, "../..")

class ValidationDefinitionTestCase(unittest.TestCase):
    """
    Check equality of parsed ValidationDefinition object from known XML
    with manually initialized ValidationDefinition object.
    """
    def setUp(self):
        super(ValidationDefinitionTestCase, self).setUp()

    def test_validation_definition_parse(self):
        found = ValidationDefinition().parseDefintion(open("data/validation.xml"))

        expected = ValidationDefinition()
        expected.metadata = {"server_host": "tiny", "server_uri": "https://127.0.0.1:8089",\
                             "checkpoint_dir": "/opt/splunk/var/lib/splunk/modinputs",\
                             "session_key": "123102983109283019283",\
                             "name": "aaa"}
        parameters = {"param1": "value1", "param2": "value2", "disabled": "0", "index": "default"}
        parameters["multiValue"] = ["value1", "value2"]
        parameters["multiValue2"] = ["value3", "value4"]
        expected.parameters = parameters

        self.assertEqual(expected, found)

if __name__ == "__main__":
    unittest.main()
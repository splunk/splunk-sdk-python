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

try:
    import unittest2 as unittest
except ImportError:
    import unittest
import testlib


class ModularInputKindTestCase(testlib.SDKTestCase):
    def setUp(self):
        super(ModularInputKindTestCase, self).setUp()
        self.uncheckedRestartSplunk()
    
    def test_lists_modular_inputs(self):
        if self.service.splunk_version[0] < 5:
            print "Modular inputs don't exist prior to Splunk 5.0. Skipping."
            return
        elif not self.app_collection_installed():
            print "Test requires sdk-app-collection. Skipping."
            return
        else:
            # Install modular inputs to list, and restart
            # so they'll show up.
            self.install_app_from_collection("modular-inputs")
            self.uncheckedRestartSplunk()

            inputs = self.service.inputs
            if ('abcd','test2') not in inputs:
                inputs.create('abcd', 'test2', field1='boris')

            input = inputs['abcd', 'test2']
            self.assertEqual(input.field1, 'boris')
            for m in self.service.modular_input_kinds:
                self.check_modular_input_kind(m)

    def check_modular_input_kind(self, m):
        print m.name
        if m.name == 'test1':
            self.assertEqual('Test "Input" - 1', m['title'])
            self.assertEqual("xml", m['streaming_mode'])
        elif m.name == 'test2':
            self.assertEqual('test2', m['title'])
            self.assertEqual('simple', m['streaming_mode'])

if __name__ == "__main__":
    unittest.main()
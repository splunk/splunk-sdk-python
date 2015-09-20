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

import testlib
try:
    import unittest
except ImportError:
    import unittest2 as unittest
import splunklib.client as client

class ModularInputKindTestCase(testlib.SDKTestCase):
    def setUp(self):
        super(ModularInputKindTestCase, self).setUp()
        self.uncheckedRestartSplunk()

    def test_list_arguments(self):
        if not self.app_collection_installed():
            print "Test requires sdk-app-collection. Skipping."
            return
        self.install_app_from_collection("modular-inputs")

        if self.service.splunk_version[0] < 5:
            # Not implemented before 5.0
            return

        test1 = self.service.modular_input_kinds['test1']

        expected_args = set(["name", "resname", "key_id", "no_description", "empty_description",
                             "arg_required_on_edit", "not_required_on_edit", "required_on_create",
                            "not_required_on_create", "number_field", "string_field", "boolean_field"])
        found_args = set(test1.arguments.keys())

        self.assertEqual(expected_args, found_args)

    def test_update_raises_exception(self):
        if not self.app_collection_installed():
            print "Test requires sdk-app-collection. Skipping."
            return
        self.install_app_from_collection("modular-inputs")

        if self.service.splunk_version[0] < 5:
            # Not implemented before 5.0
            return

        test1 = self.service.modular_input_kinds['test1']
        self.assertRaises(client.IllegalOperationException, test1.update, a="b")

    def check_modular_input_kind(self, m):
        if m.name == 'test1':
            self.assertEqual('Test "Input" - 1', m['title'])
            self.assertEqual("xml", m['streaming_mode'])
        elif m.name == 'test2':
            self.assertEqual('test2', m['title'])
            self.assertEqual('simple', m['streaming_mode'])

    def test_list_modular_inputs(self):
        if not self.app_collection_installed():
            print "Test requires sdk-app-collection. Skipping."
            return
        self.install_app_from_collection("modular-inputs")

        if self.service.splunk_version[0] < 5:
            # Not implemented before 5.0
            return

        for m in self.service.modular_input_kinds:
            self.check_modular_input_kind(m)

if __name__ == "__main__":
    try:
        import unittest2 as unittest
    except ImportError:
        import unittest
    unittest.main()
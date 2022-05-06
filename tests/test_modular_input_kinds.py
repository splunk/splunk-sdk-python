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

from tests import testlib

from splunklib import client

import pytest


class ModularInputKindTestCase(testlib.SDKTestCase):
    def setUp(self):
        super().setUp()
        self.uncheckedRestartSplunk()

    @pytest.mark.app
    def test_list_arguments(self):
        self.install_app_from_collection("modular_inputs")

        if self.service.splunk_version[0] < 5:
            # Not implemented before 5.0
            return

        test1 = self.service.modular_input_kinds['test1']

        expected_args = {"name", "resname", "key_id", "no_description", "empty_description", "arg_required_on_edit",
                         "not_required_on_edit", "required_on_create", "not_required_on_create", "number_field",
                         "string_field", "boolean_field"}
        found_args = set(test1.arguments.keys())

        self.assertEqual(expected_args, found_args)

    @pytest.mark.app
    def test_update_raises_exception(self):
        self.install_app_from_collection("modular_inputs")

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

    @pytest.mark.app
    def test_list_modular_inputs(self):
        self.install_app_from_collection("modular_inputs")

        if self.service.splunk_version[0] < 5:
            # Not implemented before 5.0
            return

        for m in self.service.modular_input_kinds:
            self.check_modular_input_kind(m)


if __name__ == "__main__":
    import unittest

    unittest.main()

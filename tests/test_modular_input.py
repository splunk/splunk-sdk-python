#!/usr/bin/env python
#
# Copyright © 2011-2024 Splunk, Inc.
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

import logging

import pytest

from tests import testlib


@pytest.mark.smoke
class ModularInputKindTestCase(testlib.SDKTestCase):
    def setUp(self):
        super().setUp()
        self.uncheckedRestartSplunk()

    @pytest.mark.app
    def test_lists_modular_inputs(self):
        # Install modular inputs to list, and restart
        # so they'll show up.
        self.install_app_from_collection("modular_inputs")
        self.uncheckedRestartSplunk()

        inputs = self.service.inputs
        if ("abcd", "test2") not in inputs:
            inputs.create("abcd", "test2", field1="boris")

        input = inputs["abcd", "test2"]
        self.assertEqual(input.field1, "boris")
        for kind in self.service.modular_input_kinds:
            self.check_modular_input_kind(kind)

    def check_modular_input_kind(self, kind):
        logging.debug(kind.name)
        if kind.name == "test1":
            self.assertEqual('Test "Input" - 1', kind["title"])
            self.assertEqual("xml", kind["streaming_mode"])
        elif kind.name == "test2":
            self.assertEqual("test2", kind["title"])
            self.assertEqual("simple", kind["streaming_mode"])


if __name__ == "__main__":
    import unittest

    unittest.main()

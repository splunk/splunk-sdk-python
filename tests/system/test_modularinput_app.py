#!/usr/bin/env python
#
# Copyright © 2011-2025 Splunk, Inc.
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

from splunklib import results
from tests import testlib
from splunklib.binding import HTTPError


class ModularInput(testlib.SDKTestCase):
    index_name = "test_modular_input"
    input_name = "test_modular_input"
    input_kind = "modularinput"

    def setUp(self):
        super().setUp()

        app_found = False
        for kind in self.service.modular_input_kinds:
            if kind.name == self.input_kind:
                app_found = True

        self.assertTrue(app_found, f"{self.input_kind} modular input not installed")
        self.clean()

    def tearDown(self):
        super().tearDown()
        self.clean()

    def clean(self):
        for input in self.service.inputs:
            if input.name == self.input_name and input.kind == self.input_kind:
                self.service.inputs.delete(self.input_name, self.input_kind)

        for index in self.service.indexes:
            if index.name == self.input_name:
                self.service.indexes.delete(self.input_name)

    def test_modular_input(self):
        self.service.indexes.create(self.index_name)

        self.service.inputs.create(
            self.input_name,
            self.input_kind,
            endpoint="https://example.com/api/endpoint",
            index=self.index_name,
        )

        def query():
            stream = self.service.jobs.oneshot(
                f'search index="{self.index_name}"', output_mode="json"
            )
            reader = results.JSONResultsReader(stream)
            return list(reader)

        # Wait until the modular input is executed by splunk.
        self.assertEventuallyTrue(lambda: len(query()) != 0, timeout=10)

        items = query()
        self.assertTrue(len(items) == 1)
        self.assertEqual(items[0]["_raw"], "example message")

    def test_external_validator(self):
        def create():
            self.service.inputs.create(
                self.input_name,
                self.input_kind,
                endpoint="http://example.com/api/endpoint",
                index=self.index_name,
            )

        self.assertRaisesRegex(HTTPError, "non-supported scheme http", create)


if __name__ == "__main__":
    import unittest

    unittest.main()

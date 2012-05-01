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

import testlib

import splunklib.client as client

class TestCase(testlib.TestCase):
    def check_message(self, message):
        self.check_entity(message)

    def test_read(self):
        service = client.connect(**self.opts.kwargs)

        for message in service.messages:
            self.check_message(message)
            message.refresh()
            self.check_message(message)

    def test_crud(self):
        service = client.connect(**self.opts.kwargs)

        messages = service.messages

        if messages.contains('sdk-test-message1'):
            messages.delete('sdk-test-message1')
        if messages.contains('sdk-test-message2'):
            messages.delete('sdk-test-message2')
        self.assertFalse(messages.contains('sdk-test-message1'))
        self.assertFalse(messages.contains('sdk-test-message2'))

        messages.create('sdk-test-message1', value="Hello!")
        self.assertTrue(messages.contains('sdk-test-message1'))
        self.assertEqual(messages['sdk-test-message1'].value, "Hello!")

        messages.create('sdk-test-message2', value="World!")
        self.assertTrue(messages.contains('sdk-test-message2'))
        self.assertEqual(messages['sdk-test-message2'].value, "World!")

        messages.delete('sdk-test-message1')
        messages.delete('sdk-test-message2')
        self.assertFalse(messages.contains('sdk-test-message1'))
        self.assertFalse(messages.contains('sdk-test-message2'))

        # Verify that message names with spaces work correctly
        if messages.contains('sdk test message'):
            messages.delete('sdk test message')
        self.assertFalse(messages.contains('sdk test message'))
        messages.create('sdk test message', value="xyzzy")
        self.assertTrue(messages.contains('sdk test message'))
        self.assertEqual(messages['sdk test message'].value, "xyzzy")
        messages.delete('sdk test message')
        self.assertFalse(messages.contains('sdk test message'))

        # Verify that create raises a ValueError on invalid name args
        with self.assertRaises(ValueError):
            messages.create(None, value="What?")
            messages.create(42, value="Who, me?")
            messages.create([1, 2,  3], value="Who, me?")

if __name__ == "__main__":
    testlib.main()

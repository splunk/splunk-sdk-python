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

import splunklib.client as client

class MessageTest(testlib.SDKTestCase):
    def setUp(self):
        testlib.SDKTestCase.setUp(self)
        self.message_name = testlib.tmpname()
        self.message = self.service.messages.create(
            self.message_name,
            value='Test message created by the SDK')

    def tearDown(self):
        testlib.SDKTestCase.tearDown(self)
        self.service.messages.delete(self.message_name)

class TestCreateDelete(testlib.SDKTestCase):
    def test_create_delete(self):
        message_name = testlib.tmpname()
        message_value = 'Test message'
        message = self.service.messages.create(
            message_name, value=message_value)
        self.assertTrue(message_name in self.service.messages)
        self.assertEqual(message.value, message_value)
        self.check_entity(message)
        self.service.messages.delete(message_name)
        self.assertFalse(message_name in self.service.messages)

    def test_invalid_name(self):
        self.assertRaises(client.InvalidNameException, self.service.messages.create, None, value="What?")
        self.assertRaises(client.InvalidNameException, self.service.messages.create, 42, value="Who, me?")
        self.assertRaises(client.InvalidNameException, self.service.messages.create, [1,2,3], value="Who, me?")

if __name__ == "__main__":
    try:
        import unittest2 as unittest
    except ImportError:
        import unittest
    unittest.main()

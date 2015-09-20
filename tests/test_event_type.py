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
import logging

import splunklib.client as client

class TestRead(testlib.SDKTestCase):
    def test_read(self):
        for event_type in self.service.event_types.list(count=1):
            self.check_entity(event_type)

class TestCreate(testlib.SDKTestCase):
    def test_create(self):
        self.event_type_name = testlib.tmpname()
        event_types = self.service.event_types
        self.assertFalse(self.event_type_name in event_types)

        kwargs = {}
        kwargs['search'] = "index=_internal *"
        kwargs['description'] = "An internal event"
        kwargs['disabled'] = 1
        kwargs['priority'] = 2

        event_type = event_types.create(self.event_type_name, **kwargs)
        self.assertTrue(self.event_type_name in event_types)
        self.assertEqual(self.event_type_name, event_type.name)

    def tearDown(self):
        super(TestCreate, self).setUp()
        try:
            self.service.event_types.delete(self.event_type_name)
        except KeyError:
            pass

class TestEventType(testlib.SDKTestCase):
    def setUp(self):
        super(TestEventType, self).setUp()
        self.event_type_name = testlib.tmpname()
        self.event_type = self.service.event_types.create(
            self.event_type_name,
            search="index=_internal *")

    def tearDown(self):
        super(TestEventType, self).setUp()
        try:
            self.service.event_types.delete(self.event_type_name)
        except KeyError:
            pass

    def test_delete(self):
        self.assertTrue(self.event_type_name in self.service.event_types)
        self.service.event_types.delete(self.event_type_name)
        self.assertFalse(self.event_type_name in self.service.event_types)

    def test_update(self):
        kwargs = {}
        kwargs['search'] = "index=_audit *"
        kwargs['description'] = "An audit event"
        kwargs['priority'] = '3'
        self.event_type.update(**kwargs)
        self.event_type.refresh()
        self.assertEqual(self.event_type['search'], kwargs['search'])
        self.assertEqual(self.event_type['description'], kwargs['description'])
        self.assertEqual(self.event_type['priority'], kwargs['priority'])
                         
    def test_enable_disable(self):
        self.assertEqual(self.event_type['disabled'], '0')
        self.event_type.disable()
        self.event_type.refresh()
        self.assertEqual(self.event_type['disabled'], '1')
        self.event_type.enable()
        self.event_type.refresh()
        self.assertEqual(self.event_type['disabled'], '0')

if __name__ == "__main__":
    try:
        import unittest2 as unittest
    except ImportError:
        import unittest
    unittest.main()

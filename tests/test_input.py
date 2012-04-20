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

import splunklib.client as client

import testlib

class TestCase(testlib.TestCase):
    def check_input(self, entity):
        self.check_entity(entity)

        self.assertTrue(entity.kind is not None)

        # Note: The disabled flag appears to be the only common content
        # attribute, as there are apparently cases where even index does 
        # not appear.
        entity.content.disabled

        if entity.kind == "ad":
            entity.content.monitorSubtree
            return
            
        if entity.kind == "monitor":
            return

        if entity.kind == "registry":
            entity.content.baseline
            entity.content.proc
            entity.content.hive
            entity.content.index
            return

        if entity.kind == "script":
            entity.content._rcvbuf
            entity.content.index
            entity.content.interval
            return

        if entity.kind == "tcp":
            entity.content._rcvbuf
            entity.content.group
            return

        if entity.kind == "splunktcp":
            entity.content._rcvbuf
            entity.content.group
            entity.content.host
            entity.content.index
            return

        if entity.kind == "udp":
            entity.content._rcvbuf
            entity.content.group
            entity.content.host
            entity.content.index
            return

        if entity.kind == "win-event-log-collections":
            entity.content.lookup_host
            entity.content.name
            return

        if entity.kind == "win-perfmon":
            entity.content.interval
            entity.content.object
            return

        if entity.kind == "win-wmi-collections":
            entity.content.classes
            entity.content.interval
            entity.content.lookup_host
            entity.content.wql
            return

        self.fail("Unknown input kind: '%s'" % entity.kind)

    def test_read(self):
        service = client.connect(**self.opts.kwargs)

        inputs = service.inputs

        for item in inputs: 
            self.check_input(item)
            item.refresh()
            self.check_input(item)

        for kind in inputs.kinds:
            for item in inputs.list(kind):
                self.assertEqual(item.kind, kind)

    def test_crud(self):
        service = client.connect(**self.opts.kwargs)

        inputs = service.inputs

        if inputs.contains('9999'): inputs.delete('9999')
        self.assertFalse(inputs.contains('9999'))
        inputs.create("tcp", "9999", host="sdk-test")
        self.assertTrue(inputs.contains('9999'))
        input_ = inputs['9999']
        self.assertEqual(input_.kind, "tcp")
        self.assertEqual(input_['host'], "sdk-test")
        input_.update(host="foo", sourcetype="bar")
        input_.refresh()
        self.assertEqual(input_['host'], "foo")
        self.assertEqual(input_['sourcetype'], "bar")
        inputs.delete('9999')
        self.assertFalse(inputs.contains('9999'))

if __name__ == "__main__":
    testlib.main()

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

    def test_crud(self):
        service = client.connect(**self.opts.kwargs)

        self.assertTrue('props' in service.confs)
        props = service.confs['props']

        if 'sdk-tests' in props: props.delete('sdk-tests')
        self.assertFalse('sdk-tests' in props)

        stanza = props.create('sdk-tests')
        self.assertTrue(props.contains('sdk-tests'))
        self.assertEqual(stanza.name,'sdk-tests')
        self.assertTrue('maxDist' in stanza.content)
        value = int(stanza['maxDist'])
        stanza.update(maxDist=value+1)
        stanza.refresh()
        self.assertEqual(stanza['maxDist'], str(value + 1))
        stanza.update(maxDist=value)
        stanza.refresh()
        self.assertEqual(stanza['maxDist'], str(value))

        props.delete('sdk-tests')
        self.assertFalse(props.contains('sdk-tests')) 

    def test_read(self):
        service = client.connect(**self.opts.kwargs)

        confs = service.confs

        # Make sure the collection contains some of the expected entries
        self.assertTrue('eventtypes' in confs)
        self.assertTrue('indexes' in confs)
        self.assertTrue('inputs' in confs)
        self.assertTrue('props' in confs)
        self.assertTrue('transforms' in confs)
        self.assertTrue('savedsearches' in confs)

        for conf in confs:
            conf.name
            conf.path
            for stanza in conf: 
                stanza.name
                stanza.path
                stanza.content
                stanza.metadata

if __name__ == "__main__":
    testlib.main()

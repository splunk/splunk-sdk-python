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

import sys
from os import path
import xml.etree.ElementTree as et

import testlib

import splunklib.data as data

class DataTestCase(testlib.SDKTestCase):
    def test_elems(self):
        result = data.load("")
        self.assertTrue(result is None)

        result = data.load("<a></a>")
        self.assertEqual(result, {'a': None})

        result = data.load("<a>1</a>")
        self.assertEqual(result, {'a': "1"})

        result = data.load("<a><b></b></a>")
        self.assertEqual(result, {'a': {'b': None}})

        result = data.load("<a><b>1</b></a>")
        self.assertEqual(result, {'a': {'b': '1'}})

        result = data.load("<a><b></b><b></b></a>")
        self.assertEqual(result, {'a': {'b': [None, None]}})

        result = data.load("<a><b>1</b><b>2</b></a>")
        self.assertEqual(result, {'a': {'b': ['1', '2']}})

        result = data.load("<a><b></b><c></c></a>")
        self.assertEqual(result, {'a': {'b': None, 'c': None}})

        result = data.load("<a><b>1</b><c>2</c></a>")
        self.assertEqual(result, {'a': {'b': '1', 'c': '2'}})

        result = data.load("<a><b><c>1</c></b></a>")
        self.assertEqual(result, {'a': {'b': {'c': '1'}}})

        result = data.load("<a><b><c>1</c></b><b>2</b></a>")
        self.assertEqual(result, {'a': {'b': [{'c': '1'}, '2']}})

        result = data.load('<e><a1>alpha</a1><a1>beta</a1></e>')
        self.assertEqual(result, {'e': {'a1': ['alpha', 'beta']}})

        result = data.load("<e a1='v1'><a1>v2</a1></e>")
        self.assertEqual(result, {'e': {'a1': ['v2', 'v1']}})

    def test_attrs(self):
        result = data.load("<e a1='v1'/>")
        self.assertEqual(result, {'e': {'a1': 'v1'}})

        result = data.load("<e a1='v1' a2='v2'/>")
        self.assertEqual(result, {'e': {'a1': 'v1', 'a2': 'v2'}})

        result = data.load("<e a1='v1'>v2</e>")
        self.assertEqual(result, {'e': {'$text': 'v2', 'a1': 'v1'}})

        result = data.load("<e a1='v1'><b>2</b></e>")
        self.assertEqual(result, {'e': {'a1': 'v1', 'b': '2'}})

        result = data.load("<e a1='v1'>v2<b>bv2</b></e>")
        self.assertEqual(result, {'e': {'a1': 'v1', 'b': 'bv2'}})

        result = data.load("<e a1='v1'><a1>v2</a1></e>")
        self.assertEqual(result, {'e': {'a1': ['v2', 'v1']}})

        result = data.load("<e1 a1='v1'><e2 a1='v1'>v2</e2></e1>")
        self.assertEqual(result,
            {'e1': {'a1': 'v1', 'e2': {'$text': 'v2', 'a1': 'v1'}}})

    def test_real(self):
        """Test some real Splunk response examples."""
        testpath = path.dirname(path.abspath(__file__))

        fh = open(path.join(testpath, "data/services.xml"), 'r')
        result = data.load(fh.read())
        self.assertTrue(result.has_key('feed'))
        self.assertTrue(result.feed.has_key('author'))
        self.assertTrue(result.feed.has_key('entry'))
        titles = [item.title for item in result.feed.entry]
        self.assertEqual(
            titles,
            ['alerts', 'apps', 'authentication', 'authorization', 'data',
             'deployment', 'licenser', 'messages', 'configs', 'saved',
             'scheduled', 'search', 'server', 'streams', 'broker', 'clustering',
             'masterlm'])

        fh = open(path.join(testpath, "data/services.server.info.xml"), 'r')
        result = data.load(fh.read())
        self.assertTrue(result.has_key('feed'))
        self.assertTrue(result.feed.has_key('author'))
        self.assertTrue(result.feed.has_key('entry'))
        self.assertEqual(result.feed.title, 'server-info')
        self.assertEqual(result.feed.author.name, 'Splunk')
        self.assertEqual(result.feed.entry.content.cpu_arch, 'i386')
        self.assertEqual(result.feed.entry.content.os_name, 'Darwin')
        self.assertEqual(result.feed.entry.content.os_version, '10.8.0')

    def test_invalid(self):
        if sys.version_info[1] >= 7:
            self.assertRaises(et.ParseError, data.load, "<dict</dict>")
        else:
            from xml.parsers.expat import ExpatError
            self.assertRaises(ExpatError, data.load, "<dict</dict>")
            
        self.assertRaises(KeyError, data.load, "<dict><key>a</key></dict>")

    def test_dict(self):
        result = data.load("""
            <dict></dict>
        """)
        self.assertEqual(result, {})

        result = data.load("""
            <dict>
              <key name='n1'>v1</key>
              <key name='n2'>v2</key>
            </dict>""")
        self.assertEqual(result, {'n1': "v1", 'n2': "v2"})

        result = data.load("""
            <content>
              <dict>
                <key name='n1'>v1</key>
                <key name='n2'>v2</key>
              </dict>
            </content>""")
        self.assertEqual(result, {'content': {'n1': "v1", 'n2': "v2"}})

        result = data.load("""
            <content>
              <dict>
                <key name='n1'>
                  <dict>
                    <key name='n1n1'>n1v1</key>
                  </dict>
                </key>
                <key name='n2'>
                  <dict>
                    <key name='n2n1'>n2v1</key>
                  </dict>
                </key>
              </dict>
            </content>""")
        self.assertEqual(result, 
            {'content': {'n1': {'n1n1': "n1v1"}, 'n2': {'n2n1': "n2v1"}}})

        result = data.load("""
            <content>
              <dict>
                <key name='n1'>
                  <list>
                    <item>1</item><item>2</item><item>3</item><item>4</item>
                  </list>
                </key>
              </dict>
            </content>""")
        self.assertEqual(result, 
            {'content': {'n1': ['1', '2', '3', '4']}})

    def test_list(self):
        result = data.load("""<list></list>""")
        self.assertEqual(result, [])

        result = data.load("""
            <list>
              <item>1</item><item>2</item><item>3</item><item>4</item>
            </list>""")
        self.assertEqual(result, ['1', '2', '3', '4'])

        result = data.load("""
            <content>
              <list>
                <item>1</item><item>2</item><item>3</item><item>4</item>
              </list>
            </content>""")
        self.assertEqual(result, {'content': ['1', '2', '3', '4']})

        result = data.load("""
            <content>
              <list>
                <item>
                  <list><item>1</item><item>2</item></list>
                </item>
                <item>
                  <list><item>3</item><item>4</item></list>
                </item>
              </list>
            </content>""")
        self.assertEqual(result, {'content': [['1', '2'], ['3', '4']]})

        result = data.load("""
            <content>
              <list>
                <item><dict><key name='n1'>v1</key></dict></item>
                <item><dict><key name='n2'>v2</key></dict></item>
                <item><dict><key name='n3'>v3</key></dict></item>
                <item><dict><key name='n4'>v4</key></dict></item>
              </list>
            </content>""")
        self.assertEqual(result, 
            {'content': [{'n1':"v1"}, {'n2':"v2"}, {'n3':"v3"}, {'n4':"v4"}]})

        result = data.load("""
        <ns1:dict xmlns:ns1="http://dev.splunk.com/ns/rest">
            <ns1:key name="build">101089</ns1:key>
            <ns1:key name="cpu_arch">i386</ns1:key>
            <ns1:key name="isFree">0</ns1:key>
        </ns1:dict>
        """)
        self.assertEqual(result,
        {'build': '101089', 'cpu_arch': 'i386', 'isFree': '0'})

    def test_record(self):
        d = data.record()
        d.update({'foo': 5,
                  'bar.baz': 6,
                  'bar.qux': 7,
                  'bar.zrp.meep': 8,
                  'bar.zrp.peem': 9})
        self.assertEqual(d['foo'], 5)
        self.assertEqual(d['bar.baz'], 6)
        self.assertEqual(d['bar'], {'baz': 6, 'qux': 7, 'zrp': {'meep': 8, 'peem':9}})
        self.assertEqual(d.foo, 5)
        self.assertEqual(d.bar.baz, 6)
        self.assertEqual(d.bar, {'baz': 6, 'qux': 7, 'zrp': {'meep': 8, 'peem':9}})
        self.assertRaises(KeyError, d.__getitem__, 'boris')


if __name__ == "__main__":
    try:
        import unittest2 as unittest
    except ImportError:
        import unittest
    unittest.main()


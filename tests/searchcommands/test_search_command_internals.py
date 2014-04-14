#!/usr/bin/env python
#
# Copyright 2011-2014 Splunk, Inc.
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

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from splunklib.searchcommands import Configuration, Option, ReportingCommand, StreamingCommand, validators
from splunklib.searchcommands import search_command_internals
from cStringIO import StringIO
from contextlib import closing
from itertools import izip
from json import JSONEncoder

import os


@Configuration()
class StubbedReportingCommand(ReportingCommand):
    boolean = Option(
        doc='''
        **Syntax:** **boolean=***<value>*
        **Description:** A boolean value''',
        require=False, validate=validators.Boolean())

    duration = Option(
        doc='''
        **Syntax:** **duration=***<value>*
        **Description:** A length of time''',
        validate=validators.Duration())

    fieldname = Option(
        doc='''
        **Syntax:** **fieldname=***<value>*
        **Description:** Name of a field''',
        validate=validators.Fieldname())

    file = Option(
        doc='''
        **Syntax:** **file=***<value>*
        **Description:** Name of a file''',
        validate=validators.File(mode='r'))

    integer = Option(
        doc='''
        **Syntax:** **integer=***<value>*
        **Description:** An integer value''',
        validate=validators.Integer())

    optionname = Option(
        doc='''
        **Syntax:** **optionname=***<value>*
        **Description:** The name of an option (used internally)''',
        validate=validators.OptionName())

    regularexpression = Option(
        doc='''
        **Syntax:** **regularexpression=***<value>*
        **Description:** Regular expression pattern to match''',
        validate=validators.RegularExpression())

    set = Option(
        doc='''
        **Syntax:** **set=***<value>*
        **Description:** Regular expression pattern to match''',
        validate=validators.Set("foo", "bar", "test"))

    @Configuration()
    def map(self, records):
        pass

    def reduce(self, records):
        pass


@Configuration()
class StubbedStreamingCommand(StreamingCommand):
    boolean = Option(
        doc='''
        **Syntax:** **boolean=***<value>*
        **Description:** A boolean value''',
        require=True, validate=validators.Boolean())

    duration = Option(
        doc='''
        **Syntax:** **duration=***<value>*
        **Description:** A length of time''',
        require=True, validate=validators.Duration())

    fieldname = Option(
        doc='''
        **Syntax:** **fieldname=***<value>*
        **Description:** Name of a field''',
        require=True, validate=validators.Fieldname())

    file = Option(
        doc='''
        **Syntax:** **file=***<value>*
        **Description:** Name of a file''',
        require=True, validate=validators.File(mode='r'))

    integer = Option(
        doc='''
        **Syntax:** **integer=***<value>*
        **Description:** An integer value''',
        require=True, validate=validators.Integer())

    optionname = Option(
        doc='''
        **Syntax:** **optionname=***<value>*
        **Description:** The name of an option (used internally)''',
        require=True, validate=validators.OptionName())

    regularexpression = Option(
        doc='''
        **Syntax:** **regularexpression=***<value>*
        **Description:** Regular expression pattern to match''',
        require=True, validate=validators.RegularExpression())

    set = Option(
        doc='''
        **Syntax:** **set=***<value>*
        **Description:** Regular expression pattern to match''',
        require=True, validate=validators.Set("foo", "bar", "test"))

    def stream(self, records):
        pass


class TestSearchCommandInternals(unittest.TestCase):

    def setUp(self):
        super(TestSearchCommandInternals, self).setUp()
        return

    def test_command_parser(self):

        parser = search_command_internals.SearchCommandParser()
        encoder = JSONEncoder()
        file_path = os.path.abspath(os.path.join(TestSearchCommandInternals._package_path, 'data', 'input', '_empty.csv'))

        options = [
            'boolean=true',
            'duration=00:00:10',
            'fieldname=word_count',
            'file=%s' % encoder.encode(file_path),
            'integer=10',
            'optionname=foo_bar',
            'regularexpression="\\\\w+"',
            'set=foo']

        fields = ['field_1', 'field_2', 'field_3']

        command = StubbedStreamingCommand()  # All options except for the builtin options are required
        parser.parse(options + fields, command)
        command_line = str(command)

        self.assertEqual(
            'stubbedstreaming boolean=true duration=10 fieldname="word_count" file=%s integer=10 optionname="foo_bar" regularexpression="\\\\w+" set="foo" field_1 field_2 field_3' % encoder.encode(file_path),
            command_line)

        for option in options:
            self.assertRaises(ValueError, parser.parse, [x for x in options if x != option] + ['field_1', 'field_2', 'field_3'], command)

        command = StubbedReportingCommand()  # No options are required
        parser.parse(options + fields, command)

        for option in options:
            try:
                parser.parse([x for x in options if x != option] + ['field_1', 'field_2', 'field_3'], command)
            except Exception as e:
                self.assertFalse("Unexpected exception: %s" % e)

        try:
            parser.parse(options, command)
        except Exception as e:
            self.assertFalse("Unexpected exception: %s" % e)

        for option in command.options.itervalues():
            if option.name in ['show_configuration', 'logging_configuration', 'logging_level']:
                continue
            self.assertTrue(option.is_set)

        self.assertEqual(len(command.fieldnames), 0)

        try:
            parser.parse(fields, command)
        except Exception as e:
            self.assertFalse("Unexpected exception: %s" % e)

        for option in command.options.itervalues():
            self.assertFalse(option.is_set)

        self.assertListEqual(fields, command.fieldnames)
        return

    def test_input_header(self):

        # No items

        input_header = search_command_internals.InputHeader()

        with closing(StringIO('\r\n')) as input_file:
            input_header.read(input_file)

        self.assertEquals(len(input_header), 0)

        # One unnamed single-line item (same as no items)

        input_header = search_command_internals.InputHeader()

        with closing(StringIO('this%20is%20an%20unnamed%20single-line%20item\n\n')) as input_file:
            input_header.read(input_file)

        self.assertEquals(len(input_header), 0)

        input_header = search_command_internals.InputHeader()

        with closing(StringIO('this%20is%20an%20unnamed\nmulti-\nline%20item\n\n')) as input_file:
            input_header.read(input_file)

        self.assertEquals(len(input_header), 0)

        # One named single-line item

        input_header = search_command_internals.InputHeader()

        with closing(StringIO('Foo:this%20is%20a%20single-line%20item\n\n')) as input_file:
            input_header.read(input_file)

        self.assertEquals(len(input_header), 1)
        self.assertEquals(input_header['Foo'], 'this is a single-line item')

        input_header = search_command_internals.InputHeader()

        with closing(StringIO('Bar:this is a\nmulti-\nline item\n\n')) as input_file:
            input_header.read(input_file)

        self.assertEquals(len(input_header), 1)
        self.assertEquals(input_header['Bar'], 'this is a\nmulti-\nline item')

        # The infoPath item (which is the path to a file that we open for reads)

        input_header = search_command_internals.InputHeader()

        with closing(StringIO('infoPath:data/input/_empty.csv\n\n')) as input_file:
            input_header.read(input_file)

        self.assertEquals(len(input_header), 1)
        self.assertEqual(input_header['infoPath'], 'data/input/_empty.csv')

        # Set of named items

        collection = {
            'word_list': 'hello\nworld\n!',
            'word_1': 'hello',
            'word_2': 'world',
            'word_3': '!',
            'sentence': 'hello world!'}

        input_header = search_command_internals.InputHeader()
        text = reduce(lambda value, item: value + '%s:%s\n' % (item[0], item[1]), collection.iteritems(), '') + '\n'

        with closing(StringIO(text)) as input_file:
            input_header.read(input_file)

        self.assertEqual(len(input_header), len(collection))

        for key, value in input_header.iteritems():
            self.assertEqual(value, collection[key])

        # Set of named items with an unnamed item at the beginning (the only
        # place that an unnamed item can appear)

        with closing(StringIO('unnamed item\n' + text)) as input_file:
            input_header.read(input_file)

        self.assertEqual(len(input_header), len(collection))

        # Test iterators, indirectly through items, keys, and values

        self.assertEqual(sorted(input_header.items()), sorted(collection.items()))
        self.assertEqual(sorted(input_header.keys()), sorted(collection.keys()))
        self.assertEqual(sorted(input_header.values()), sorted(collection.values()))

        return

    def test_messages_header(self):

        messages_header = search_command_internals.MessagesHeader()
        self.assertEqual(len(messages_header), 0)

        messages = [
            ('info_message', 'some information message'),
            ('warn_message', 'some warning message'),
            ('error_message', 'some error message'),
            ('debug_message', 'some debug message')]

        for message in messages:
            messages_header += message

        self.assertEqual(len(messages_header), len(messages))

        for message in izip(messages_header, messages):
            self.assertEqual(message[0], message[1])

        for message_level, message_text in messages:
            messages_header.append(message_level, message_text)

        self.assertEqual(len(messages_header), 2 * len(messages))

        for message in izip(messages_header, messages + messages):
            self.assertEqual(message[0], message[1])

        self.assertEqual(repr(messages_header), "MessagesHeader(%s)" % repr(messages + messages))

        self.assertRaises(ValueError, messages_header.append, "not_a_debug_info_warn_or_error_message", "foo bar")

        return

    _package_path = os.path.dirname(__file__)

if __name__ == "__main__":
    unittest.main()

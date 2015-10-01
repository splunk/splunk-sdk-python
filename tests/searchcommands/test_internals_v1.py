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

from __future__ import absolute_import, division, print_function, unicode_literals

from splunklib.searchcommands.internals import CommandLineParser, InputHeader, RecordWriterV1
from splunklib.searchcommands.decorators import Configuration, Option
from splunklib.searchcommands.validators import Boolean

from splunklib.searchcommands.search_command import SearchCommand

from contextlib import closing
from cStringIO import StringIO
from itertools import izip
from unittest import main, TestCase

import os


class TestInternals(TestCase):
    def setUp(self):
        TestCase.setUp(self)

    def test_command_line_parser(self):

        @Configuration()
        class TestCommandLineParserCommand(SearchCommand):

            required_option = Option(validate=Boolean(), require=True)
            unnecessary_option = Option(validate=Boolean(), default=True, require=False)

            class ConfigurationSettings(SearchCommand.ConfigurationSettings):

                @classmethod
                def fix_up(cls, command_class): pass

        # Command line without fieldnames

        options = ['required_option=true', 'unnecessary_option=false']

        command = TestCommandLineParserCommand()
        CommandLineParser.parse(command, options)

        for option in command.options.itervalues():
            if option.name in ['logging_configuration', 'logging_level', 'record', 'show_configuration']:
                self.assertFalse(option.is_set)
                continue
            self.assertTrue(option.is_set)

        expected = 'testcommandlineparser required_option="t" unnecessary_option="f"'
        self.assertEqual(expected, str(command))
        self.assertEqual(command.fieldnames, [])

        # Command line with fieldnames

        fieldnames = ['field_1', 'field_2', 'field_3']

        command = TestCommandLineParserCommand()
        CommandLineParser.parse(command, options + fieldnames)

        for option in command.options.itervalues():
            if option.name in ['logging_configuration', 'logging_level', 'record', 'show_configuration']:
                self.assertFalse(option.is_set)
                continue
            self.assertTrue(option.is_set)

        expected = 'testcommandlineparser required_option="t" unnecessary_option="f" field_1 field_2 field_3'
        self.assertEqual(expected, str(command))
        self.assertEquals(command.fieldnames, fieldnames)

        # Command line without any unnecessary options

        command = TestCommandLineParserCommand()
        CommandLineParser.parse(command, ['required_option=true'] + fieldnames)

        for option in command.options.itervalues():
            if option.name in ['unnecessary_option', 'logging_configuration', 'logging_level', 'record', 'show_configuration']:
                self.assertFalse(option.is_set)
                continue
            self.assertTrue(option.is_set)

        expected = 'testcommandlineparser required_option="t" field_1 field_2 field_3'
        self.assertEqual(expected, str(command))
        self.assertEquals(command.fieldnames, fieldnames)

        # Command line with missing required options, with or without fieldnames or unnecessary options

        options = ['unnecessary_option=true']
        self.assertRaises(ValueError, CommandLineParser.parse, command, options + fieldnames)
        self.assertRaises(ValueError, CommandLineParser.parse, command, options)
        self.assertRaises(ValueError, CommandLineParser.parse, command, [])

        # Command line with unrecognized options

        self.assertRaises(ValueError, CommandLineParser.parse, command, ['unrecognized_option_1=foo', 'unrecognized_option_2=bar'])

        # Command line with a variety of quoted/escaped text options

        @Configuration()
        class TestCommandLineParserCommand(SearchCommand):

            text = Option()

            class ConfigurationSettings(SearchCommand.ConfigurationSettings):

                @classmethod
                def fix_up(cls, command_class): pass

        strings = [
            r'"foo bar"',
            r'"foo/bar"',
            r'"foo\\bar"',
            r'"""foo bar"""',
            r'"\"foo bar\""',
            r'Hello\ World!',
            r'\"Hello\ World!\"']

        expected_values = [
            r'foo bar',
            r'foo/bar',
            r'foo\bar',
            r'"foo bar"',
            r'"foo bar"',
            r'Hello World!',
            r'"Hello World!"'
        ]

        for string, expected_value in izip(strings, expected_values):
            command = TestCommandLineParserCommand()
            argv = ['text', '=', string]
            CommandLineParser.parse(command, argv)
            self.assertEqual(command.text, expected_value)

        for string, expected_value in izip(strings, expected_values):
            command = TestCommandLineParserCommand()
            argv = [string]
            CommandLineParser.parse(command, argv)
            self.assertEqual(command.fieldnames[0], expected_value)

        for string, expected_value in izip(strings, expected_values):
            command = TestCommandLineParserCommand()
            argv = ['text', '=', string] + strings
            CommandLineParser.parse(command, argv)
            self.assertEqual(command.text, expected_value)
            self.assertEqual(command.fieldnames, expected_values)

        strings = [
            'some\\ string\\',
            r'some\ string"',
            r'"some string',
            r'some"string'
        ]

        for string in strings:
            command = TestCommandLineParserCommand()
            argv = [string]
            self.assertRaises(SyntaxError, CommandLineParser.parse, command, argv)

        return

    def test_command_line_parser_unquote(self):
        parser = CommandLineParser

        options = [
            r'foo',                 # unquoted string with no escaped characters
            r'fo\o\ b\"a\\r',       # unquoted string with some escaped characters
            r'"foo"',               # quoted string with no special characters
            r'"""foobar1"""',       # quoted string with quotes escaped like this: ""
            r'"\"foobar2\""',       # quoted string with quotes escaped like this: \"
            r'"foo ""x"" bar"',     # quoted string with quotes escaped like this: ""
            r'"foo \"x\" bar"',     # quoted string with quotes escaped like this: \"
            r'"\\foobar"',          # quoted string with an escaped backslash
            r'"foo \\ bar"',        # quoted string with an escaped backslash
            r'"foobar\\"',          # quoted string with an escaped backslash
            r'foo\\\bar',           # quoted string with an escaped backslash and an escaped 'b'
            r'""',                  # pair of quotes
            r'']                    # empty string

        expected = [
            r'foo',
            r'foo b"a\r',
            r'foo',
            r'"foobar1"',
            r'"foobar2"',
            r'foo "x" bar',
            r'foo "x" bar',
            '\\foobar',
            r'foo \ bar',
            'foobar\\',
            r'foo\bar',
            r'',
            r'']

        # Command line with an assortment of string values

        self.assertEqual(expected[-4], parser.unquote(options[-4]))

        for i in range(0, len(options)):
            self.assertEqual(expected[i], parser.unquote(options[i]))

        self.assertRaises(SyntaxError, parser.unquote, '"')
        self.assertRaises(SyntaxError, parser.unquote, '"foo')
        self.assertRaises(SyntaxError, parser.unquote, 'foo"')
        self.assertRaises(SyntaxError, parser.unquote, 'foo\\')

    def test_input_header(self):

        # No items

        input_header = InputHeader()

        with closing(StringIO('\r\n'.encode())) as input_file:
            input_header.read(input_file)

        self.assertEquals(len(input_header), 0)

        # One unnamed single-line item (same as no items)

        input_header = InputHeader()

        with closing(StringIO('this%20is%20an%20unnamed%20single-line%20item\n\n'.encode())) as input_file:
            input_header.read(input_file)

        self.assertEquals(len(input_header), 0)

        input_header = InputHeader()

        with closing(StringIO('this%20is%20an%20unnamed\nmulti-\nline%20item\n\n'.encode())) as input_file:
            input_header.read(input_file)

        self.assertEquals(len(input_header), 0)

        # One named single-line item

        input_header = InputHeader()

        with closing(StringIO('Foo:this%20is%20a%20single-line%20item\n\n'.encode())) as input_file:
            input_header.read(input_file)

        self.assertEquals(len(input_header), 1)
        self.assertEquals(input_header['Foo'], 'this is a single-line item')

        input_header = InputHeader()

        with closing(StringIO('Bar:this is a\nmulti-\nline item\n\n'.encode())) as input_file:
            input_header.read(input_file)

        self.assertEquals(len(input_header), 1)
        self.assertEquals(input_header['Bar'], 'this is a\nmulti-\nline item')

        # The infoPath item (which is the path to a file that we open for reads)

        input_header = InputHeader()

        with closing(StringIO('infoPath:non-existent.csv\n\n'.encode())) as input_file:
            input_header.read(input_file)

        self.assertEquals(len(input_header), 1)
        self.assertEqual(input_header['infoPath'], 'non-existent.csv')

        # Set of named items

        collection = {
            'word_list': 'hello\nworld\n!',
            'word_1': 'hello',
            'word_2': 'world',
            'word_3': '!',
            'sentence': 'hello world!'}

        input_header = InputHeader()
        text = reduce(lambda value, item: value + '{}:{}\n'.format(item[0], item[1]), collection.iteritems(), '') + '\n'

        with closing(StringIO(text.encode())) as input_file:
            input_header.read(input_file)

        self.assertDictEqual(input_header, collection)

        # Set of named items with an unnamed item at the beginning (the only place that an unnamed item can appear)

        with closing(StringIO(('unnamed item\n' + text).encode())) as input_file:
            input_header.read(input_file)

        self.assertDictEqual(input_header, collection)

        # Test iterators, indirectly through items, keys, and values

        self.assertEqual(sorted(input_header.items()), sorted(collection.items()))
        self.assertEqual(sorted(input_header.keys()), sorted(collection.keys()))
        self.assertEqual(sorted(input_header.values()), sorted(collection.values()))

        return

    def test_messages_header(self):

        @Configuration()
        class TestMessagesHeaderCommand(SearchCommand):

            class ConfigurationSettings(SearchCommand.ConfigurationSettings):

                @classmethod
                def fix_up(cls, command_class): pass

        command = TestMessagesHeaderCommand()
        command._protocol_version = 1
        output_buffer = StringIO()
        command._record_writer = RecordWriterV1(output_buffer)

        messages = [
            (command.write_debug, 'debug_message'),
            (command.write_error, 'error_message'),
            (command.write_fatal, 'fatal_message'),
            (command.write_info, 'info_message'),
            (command.write_warning, 'warning_message')]

        for write, message in messages:
            write(message)

        command.finish()

        expected = (
            'debug_message=debug_message\r\n'
            'error_message=error_message\r\n'
            'error_message=fatal_message\r\n'
            'info_message=info_message\r\n'
            'warn_message=warning_message\r\n'
            '\r\n')

        self.assertEquals(output_buffer.getvalue(), expected)
        return

    _package_path = os.path.dirname(__file__)


if __name__ == "__main__":
    main()

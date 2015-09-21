#!/usr/bin/env python
# coding=utf-8
#
# Copyright © 2011-2015 Splunk, Inc.
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

# TODO: Fortify command-type specific configuration settings tests
# Example: Test that a ReportingCommand accepts required_fields and serializes it correctly

# TODO: Add SCP1 test for local configuration setting
# Requirements:
# * Value applies to streaming and generating, not to reporting and eventing commands
# * If a value is not set in code, the value specified in commands.conf is enforced
# * If a value is set in code, it overrides the value specified in commands.conf

from __future__ import absolute_import, division, print_function, unicode_literals

from splunklib.searchcommands.decorators import Configuration
from unittest import main, TestCase


class TestConfigurationSettings(TestCase):

    def test_generating_command(self):

        from splunklib.searchcommands import Configuration, GeneratingCommand

        @Configuration()
        class TestCommand(GeneratingCommand):
            def generate(self):
                pass

        command = TestCommand()
        command._protocol_version = 1

        self.assertTrue(
            [(name, value) for name, value in command.configuration.iteritems()],
            [('generates_timeorder', False), ('generating', True), ('retainsevents', False), ('streaming', True)])

        self.assertIs(command.configuration.generates_timeorder, False)
        self.assertIs(command.configuration.generating, True)
        self.assertIs(command.configuration.retainsevents, False)
        self.assertIs(command.configuration.streaming, True)

        command.configuration.generates_timeorder = True
        command.configuration.retainsevents = True
        command.configuration.streaming = True

        try:
            command.configuration.generating = False
        except AttributeError:
            pass
        except Exception as error:
            self.fail('Expected AttributeError, not {}: {}'.format(type(error).__name__, error))
        else:
            self.fail('Expected AttributeError')

        self.assertEqual(
            [(name, value) for name, value in command.configuration.iteritems()],
            [('generates_timeorder', True), ('generating', True), ('local', False), ('retainsevents', True),
             ('streaming', True)])

        command = TestCommand()
        command._protocol_version = 2

        self.assertEqual(
            [(name, value) for name, value in command.configuration.iteritems()],
            [('generating', True), ('type', 'streaming')])

        self.assertIs(command.configuration.distributed, False)
        self.assertIs(command.configuration.generating, True)
        self.assertEqual(command.configuration.type, 'streaming')

        command.configuration.distributed = True

        try:
            command.configuration.generating = False
        except AttributeError:
            pass
        except Exception as error:
            self.fail('Expected AttributeError, not {}: {}'.format(type(error).__name__, error))
        else:
            self.fail('Expected AttributeError')

        self.assertEqual(
            [(name, value) for name, value in command.configuration.iteritems()],
            [('generating', True), ('type', 'stateful')])

        return

    def test_streaming_command(self):

        from splunklib.searchcommands import Configuration, StreamingCommand

        @Configuration()
        class TestCommand(StreamingCommand):
            def stream(self, records):
                pass

        command = TestCommand()

        command._protocol_version = 1

        self.assertEqual(
            [(name, value) for name, value in command.configuration.iteritems()],
            [('local', False), ('streaming', True)])

        self.assertIs(command.configuration.clear_required_fields, False)
        self.assertIs(command.configuration.local, False)
        self.assertIs(command.configuration.overrides_timeorder, None)
        self.assertIs(command.configuration.required_fields, None)
        self.assertIs(command.configuration.streaming, True)

        command.configuration.clear_required_fields = True
        command.configuration.local = True
        command.configuration.overrides_timeorder = True
        command.configuration.required_fields = ['field_1', 'field_2', 'field_3']

        try:
            command.configuration.streaming = False
        except AttributeError:
            pass
        except Exception as error:
            self.fail('Expected AttributeError, not {}: {}'.format(type(error).__name__, error))
        else:
            self.fail('Expected AttributeError')

        self.assertEqual(
            [(name, value) for name, value in command.configuration.iteritems()],
            [('clear_required_fields', True), ('local', True), ('overrides_timeorder', True), ('required_fields', ['field_1', 'field_2', 'field_3']), ('streaming', True)])

        command = TestCommand()
        command._protocol_version = 2

        self.assertEqual(
            [(name, value) for name, value in command.configuration.iteritems()],
            [('type', 'stateful')])

        self.assertIs(command.configuration.distributed, True)
        self.assertEqual(command.configuration.type, 'streaming')

        command.configuration.distributed = False
        command.configuration.required_fields = ['field_1', 'field_2', 'field_3']

        try:
            command.configuration.type = 'eventing'
        except AttributeError:
            pass
        except Exception as error:
            self.fail('Expected AttributeError, not {}: {}'.format(type(error).__name__, error))
        else:
            self.fail('Expected AttributeError')

        self.assertEqual(
            [(name, value) for name, value in command.configuration.iteritems()],
            [('required_fields', ['field_1', 'field_2', 'field_3']), ('type', 'streaming')])

        return

if __name__ == "__main__":
    main()

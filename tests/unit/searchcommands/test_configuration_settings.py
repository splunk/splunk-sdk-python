#!/usr/bin/env python
# coding=utf-8
#
# Copyright © 2011-2024 Splunk, Inc.
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


from unittest import main, TestCase
import pytest
from splunklib.searchcommands.decorators import Configuration



@pytest.mark.smoke
class TestConfigurationSettings(TestCase):

    def test_generating_command(self):

        from splunklib.searchcommands import GeneratingCommand

        @Configuration()
        class TestCommand(GeneratingCommand):
            def generate(self):
                pass

        command = TestCommand()
        command._protocol_version = 1

        self.assertTrue(
            list(command.configuration.items()),
            [('generating', True)])

        self.assertIs(command.configuration.generates_timeorder, None)
        self.assertIs(command.configuration.generating, True)
        self.assertIs(command.configuration.retainsevents, None)
        self.assertIs(command.configuration.streaming, None)

        command.configuration.generates_timeorder = True
        command.configuration.local = True
        command.configuration.retainsevents = True
        command.configuration.streaming = True

        try:
            command.configuration.generating = False
        except AttributeError:
            pass
        except Exception as error:
            self.fail(f'Expected AttributeError, not {type(error).__name__}: {error}')
        else:
            self.fail('Expected AttributeError')

        self.assertEqual(
            list(command.configuration.items()),
            [('generates_timeorder', True), ('generating', True), ('local', True), ('retainsevents', True),
             ('streaming', True)])

        command = TestCommand()
        command._protocol_version = 2

        self.assertEqual(
            list(command.configuration.items()),
            [('generating', True), ('type', 'stateful')])

        self.assertIs(command.configuration.distributed, False)
        self.assertIs(command.configuration.generating, True)
        self.assertEqual(command.configuration.type, 'streaming')

        command.configuration.distributed = True

        try:
            command.configuration.generating = False
        except AttributeError:
            pass
        except Exception as error:
            self.fail(f'Expected AttributeError, not {type(error).__name__}: {error}')
        else:
            self.fail('Expected AttributeError')

        self.assertEqual(
            list(command.configuration.items()),
            [('generating', True), ('type', 'streaming')])

    def test_streaming_command(self):

        from splunklib.searchcommands import StreamingCommand

        @Configuration()
        class TestCommand(StreamingCommand):
            def stream(self, records):
                pass

        command = TestCommand()

        command._protocol_version = 1

        self.assertEqual(
            list(command.configuration.items()),
            [('streaming', True)])

        self.assertIs(command.configuration.clear_required_fields, None)
        self.assertIs(command.configuration.local, None)
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
            self.fail(f'Expected AttributeError, not {type(error).__name__}: {error}')
        else:
            self.fail('Expected AttributeError')

        self.assertEqual(
            list(command.configuration.items()),
            [('clear_required_fields', True), ('local', True), ('overrides_timeorder', True),
             ('required_fields', ['field_1', 'field_2', 'field_3']), ('streaming', True)])

        command = TestCommand()
        command._protocol_version = 2

        self.assertEqual(
            list(command.configuration.items()),
            [('type', 'streaming')])

        self.assertIs(command.configuration.distributed, True)
        self.assertEqual(command.configuration.type, 'streaming')

        command.configuration.distributed = False
        command.configuration.required_fields = ['field_1', 'field_2', 'field_3']

        try:
            command.configuration.type = 'events'
        except AttributeError:
            pass
        except Exception as error:
            self.fail(f'Expected AttributeError, not {type(error).__name__}: {error}')
        else:
            self.fail('Expected AttributeError')

        self.assertEqual(
            list(command.configuration.items()),
            [('required_fields', ['field_1', 'field_2', 'field_3']), ('type', 'stateful')])


if __name__ == "__main__":
    main()

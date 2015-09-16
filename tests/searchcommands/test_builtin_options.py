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

from __future__ import absolute_import, division, print_function, unicode_literals

from cStringIO import StringIO
from unittest import main, TestCase

import os
import sys
import logging

from splunklib.searchcommands import environment
from splunklib.searchcommands.decorators import Configuration
from splunklib.searchcommands.search_command import SearchCommand

from tests.searchcommands import package_directory, rebase_environment


@Configuration()
class StubbedSearchCommand(SearchCommand):
    class ConfigurationSettings(SearchCommand.ConfigurationSettings):
        @classmethod
        def fix_up(cls, command_class):
            pass


class TestBuiltinOptions(TestCase):

    def setUp(self):
        TestCase.setUp(self)

    def test_logging_configuration(self):

        # Test that logging is properly initialized when there is no logging configuration file

        rebase_environment('app_without_logging_configuration')

        self.assertIsInstance(environment.splunklib_logger, logging.Logger)
        self.assertIsNone(environment.logging_configuration)
        self.assertEqual(len(logging.root.handlers), 1)
        self.assertEqual(len(logging.Logger.manager.loggerDict), 1)
        self.assertIsInstance(logging.root.handlers[0], logging.StreamHandler)
        self.assertIs(environment.splunklib_logger, logging.getLogger('splunklib'))
        self.assertIsNone(environment.logging_configuration)

        command = StubbedSearchCommand()

        self.assertIs(command.logger, logging.getLogger('StubbedSearchCommand'))
        self.assertEqual(len(command.logger.handlers), 0)
        self.assertIsNone(command.logging_configuration)
        self.assertIs(command.logger.root, logging.root)
        self.assertEqual(len(logging.root.handlers), 1)

        root_handler = logging.root.handlers[0]

        self.assertIsInstance(root_handler, logging.StreamHandler)
        self.assertEqual(root_handler.stream, sys.stderr)

        self.assertEqual(command.logging_level, logging.getLevelName(logging.WARNING))
        root_handler.stream = StringIO()
        message = 'Test that output is directed to stderr without formatting'
        command.logger.warning(message)
        self.assertEqual(root_handler.stream.getvalue(), message + '\n')

        # A search command loads {local,default}/logging.conf when it is available

        rebase_environment('app_with_logging_configuration')

        command = StubbedSearchCommand()
        self.assertEqual(command.logging_configuration, os.path.join(environment.app_root, 'default', 'logging.conf'))
        self.assertIs(command.logger, logging.getLogger('StubbedSearchCommand'))

        # Setting logging_configuration loads a new logging configuration file relative to the app root

        command.logging_configuration = 'alternative-logging.conf'
        self.assertEqual(
            command.logging_configuration, os.path.join(environment.app_root, 'default', 'alternative-logging.conf'))
        self.assertIs(command.logger, logging.getLogger('StubbedSearchCommand'))

        # Setting logging_configuration loads a new logging configuration file on an absolute path

        app_root_logging_configuration = os.path.join(environment.app_root, 'logging.conf')
        command.logging_configuration = app_root_logging_configuration

        self.assertEqual(command.logging_configuration, app_root_logging_configuration)
        self.assertIs(command.logger, logging.getLogger('StubbedSearchCommand'))

        # logging_configuration raises a value error, if a non-existent logging configuration file is provided

        try:
            command.logging_configuration = 'foo'
        except ValueError:
            pass
        except BaseException as e:
            self.fail('Expected ValueError, but {} was raised'.format(type(e)))
        else:
            self.fail('Expected ValueError, but logging_configuration={}'.format(command.logging_configuration))

        try:
            command.logging_configuration = os.path.join(package_directory, 'non-existent.logging.conf')
        except ValueError:
            pass
        except BaseException as e:
            self.fail('Expected ValueError, but {} was raised'.format(type(e)))
        else:
            self.fail('Expected ValueError, but logging_configuration={}'.format(command.logging_configuration))

    def test_logging_level(self):

        rebase_environment('app_without_logging_configuration')
        command = StubbedSearchCommand()

        warning = logging.getLevelName(logging.WARNING)
        notset = logging.getLevelName(logging.NOTSET)
        logging.root.setLevel(logging.WARNING)

        self.assertEqual(command.logging_level, warning)

        # logging_level accepts all logging levels and returns their canonical string values

        self.assertEquals(warning, command.logging_level)

        for level in logging._levelNames:
            if type(level) is int:
                command.logging_level = level
                level_name = logging.getLevelName(level)
                self.assertEquals(command.logging_level, warning if level_name == notset else level_name)
            else:
                level_name = logging.getLevelName(logging.getLevelName(level))
                for variant in level, level.lower(), level.capitalize():
                    command.logging_level = variant
                    self.assertEquals(command.logging_level, warning if level_name == notset else level_name)

        # logging_level accepts any numeric value

        for level in 999, 999.999:
            command.logging_level = level
            self.assertEqual(command.logging_level, 'Level 999')

        # logging_level raises a value error for unknown logging level names

        current_value = command.logging_level

        try:
            command.logging_level = 'foo'
        except ValueError:
            pass
        except BaseException as e:
            self.fail('Expected ValueError, but {} was raised'.format(type(e)))
        else:
            self.fail('Expected ValueError, but logging_level={}'.format(command.logging_level))

        self.assertEqual(command.logging_level, current_value)

    def test_record(self):
        self._test_boolean_option(StubbedSearchCommand.record)

    def test_show_configuration(self):
        self._test_boolean_option(StubbedSearchCommand.show_configuration)

    def _test_boolean_option(self, option):

        rebase_environment('app_without_logging_configuration')
        command = StubbedSearchCommand()

        # show_configuration accepts Splunk boolean values

        boolean_values = {
            '0': False, '1': True,
            'f': False, 't': True,
            'n': False, 'y': True,
            'no': False, 'yes': True,
            'false': False, 'true': True}

        for value in boolean_values:
            for variant in value, value.capitalize(), value.upper():
                for s in variant, bytes(variant):
                    option.fset(command, s)
                    self.assertEquals(option.fget(command), boolean_values[value])

        option.fset(command, None)
        self.assertEquals(option.fget(command), None)

        for value in 13, b'bytes', 'string', object():
            try:
                option.fset(command, value)
            except ValueError:
                pass
            except BaseException as error:
                self.fail('Expected ValueError when setting {}={}, but {} was raised'.format(
                    option.name, repr(value), type(error)))
            else:
                self.fail('Expected ValueError, but {}={} was accepted.'.format(
                    option.name, repr(option.fget(command))))

        return


if __name__ == "__main__":
    main()

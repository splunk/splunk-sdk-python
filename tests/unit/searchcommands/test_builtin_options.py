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


import os
import sys
import logging

from unittest import main, TestCase
import pytest
from io import StringIO


from splunklib.searchcommands import environment
from splunklib.searchcommands.decorators import Configuration
from splunklib.searchcommands.search_command import SearchCommand

from tests.unit.searchcommands import rebase_environment, package_directory


# portable log level names
# https://stackoverflow.com/a/49724281
def level_names():
    return [
        logging.getLevelName(v)
        for v in sorted(getattr(logging, "_levelToName", None) or logging._levelNames)
        if getattr(v, "real", 0)
    ]


@Configuration()
class StubbedSearchCommand(SearchCommand):
    class ConfigurationSettings(SearchCommand.ConfigurationSettings):
        @classmethod
        def fix_up(cls, command_class):
            pass


@pytest.mark.smoke
class TestBuiltinOptions(TestCase):
    def setUp(self):
        TestCase.setUp(self)

    def test_logging_configuration(self):
        # Test that logging is properly initialized when there is no logging configuration file

        rebase_environment("app_without_logging_configuration")

        self.assertIsNone(environment.logging_configuration)
        self.assertTrue(
            any(isinstance(h, logging.StreamHandler) for h in logging.root.handlers)
        )
        self.assertTrue("splunklib" in logging.Logger.manager.loggerDict)
        self.assertEqual(
            environment.splunklib_logger, logging.Logger.manager.loggerDict["splunklib"]
        )
        self.assertIsInstance(environment.splunklib_logger, logging.Logger)

        command = StubbedSearchCommand()

        self.assertIs(command.logger, logging.getLogger("StubbedSearchCommand"))
        self.assertEqual(len(command.logger.handlers), 0)
        self.assertIsNone(command.logging_configuration)
        self.assertIs(command.logger.root, logging.root)

        root_handler = next(
            h for h in logging.root.handlers if isinstance(h, logging.StreamHandler)
        )

        self.assertIsInstance(root_handler, logging.StreamHandler)
        self.assertEqual(root_handler.stream, sys.stderr)

        self.assertEqual(
            command.logging_level, logging.getLevelName(logging.root.level)
        )
        root_handler.stream = StringIO()
        message = "Test that output is directed to stderr without formatting"
        command.logger.warning(message)
        self.assertEqual(root_handler.stream.getvalue(), message + "\n")

        # A search command loads {local,default}/logging.conf when it is available

        rebase_environment("app_with_logging_configuration")

        command = StubbedSearchCommand()
        self.assertEqual(
            command.logging_configuration,
            os.path.join(environment.app_root, "default", "logging.conf"),
        )
        self.assertIs(command.logger, logging.getLogger("StubbedSearchCommand"))

        # Setting logging_configuration loads a new logging configuration file relative to the app root

        command.logging_configuration = "alternative-logging.conf"
        self.assertEqual(
            command.logging_configuration,
            os.path.join(environment.app_root, "default", "alternative-logging.conf"),
        )
        self.assertIs(command.logger, logging.getLogger("StubbedSearchCommand"))

        # Setting logging_configuration loads a new logging configuration file on an absolute path

        app_root_logging_configuration = os.path.join(
            environment.app_root, "logging.conf"
        )
        command.logging_configuration = app_root_logging_configuration

        self.assertEqual(command.logging_configuration, app_root_logging_configuration)
        self.assertIs(command.logger, logging.getLogger("StubbedSearchCommand"))

        # logging_configuration raises a value error, if a non-existent logging configuration file is provided

        try:
            command.logging_configuration = "foo"
        except ValueError:
            pass
        except BaseException as e:
            self.fail(f"Expected ValueError, but {type(e)} was raised")
        else:
            self.fail(
                f"Expected ValueError, but logging_configuration={command.logging_configuration}"
            )

        try:
            command.logging_configuration = os.path.join(
                package_directory, "non-existent.logging.conf"
            )
        except ValueError:
            pass
        except BaseException as e:
            self.fail(f"Expected ValueError, but {type(e)} was raised")
        else:
            self.fail(
                f"Expected ValueError, but logging_configuration={command.logging_configuration}"
            )

    def test_logging_level(self):
        rebase_environment("app_without_logging_configuration")
        command = StubbedSearchCommand()

        warning = logging.getLevelName(logging.WARNING)
        notset = logging.getLevelName(logging.NOTSET)
        logging.root.setLevel(logging.WARNING)

        self.assertEqual(command.logging_level, warning)

        # logging_level accepts all logging levels and returns their canonical string values

        self.assertEqual(warning, command.logging_level)

        for level in level_names():
            if isinstance(level, int):
                command.logging_level = level
                level_name = logging.getLevelName(level)
                self.assertEqual(
                    command.logging_level,
                    warning if level_name == notset else level_name,
                )
            else:
                level_name = logging.getLevelName(logging.getLevelName(level))
                for variant in level, level.lower(), level.capitalize():
                    command.logging_level = variant
                    self.assertEqual(
                        command.logging_level,
                        warning if level_name == notset else level_name,
                    )

        # logging_level accepts any numeric value

        for level in 999, 999.999:
            command.logging_level = level
            self.assertEqual(command.logging_level, "Level 999")

        # logging_level raises a value error for unknown logging level names

        current_value = command.logging_level

        try:
            command.logging_level = "foo"
        except ValueError:
            pass
        except BaseException as e:
            self.fail(f"Expected ValueError, but {type(e)} was raised")
        else:
            self.fail(f"Expected ValueError, but logging_level={command.logging_level}")

        self.assertEqual(command.logging_level, current_value)

    def test_record(self):
        self._test_boolean_option(StubbedSearchCommand.record)

    def test_show_configuration(self):
        self._test_boolean_option(StubbedSearchCommand.show_configuration)

    def _test_boolean_option(self, option):
        rebase_environment("app_without_logging_configuration")
        command = StubbedSearchCommand()

        # show_configuration accepts Splunk boolean values

        boolean_values = {
            "0": False,
            "1": True,
            "f": False,
            "t": True,
            "n": False,
            "y": True,
            "no": False,
            "yes": True,
            "false": False,
            "true": True,
        }

        for value in boolean_values:
            for variant in value, value.capitalize(), value.upper():
                option.fset(command, variant)
                self.assertEqual(option.fget(command), boolean_values[value])

        option.fset(command, None)
        self.assertEqual(option.fget(command), None)

        for value in 13, b"bytes", "string", object():
            try:
                option.fset(command, value)
            except ValueError:
                pass
            except BaseException as error:
                self.fail(
                    f"Expected ValueError when setting {option.name}={repr(value)}, but {type(error)} was raised"
                )
            else:
                self.fail(
                    f"Expected ValueError, but {option.name}={repr(option.fget(command))} was accepted."
                )


if __name__ == "__main__":
    main()

# coding=utf-8
# Copyright 2011-2013 Splunk, Inc.
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

from __future__ import absolute_import

from collections import OrderedDict
from logging import getLogger, NOTSET
import inspect
import sys

from . import csv
from . import logging
from . decorators import Option
from . validators import Boolean, Fieldname, Set
from . InputHeader import InputHeader
from . MessagesHeader import MessagesHeader
from . SearchCommandParser import SearchCommandParser


class SearchCommand(object):
    """ TODO: Documentation

    """
    def __init__(self):
        logging.configure()

        # Variables that may be used, but not altered by derived classes

        self.logger = getLogger(type(self).__name__)
        self.input_header = InputHeader()
        self.messages = MessagesHeader()

        # Variables backing option/property values

        self._configuration = None
        self._option_view = None
        self._fieldnames = None
        self._logging_configuration = None

        self.parser = SearchCommandParser()

    def __repr__(self):
        # TODO: Meet the bar for a __repr__ implementation: format value as a
        # Python expression, if you can provide an exact representation
        return str(self)

    def __str__(self):
        return ' '.join([type(self).name, str(self.options)] + self.fieldnames)

    #region Options

    @Option
    def logging_configuration(self):
        """ **Syntax:** logging_configuration=<path>
        **Description:** Loads an alternative logging configuration file for
        a command invocation. The logging configuration file must be in Python
        ConfigParser-format. Path names are relative to the app root directory.

        """
        return self._logging_configuration

    @logging_configuration.setter
    def logging_configuration(self, value):
        if value is None:
            # TODO: Return to configuration as set by logging.configure
            pass
        else:
            logging.configure(value)
            self._logging_configuration = value
        return

    @Option
    def logging_level(self):
        """ **Syntax:** logging_level=[CRITICAL|ERROR|WARNING|INFO|DEBUG|NOTSET]
        **Description:** Sets the threshold for the logger of this command
        invocation. Logging messages less severe than `logging_level` will be
        ignored.

        """
        return self.logger.getEffectiveLevel()

    @logging_level.setter
    def logging_level(self, value):
        if value is None:
            # TODO: Return to logging level as set by logging.configure
            pass
        else:
            self.logger.setLevel(value)
        return

    show_configuration = Option(doc='''
        **Syntax:** show_configuration=<bool>
        **Description:** When `true`, reports command configuration in the
        messages header for this command invocation. Defaults to `false`.

        ''', default=False, validate=Boolean())

    #endregion

    #region Properties

    @property
    def configuration(self):
        return self._configuration

    @property
    def fieldnames(self):
        return self._fieldnames

    @fieldnames.setter
    def fieldnames(self, value):
        self._fieldnames = value

    @property
    def options(self):
        if self._option_view is None:
            self._option_view = Option.View(self)
        return self._option_view

    #endregion

    #region Methods

    def process(self, argv=sys.argv, input_file=sys.stdin, output_file=sys.stdout):
        """ Process items on the pipeline using instructions on the command line

        TODO: Description

        """
        self.logger.debug('Command line: %s' % argv)
        self._configuration = None

        if len(argv) >= 2 and argv[1] == '__GETINFO__':

            # BFR: Check if Splunk gives us an input header on __GETINFO__

            argv, configuration, operation, fieldnames = self._configure(
                argv, input_file=None)
            try:
                self.parser.parse(argv, self, 'ANY')
            except (SyntaxError, ValueError) as e:
                writer = csv.DictWriter(self, fieldnames=['ERROR'])
                writer.writerow({'ERROR': e})
                self.logger.error(e)
                return
            self._configuration = configuration.get_effective(self)
            if self.show_configuration:
                self.messages.append(
                    'info_message', '\n'.join(
                        ['%s = %s' % (n, v)
                         for n, v in self.configuration.iteritems()]))
            writer = csv.DictWriter(
                self, output_file, fieldnames=sorted(self.configuration.keys()),
                mv_delimiter=',')
            writer.writerow(self.configuration)

        elif len(argv) >= 2 and argv[1] == '__EXECUTE__':

            self.input_header.read(input_file)
            # TODO: Do generating commands get input headers?
            argv, configuration, operation, reader = self._configure(
                argv, input_file)

            try:
                self.parser.parse(argv, self, reader.fieldnames)
            except (SyntaxError, ValueError) as e:
                self.messages.append("error_message", e)
                self.messages.write(output_file)
                self.logger.error(e)
                return

            self._configuration = configuration.get_effective(self)
            writer = csv.DictWriter(self, output_file)
            self._execute(operation, reader, writer)

        else:
            message = ('Static configuration is unsupported in this release. ' +
                       'Please add this setting to commands.conf: ' +
                       'supports_getinfo = true')
            self.messages.append('error_message', message)
            self.messages.write()
            self.logger.error(message)
            # TODO: Support static configuration by verifying the implementation
            # based on configuration. Can we support map/reduce commands or must
            # commands be either map or reduce in this scenario?

    @staticmethod
    def records(reader):
        for record in reader:
            yield record
        return

    def _configure(self, argv, input_file):
        raise NotImplementedError('SearchCommand._configure(self, argv)')

    def _execute(self, operation, reader, writer):
        raise NotImplementedError('SearchCommand._configure(self, argv)')

    #endregion

    #region Types

    class ConfigurationSettings(object):
        """ TODO: Documentation

        """
        def __init__(self, settings, target_class):
            # TODO: Validate against property list with friendly diagnostic
            # messages when properties don't check
            if settings is not None:
                for setting, value in settings.iteritems():
                    setattr(self, setting, value)
            self._clear_required_fields = False

        def __str__(self):
            # TODO: Return command.conf stanza
            return ''

        #region Properties

        # Constant configuration settings

        @property
        def clear_required_fields(self):
            """ Indicates whether required_fields are additive fields required
            by subsequent commands

            If true, required_fields represents the *only* fields required.	If
            false, required_fields are additive to any fields that may be
            required by subsequent commands. In most cases, false is appropriate
            for streaming commands and true for reporting commands.

            """
            return self._clear_required_fields

        @clear_required_fields.setter
        def clear_required_fields(self, value):
            self._clear_required_fields = bool(value)

        @property
        def enableheader(self):
            """ TODO: Documentation

            """
            return True

        @property
        def outputheader(self):
            """ TODO: Documentation

            """
            return True

        @property
        def supports_multivalue(self):
            """ TODO: Documentation

            """
            return True

        @property
        def supports_rawargs(self):
            """ TODO: Documentation
            """
            return True

        # Derived configuration settings

        @property
        def required_fields(self):
            """ TODO: Documentation

            """
            return SearchCommand.ConfigurationSettings._get_required_fields

        #endregion

        #region Methods

        def get_effective(self, command):
            """ TODO: Documentation

            """
            cls = type(self)
            if cls._settings is None:
                cls._settings = OrderedDict()
                for name in dir(cls):
                    attr = getattr(cls, name)
                    if isinstance(attr, property):
                        cls._settings[name] = attr
            settings = OrderedDict()
            for name, prop in cls._settings.iteritems():
                value = prop.__get__(self)
                if inspect.ismethod(value):
                    value = value(command)
                settings[name] = value
            command.logger.debug('Configuration: %s' % settings)
            return settings

        @classmethod
        def _get_required_fields(cls, command):
            """ Assemble comma-separated list of required field names

            This is the union of the set of fieldnames and fieldname valued
            options given as argument to `command`.

            """
            fieldnames = set(command.fieldnames)
            options = command.options
            command_type = type(command)
            for option_name in options:
                option_object = getattr(command_type, option_name)
                if isinstance(option_object.validate, Fieldname):
                    value = getattr(command, option_name)
                    if value is not None:
                        fieldnames.add(value)
            return ','.join(fieldnames)

        #endregion

        #region Variables

        _settings = None

        #endregion

    #endregion

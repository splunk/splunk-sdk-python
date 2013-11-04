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

# Absolute imports
from collections import OrderedDict
from inspect import getmembers
from logging import getLogger
from os import path
from sys import argv, stdin, stdout

# Relative imports
from . import csv, logging
from . decorators import Option
from . validators import Boolean, Fieldname
from . internals import InputHeader, MessagesHeader, SearchCommandParser


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

    def process(self, args=argv, input_file=stdin, output_file=stdout):
        """ Process search result records as specified by command arguments

        :param args: Sequence of command arguments
        :param input_file: Pipeline input file
        :param output_file: Pipeline output file

        """
        self.logger.debug('Command line: %s' % args)
        self._configuration = None

        if len(args) >= 2 and args[1] == '__GETINFO__':

            # BFR: Check if Splunk gives us an input header on __GETINFO__

            ConfigurationSettings, operation, args, reader = self._prepare(
                args, input_file=None)
            try:
                self.parser.parse(args, self, 'ANY')
            except (SyntaxError, ValueError) as e:
                writer = csv.DictWriter(output_file, self, fieldnames=['ERROR'])
                writer.writerow({'ERROR': e})
                self.logger.error(e)
                return
            self._configuration = ConfigurationSettings(self)
            if self.show_configuration:
                self.messages.append('info_message', str(self.configuration))
            writer = csv.DictWriter(
                output_file, self, self.configuration.keys(), mv_delimiter=',')
            writer.writerow(self.configuration.items())

        elif len(args) >= 2 and args[1] == '__EXECUTE__':

            # TODO: Do generating commands get input headers?

            self.input_header.read(input_file)
            ConfigurationSettings, operation, args, reader = self._prepare(
                args, input_file)

            try:
                self.parser.parse(args, self, reader.fieldnames)
            except (SyntaxError, ValueError) as e:
                self.messages.append("error_message", e)
                self.messages.write(output_file)
                self.logger.error(e)
                return

            self._configuration = ConfigurationSettings(self)
            writer = csv.DictWriter(output_file, self)
            self._execute(operation, reader, writer)

        else:
            message = (
                'Static configuration is unsupported. Please configure this '
                'command as follows in default/commands.conf:\n\n'
                '[default]\n'
                'supports_getinfo = true\n'
                '[%s]\n'
                'filename = %s' %
                (type(self).name, path.basename(argv[0])))
            self.messages.append('error_message', message)
            self.messages.write()
            self.logger.error(message)

    @staticmethod
    def records(reader):
        for record in reader:
            yield record
        return

    def _prepare(self, argv, input_file):
        raise NotImplementedError('SearchCommand._configure(self, argv)')

    def _execute(self, operation, reader, writer):
        raise NotImplementedError('SearchCommand._configure(self, argv)')

    #endregion

    #region Types

    class ConfigurationSettings(object):
        """ TODO: Documentation

        """
        def __init__(self, command):
            self.command = command

        def __str__(self):
            """ Retrieves the string representation of this instance

            :return: String of newline-separated `name = value` pairs

            """
            text = '\n'.join(
                ['%s = %s' % (k, getattr(self, k)) for k in self.keys()])
            return text

        #region Properties

        # Constant configuration settings

        @property
        def changes_colorder(self):
            """ Specifies whether output should be used to change the column
            ordering of fields

            Default: True.

            """
            return type(self)._changes_colorder

        _changes_colorder = True

        @property
        def clear_required_fields(self):
            """ Signals if `required_fields` are the only fields required by
            subsequent commands

            If `True`, `required_fields` are the *only* fields required by
            subsequent commands. If `False`, required_fields are additive to any
            fields that may be required by subsequent commands. In most cases
            `False` is appropriate for streaming commands and `True` is
            appropriate for reporting commands.

            """
            return type(self)._clear_required_fields

        _clear_required_fields = False

        @property
        def enableheader(self):
            """ TODO: Documentation

            """
            return True

        @property
        def maxinputs(self):
            """ Maximum number of events that may be passed to an invocation of
            the command

            This limit may not exceed the value of `maxresultrows` as defined in
            limits.conf (default: 50,000). Use a value  of zero (0) to select a
            limit of `maxresultrows`.

            Default: maxinputs=0

            """
            return type(self)._maxinputs

        _maxinputs = 0

        @property
        def needs_empty_results(self):
            """ Specifies whether or not this search command must be called with
            intermediate empty search results

            Default: True

            """
            return type(self)._needs_empty_results

        _needs_empty_results = True


        @property
        def outputheader(self):
            """ TODO: Documentation

            """
            return True

        @property
        def passauth(self):
            """ Specifies whether or not this search command requires an
            authentication token on the start of input

            Default: False

            """
            return type(self)._passauth

        _passauth = False


        @property
        def perf_warn_limit(self):
            """ Instructs Splunk to issue a performance warning message if more
            than this many input events are passed to this search command

            A value of zero (0) disables performance warning messages.

            Default: 0

            """
            return type(self)._perf_warn_limit

        _perf_warn_limit = 0

        @property
        def requires_srinfo(self):
            """ Specifies if the command requires search results information

            If true the full path name to a search results information file
            will be provided in the `self.input_headers` under the key
            `'infoPath'`.

            Default: False

            """
            return type(self)._requires_srinfo

        _requires_srinfo = False

        @property
        def run_in_preview(self):
            """ Specify whether to run this command if generating results just
            for preview rather than final output

            Default: True

            """
            return type(self)._run_in_preview

        _run_in_preview = True

        @property
        def stderr_dest(self):
            """ Specified what to do with messages logged to `stderr`

            You may specify on of these string values:

            Value     | Meaning
            ----------|---------------------------------------------------------
            `log`     | Write messages to the job's search.log file
            `message` | Write each line of each message as a search info message
            `none`    | Discard all messages logged to stderr

            Default: `log`

            """
            return type(self)._stderr_dest

        _stderr_dest = 'log'

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

        # Computed configuration settings

        @property
        def required_fields(self):
            """ Comma-separated list of required field names

            This list is the union of the set of fieldnames and fieldname-valued
            options given as argument to a command.

            """
            # TODO: Represent fieldnames as `set` to eliminate dups right away
            # TODO: Verify that option.itervalues() works

            fieldnames = set(self.command.fieldnames)
            for name, option in self.command.options.iteritems():
                if isinstance(option.validator, Fieldname):
                    value = option.value
                    if value is not None:
                        fieldnames.add(value)
            text = ','.join(fieldnames)
            return text

        #endregion

        #region Methods

        @classmethod
        def configuration_settings(cls):
            """ Represents this class as a dictionary of `property` instances
            and `backing_field` names keyed by configuration setting name

            This method is used by the `ConfigurationSettingsType` meta-class to
            construct new `ConfigurationSettings` classes. It is also used by
            instances of this class to retrieve configuration setting names and
            their values. See `SearchCommand.keys` and `SearchCommand.items`.

            """
            if cls._settings is None:
                is_property = lambda x: isinstance(x, property)
                cls._settings = {}
                for name, prop in getmembers(cls, is_property):
                    backing_field = '_' + name
                    if not hasattr(cls, backing_field):
                        backing_field = None
                    cls._settings[name] = (prop, backing_field)
            return cls._settings

        @classmethod
        def fix_up(cls, command_class):
            """ Adjusts and checks this class and its search command class

            Derived classes must override this method. It is used by the
            `Configuration` decorator to fix up the `SearchCommand` classes
            that it adorns. This method is overridden by `GeneratingCommand`,
            `ReportingCommand`, and `SearchCommand`, the built-in base types
            for all other search commands.

            :param command_class: Command class targeted by this class

            """
            raise NotImplementedError(
                'SearchCommand.fix_up method must be overridden')

        def items(self):
            """ Represents this instance as an `OrderedDict`

            This method is used by the SearchCommand.process method to report
            configuration settings to Splunk during the `__GETINFO__` phase of
            a request to process a chunk of search results.

            :return: OrderedDict containing setting values keyed by name

            """
            return OrderedDict([(k, getattr(self, k)) for k in self.keys()])

        def keys(self):
            """ Gets the names of the settings represented by this instance

            :return: Sorted list of setting names.

            """
            return sorted(type(self).configuration_settings().keys())

        #endregion

        #region Variables

        _settings = None

        #endregion

    #endregion

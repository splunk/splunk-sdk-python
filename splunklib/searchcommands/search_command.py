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

from __future__ import absolute_import

# Absolute imports

from splunklib.client import Service

try:
    from collections import OrderedDict  # python 2.7
except ImportError:
    from ordereddict import OrderedDict  # python 2.6

from logging import _levelNames, getLevelName
from inspect import getmembers
from os import environ, path
from sys import argv, exit, stdin, stdout
from urlparse import urlsplit
from xml.etree import ElementTree

# Relative imports

from . import logging, splunk_csv
from .decorators import Option
from .validators import Boolean, Fieldname
from .search_command_internals import InputHeader, MessagesHeader, SearchCommandParser


class SearchCommand(object):
    """ Represents a custom search command.

    """

    def __init__(self):

        # Variables that may be used, but not altered by derived classes

        self.logger, self._logging_configuration = logging.configure(type(self).__name__)
        self.input_header = InputHeader()
        self.messages = MessagesHeader()

        if u'SPLUNK_HOME' not in environ:
            self.logger.warning(
                u'SPLUNK_HOME environment variable is undefined.\n'
                u'If you are testing outside of Splunk, consider running under control of the Splunk CLI:\n'
                u'    splunk cmd %s\n'
                u'If you are running inside of Splunk, SPLUNK_HOME should be defined. Consider troubleshooting your '
                u'installation.', self)

        # Variables backing option/property values

        self._default_logging_level = self.logger.level
        self._configuration = None
        self._fieldnames = None
        self._option_view = None
        self._output_file = None
        self._search_results_info = None
        self._service = None

        self.parser = SearchCommandParser()

    def __repr__(self):
        return str(self)

    def __str__(self):
        values = [type(self).name, str(self.options)] + self.fieldnames
        text = ' '.join([value for value in values if len(value) > 0])
        return text

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
        self.logger, self._logging_configuration = logging.configure(
            type(self).__name__, value)
        return

    @Option
    def logging_level(self):
        """ **Syntax:** logging_level=[CRITICAL|ERROR|WARNING|INFO|DEBUG|NOTSET]

        **Description:** Sets the threshold for the logger of this command
        invocation. Logging messages less severe than `logging_level` will be
        ignored.

        """
        return getLevelName(self.logger.getEffectiveLevel())

    @logging_level.setter
    def logging_level(self, value):
        if value is None:
            value = self._default_logging_level
        if type(value) is str:
            try:
                level = _levelNames[value.upper()]
            except KeyError:
                raise ValueError('Unrecognized logging level: %s' % value)
        else:
            try:
                level = int(value)
            except ValueError:
                raise ValueError('Unrecognized logging level: %s' % value)
        self.logger.setLevel(level)
        return

    show_configuration = Option(doc='''
        **Syntax:** show_configuration=<bool>

        **Description:** When `true`, reports command configuration in the
        messages header for this command invocation. Defaults to `false`.

        ''', default=False, validate=Boolean())

    # #endregion

    #region Properties

    @property
    def configuration(self):
        """ Returns the configuration settings for this command.

        """
        return self._configuration

    @property
    def fieldnames(self):
        """ Returns the fieldnames specified as argument to this command.

        """
        return self._fieldnames

    @fieldnames.setter
    def fieldnames(self, value):
        self._fieldnames = value

    @property
    def options(self):
        """ Returns the options specified as argument to this command.

        """
        if self._option_view is None:
            self._option_view = Option.View(self)
        return self._option_view

    @property
    def search_results_info(self):
        """ Returns the search results info for this command invocation or None.

        The search results info object is created from the search results info
        file associated with the command invocation. Splunk does not pass the
        location of this file by default. You must request it by specifying
        these configuration settings in commands.conf:

        .. code-block:: python
            enableheader=true
            requires_srinfo=true

        The :code:`enableheader` setting is :code:`true` by default. Hence, you
        need not set it. The :code:`requires_srinfo` setting is false by
        default. Hence, you must set it.

        :return: :class:`SearchResultsInfo`, if :code:`enableheader` and
            :code:`requires_srinfo` are both :code:`true`. Otherwise, if either
            :code:`enableheader` or :code:`requires_srinfo` are :code:`false`,
            a value of :code:`None` is returned.

        """
        if self._search_results_info is not None:
            return self._search_results_info

        try:
            info_path = self.input_header['infoPath']
        except KeyError:
            return None

        def convert_field(field):
            return (field[1:] if field[0] == '_' else field).replace('.', '_')

        def convert_value(field, value):

            if field == 'countMap':
                split = value.split(';')
                value = dict((key, int(value))
                             for key, value in zip(split[0::2], split[1::2]))
            elif field == 'vix_families':
                value = ElementTree.fromstring(value)
            elif value == '':
                value = None
            else:
                try:
                    value = float(value)
                    if value.is_integer():
                        value = int(value)
                except ValueError:
                    pass

            return value

        with open(info_path, 'rb') as f:
            from collections import namedtuple
            import csv
            reader = csv.reader(f, dialect='splunklib.searchcommands')
            fields = [convert_field(x) for x in reader.next()]
            values = [convert_value(f, v) for f, v in zip(fields, reader.next())]

        search_results_info_type = namedtuple('SearchResultsInfo', fields)
        self._search_results_info = search_results_info_type._make(values)

        return self._search_results_info

    @property
    def service(self):
        """ Returns a Splunk service object for this command invocation or None.

        The service object is created from the Splunkd URI and authentication
        token passed to the command invocation in the search results info file.
        This data is not passed to a command invocation by default. You must
        request it by specifying this pair of configuration settings in
        commands.conf:

           .. code-block:: python
               enableheader=true
               requires_srinfo=true

        The :code:`enableheader` setting is :code:`true` by default. Hence, you
        need not set it. The :code:`requires_srinfo` setting is false by
        default. Hence, you must set it.

        :return: :class:`splunklib.client.Service`, if :code:`enableheader` and
            :code:`requires_srinfo` are both :code:`true`. Otherwise, if either
            :code:`enableheader` or :code:`requires_srinfo` are :code:`false`,
            a value of :code:`None` is returned.

        """
        if self._service is not None:
            return self._service

        info = self.search_results_info

        if info is None:
            return None

        splunkd = urlsplit(info.splunkd_uri, info.splunkd_protocol, allow_fragments=False)

        self._service = Service(
            scheme=splunkd.scheme, host=splunkd.hostname, port=splunkd.port, token=info.auth_token, app=info.ppc_app)

        return self._service

    #endregion

    #region Methods

    def error_exit(self, error):
        self.logger.error('Abnormal exit: ' + error)
        self.write_error(error)
        exit(1)

    def process(self, args=argv, input_file=stdin, output_file=stdout):
        """ Processes search results as specified by command arguments.

        :param args: Sequence of command arguments
        :param input_file: Pipeline input file
        :param output_file: Pipeline output file

        """
        self.logger.debug(u'%s arguments: %s', type(self).__name__, args)
        self._configuration = None
        self._output_file = output_file

        try:
            if len(args) >= 2 and args[1] == '__GETINFO__':

                ConfigurationSettings, operation, args, reader = self._prepare(args, input_file=None)
                self.parser.parse(args, self)
                self._configuration = ConfigurationSettings(self)
                writer = splunk_csv.DictWriter(output_file, self, self.configuration.keys(), mv_delimiter=',')
                writer.writerow(self.configuration.items())

            elif len(args) >= 2 and args[1] == '__EXECUTE__':

                self.input_header.read(input_file)
                ConfigurationSettings, operation, args, reader = self._prepare(args, input_file)
                self.parser.parse(args, self)
                self._configuration = ConfigurationSettings(self)

                if self.show_configuration:
                    self.messages.append(
                        'info_message', '%s command configuration settings: %s'
                        % (self.name, self._configuration))

                writer = splunk_csv.DictWriter(output_file, self)
                self._execute(operation, reader, writer)

            else:

                file_name = path.basename(args[0])
                message = (
                    u'Command {0} appears to be statically configured and static '
                    u'configuration is unsupported by splunklib.searchcommands. '
                    u'Please ensure that default/commands.conf contains this '
                    u'stanza:\n'
                    u'[{0}]\n'
                    u'filename = {1}\n'
                    u'supports_getinfo = true\n'
                    u'supports_rawargs = true\n'
                    u'outputheader = true'.format(type(self).name, file_name))
                raise NotImplementedError(message)

        except SystemExit:
            raise

        except:

            import traceback
            import sys

            error_type, error_message, error_traceback = sys.exc_info()
            self.logger.error(traceback.format_exc(error_traceback))

            origin = error_traceback

            while origin.tb_next is not None:
                origin = origin.tb_next

            filename = origin.tb_frame.f_code.co_filename
            lineno = origin.tb_lineno

            self.write_error('%s at "%s", line %d : %s', error_type.__name__, filename, lineno, error_message)

            exit(1)

        return

    @staticmethod
    def records(reader):
        for record in reader:
            yield record
        return

    # TODO: Is it possible to support anything other than write_error? It does not seem so.

    def write_debug(self, message, *args):
        self._write_message(u'DEBUG', message, *args)
        return

    def write_error(self, message, *args):
        self._write_message(u'ERROR', message, *args)
        return

    def write_info(self, message, *args):
        self._write_message(u'INFO', message, *args)
        return

    def write_warning(self, message, *args):
        self._write_message(u'WARN', message, *args)

    def _execute(self, operation, reader, writer):
        raise NotImplementedError(u'SearchCommand._configure(self, argv)')

    def _prepare(self, argv, input_file):
        raise NotImplementedError(u'SearchCommand._configure(self, argv)')

    def _write_message(self, message_type, message_text, *args):
        import csv
        if len(args) > 0:
            message_text = message_text % args
        writer = csv.writer(self._output_file)
        writer.writerows([[], [message_type], [message_text]])

    #endregion

    #region Types

    class ConfigurationSettings(object):
        """ Represents the configuration settings common to all
        :class:`SearchCommand` classes.

        """

        def __init__(self, command):
            self.command = command

        def __str__(self):
            """ Converts the value of this instance to its string representation.

            The value of this ConfigurationSettings instance is represented as a
            string of newline-separated :code:`name=value` pairs.

            :return: String representation of this instance

            """
            text = ', '.join(
                ['%s=%s' % (k, getattr(self, k)) for k in self.keys()])
            return text

        #region Properties

        # Constant configuration settings

        @property
        def changes_colorder(self):
            """ Specifies whether output should be used to change the column
            ordering of fields.

            Default: :const:`True`

            """
            return type(self)._changes_colorder

        _changes_colorder = True

        @property
        def clear_required_fields(self):
            """ Specifies whether `required_fields` are the only fields required
            by subsequent commands.

            If :const:`True`, :attr:`required_fields` are the *only* fields
            required by subsequent commands. If :const:`False`,
            :attr:`required_fields` are additive to any fields that may be
            required by subsequent commands. In most cases :const:`False` is
            appropriate for streaming commands and :const:`True` is appropriate
            for reporting commands.

            Default: :const:`False`

            """
            return type(self)._clear_required_fields

        _clear_required_fields = False

        @property
        def enableheader(self):
            """ Signals that this command expects header information.

            Fixed: :const:`True`

            """
            return True

        @property
        def generating(self):
            """ Signals that this command does not generate new events.

            Fixed: :const:`False`

            """
            return False

        @property
        def maxinputs(self):
            """ Specifies the maximum number of events that may be passed to an
            invocation of this command.

            This limit may not exceed the value of `maxresultrows` as defined in
            limits.conf (default: 50,000). Use a value  of zero (0) to select a
            limit of `maxresultrows`.

            Default: :code:`0`

            """
            return type(self)._maxinputs

        _maxinputs = 0

        @property
        def needs_empty_results(self):
            """ Specifies whether or not this search command must be called with
            intermediate empty search results.

            Default: :const:`True`

            """
            return type(self)._needs_empty_results

        _needs_empty_results = True


        @property
        def outputheader(self):
            """ Signals that the output of this command is a messages header
            followed by a blank line and splunk_csv search results.

            Fixed: :const:`True`

            """
            return True

        @property
        def passauth(self):
            """ Specifies whether or not this search command requires an
            authentication token on the start of input.

            Default: :const:`False`

            """
            return type(self)._passauth

        _passauth = False


        @property
        def perf_warn_limit(self):
            """ Tells Splunk to issue a performance warning message if more
            than this many input events are passed to this search command.

            A value of zero (0) disables performance warning messages.

            Default: :code:`0`

            """
            return type(self)._perf_warn_limit

        _perf_warn_limit = 0

        @property
        def requires_srinfo(self):
            """ Specifies whether or not this command requires search results
            information.

            If :const:`True` the full path to a search results information file
            is provided by :attr:`SearchCommand.input_header['infoPath']`.

            Default: :const:`False`

            """
            return type(self)._requires_srinfo

        _requires_srinfo = False

        @property
        def run_in_preview(self):
            """ Tells Splunk whether to run this command when generating results
            for preview rather than final output.

            Default: :const:`True`

            """
            return type(self)._run_in_preview

        _run_in_preview = True

        @property
        def stderr_dest(self):
            """ Tells Splunk what to do with messages logged to `stderr`.

            Specify one of these string values:

            ================== ========================================================
            Value              Meaning
            ================== ========================================================
            :code:`'log'`      Write messages to the job's search.log file
            :code:`'message'`  Write each line of each message as a search info message
            :code:`'none'`     Discard all messages logged to stderr
            ================== ========================================================

            Default: :code:`'log'`

            """
            return type(self)._stderr_dest

        _stderr_dest = 'log'

        @property
        def supports_multivalues(self):
            """ Signals that this search command supports multivalues.

            Fixed: :const:`True`

            """
            return True

        @property
        def supports_rawargs(self):
            """ Signals that this search command parses raw arguments.

            Fixed: :const:`True`

            """
            return True

        # Computed configuration settings

        @property
        def required_fields(self):
            """ Specifies a comma-separated list of required field names.

            This list is computed as the union of the set of fieldnames and
            fieldname-valued options given as argument to this command.

            """
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
            """ Represents this class as a dictionary of :class:`property`
            instances and :code:`backing_field` names keyed by configuration
            setting name.

            This method is used by the :class:`ConfigurationSettingsType`
            meta-class to construct new :class:`ConfigurationSettings` classes.
            It is also used by instances of this class to retrieve configuration
            setting names and their values. See :meth:`SearchCommand.keys` and
            :meth:`SearchCommand.items`.

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
            """ Adjusts and checks this class and its search command class.

            Derived classes must override this method. It is used by the
            :decorator:`Configuration` decorator to fix up the
            :class:`SearchCommand` classes it adorns. This method is overridden
            by :class:`GeneratingCommand`, :class:`ReportingCommand`, and
            :class:`StreamingCommand`, the base types for all other search
            commands.

            :param command_class: Command class targeted by this class

            """
            raise NotImplementedError(
                'SearchCommand.fix_up method must be overridden')

        def items(self):
            """ Represents this instance as an :class:`OrderedDict`.

            This method is used by the SearchCommand.process method to report
            configuration settings to Splunk during the :code:`__GETINFO__`
            phase of a request to process a chunk of search results.

            :return: :class:`OrderedDict` containing setting values keyed by
            name

            """
            return OrderedDict([(k, getattr(self, k)) for k in self.keys()])

        def keys(self):
            """ Gets the names of the settings represented by this instance.

            :return: Sorted list of setting names.

            """
            return sorted(type(self).configuration_settings().keys())

        #endregion

        #region Variables

        _settings = None

        #endregion

        #endregion

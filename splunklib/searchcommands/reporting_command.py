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

from . search_command_internals import ConfigurationSettingsType
from . streaming_command import StreamingCommand
from . search_command import SearchCommand
from . import splunk_csv


class ReportingCommand(SearchCommand):
    """ Processes search results and generates a reporting data structure.

    Reporting search commands run as either reduce or map/reduce operations. The
    reduce part runs on a search head and is responsible for processing a single
    chunk of search results to produce the command's reporting data structure.
    The map part is called a streaming preop. It feeds the reduce part with
    partial results and by default runs on the search head and/or one or more
    indexers.

    You must implement a :meth:`reduce` method as a generator function that
    iterates over a set of event records and yields a reporting data structure.
    You may implement a :meth:`map` method as a generator function that iterates
    over a set of event records and yields :class:`dict` or :class:`list(dict)`
    instances.

    **ReportingCommand configuration**

    Configure the :meth:`map` operation using a Configuration decorator on your
    :meth:`map` method. Configure it like you would a :class:`StreamingCommand`.

    Configure the :meth:`reduce` operation using a Configuration decorator on
    your :meth:`ReportingCommand` class.


    :ivar input_header: :class:`InputHeader`:  Collection representing the input
        header associated with this command invocation.

    :ivar messages: :class:`MessagesHeader`: Collection representing the output
        messages header associated with this command invocation.

    """
    #region Methods

    def map(self, records):
        """ Override this method to compute partial results.

        You must override this method, if :code:`requires_preop=True`.

        """
        self  # Turns off ide guidance that method may be static
        return NotImplemented

    def reduce(self, records):
        """ Override this method to produce a reporting data structure.

        You must override this method.

        """
        raise NotImplementedError('reduce(self, records)')

    def _execute(self, operation, reader, writer):
        for record in operation(SearchCommand.records(reader)):
            writer.writerow(record)
        return

    def _prepare(self, argv, input_file):
        if len(argv) >= 3 and argv[2] == '__map__':
            ConfigurationSettings = type(self).map.ConfigurationSettings
            operation = self.map
            argv = argv[3:]
        else:
            ConfigurationSettings = type(self).ConfigurationSettings
            operation = self.reduce
            argv = argv[2:]
        if input_file is None:
            reader = None
        else:
            reader = splunk_csv.DictReader(input_file)
        return ConfigurationSettings, operation, argv, reader

    #endregion

    #region Types

    class ConfigurationSettings(SearchCommand.ConfigurationSettings):
        """ Represents the configuration settings for a :code:`ReportingCommand`.

        """
        #region Properties
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

            Default: :const:`True`

            """
            return type(self)._clear_required_fields

        _clear_required_fields = True

        @property
        def requires_preop(self):
            """ Indicates whether :meth:`ReportingCommand.map` is required for
            proper command execution.

            If :const:`True`, :meth:`ReportingCommand.map` is guaranteed to be
            called. If :const:`False`, Splunk considers it to be an optimization
            that may be skipped.

            Default: :const:`False`

            """
            return type(self)._requires_preop

        _requires_preop = False

        @property
        def retainsevents(self):
            """ Signals that :meth:`ReportingCommand.reduce` transforms _raw
            events to produce a reporting data structure.

            Fixed: :const:`False`

            """
            return False

        @property
        def streaming(self):
            """ Signals that :meth:`ReportingCommand.reduce` runs on the search
            head.

            Fixed: :const:`False`

            """
            return False

        @property
        def streaming_preop(self):
            """ Denotes the requested streaming preop search string.

            Computed.

            """
            command = type(self.command)

            if command.map == ReportingCommand.map:
                return ""

            command_line = str(self.command)
            command_name = type(self.command).name
            text = ' '.join([
                command_name, '__map__', command_line[len(command_name) + 1:]])

            return text

        #endregion

        #region Methods

        @classmethod
        def fix_up(cls, command):
            """ Verifies :code:`command` class structure and configures the
            :code:`command.map` method.

            Verifies that :code:`command` derives from :code:`ReportingCommand`
            and overrides :code:`ReportingCommand.reduce`. It then configures
            :code:`command.reduce`, if an overriding implementation of
            :code:`ReportingCommand.reduce` has been provided.

            :param command: :code:`ReportingCommand` class

            Exceptions:

            :code:`TypeError` :code:`command` class is not derived from :code:`ReportingCommand`
            :code:`AttributeError` No :code:`ReportingCommand.reduce` override

            """
            if not issubclass(command, ReportingCommand):
                raise TypeError('%s is not a ReportingCommand' % command)

            if command.reduce == ReportingCommand.reduce:
                raise AttributeError('No ReportingCommand.reduce override')

            if command.map == ReportingCommand.map:
                cls._requires_preop = False
                return

            f = vars(command)['map']   # Function backing the map method
                # There is no way to add custom attributes to methods. See
                # [Why does setattr fail on a method](http://goo.gl/aiOsqh)
                # for an explanation.

            try:
                settings = f._settings
            except AttributeError:
                f.ConfigurationSettings = StreamingCommand.ConfigurationSettings
                return

            # Create new `StreamingCommand.ConfigurationSettings` class

            module = '.'.join([command.__module__, command.__name__, 'map'])
            name = 'ConfigurationSettings'
            bases = (StreamingCommand.ConfigurationSettings,)

            f.ConfigurationSettings = ConfigurationSettingsType(
                module, name, bases, settings)
            del f._settings
            return

        #endregion

    #endregion

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

# BFR: Does Splunk redundantly store the value of a single-value list in
# the shadowing **__mv_** field?

from __future__ import absolute_import

from . internals import ConfigurationSettingsType
from . StreamingCommand import StreamingCommand
from . SearchCommand import SearchCommand
from . import csv


class ReportingCommand(SearchCommand):
    """ Processes search results and generates a reporting data structure.

    Reporting search commands run as either reduce or map/reduce operations. The
    reduce part runs on a search head and is responsible for processing a single
    chunk of search results to produce the command's reporting data structure.
    The map part is called a streaming preop. It feeds the reduce part with
    partial results and by default is runs on the search head and/or one or more
    indexers.

    You must implement a `reduce` method as a generator function that iterates
    over a set of event records and yields a reporting data structure. You may
    implement a `map` method as a generator function that iterates over a set of
    event records and yields `dict` or `list(dict)` instances.

    ##ReportingCommand configuration
    Configure the `reduce` operation using a Configuration decorator on your
    ReportingCommand class.

    [TODO: ReportingCommand configuration highlights]

    Configure the `map` operation using a Configuration decorator on your
    ReportingCommand.map method. Configure it like you would a StreamingCommand.

    """

    # BFR: Can the streaming_preop command be the simple name of a python
    # script? Need it be configured in commands.conf?

    def __init__(self):
        super(ReportingCommand, self).__init__()
        self.fieldnames = []
        self.reader = None
        self.writer = None

    #region Methods

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
            reader = csv.DictReader(input_file)
        return ConfigurationSettings, operation, argv, reader

    def _execute(self, operation, reader, writer):
        try:
            for record in operation(self, SearchCommand.records(reader)):
                writer.writerow(record)
        except Exception as e:
            self.logger.error(e)

    def map(self, records):
        raise NotImplementedError('map(self, records)')

    def reduce(self, records):
        raise NotImplementedError('reduce(self, records)')

    #endregion

    #region Types

    class ConfigurationSettings(SearchCommand.ConfigurationSettings):
        """ TODO: Documentation

        """
        #region Properties

        @property
        def requires_preop(self):
            """ TODO: Documentation

            """
            return type(self)._requires_preop

        _requires_preop = False

        @property
        def retainsevents(self):
            """ TODO: Documentation
            """
            return False

        @property
        def streaming(self):
            """ TODO: Documentation

            """
            return False

        @property
        def streaming_preop(self):
            """ TODO: Documentation

            """
            command_line = str(self.command)
            command_name = type(self.command).name
            text = ' '.join([
                command_name, '__map__', command_line[len(command_name) + 1:]])
            return text

        #endregion

        #region Methods

        @classmethod
        def fix_up(cls, command):
            """ Verifies `command` class structure and configures `map` method

            Verifies that `command` derives from `ReportingCommand` and
            overrides `ReportingCommand.reduce`. It then configures
            `command.reduce`, if an overriding implementation of
            `ReportingCommand.reduce` has been provided.

            :param command: `ReportingCommand` class

            Exceptions:
            `TypeError` `command` class is not derived from `ReportingCommand`
            `AttributeError` No `ReportingCommand.reduce` override

            """
            if not issubclass(command, ReportingCommand):
                raise TypeError('%s is not a ReportingCommand' % command)

            if command.reduce == ReportingCommand.reduce:
                raise AttributeError('No ReportingCommand.reduce override')

            m = command.map

            if m == ReportingCommand.map:
                # TODO: Consider complaining if cls._requires_preop is True
                cls._requires_preop = None
                return

            # Create `StreamingCommand.ConfigurationSettings` class using
            # settings, if any, saved by the `map` method's `Configuration`
            # decorator

            settings = getattr(m, '_settings', None)

            if settings is None:
                m.ConfigurationSettings = StreamingCommand.ConfigurationSettings
                return

            module = '.'.join([command.__module__, command.__name__, 'map'])
            name = 'ConfigurationSettings'
            bases = (StreamingCommand.ConfigurationSettings,)

            # TODO: Why do setattr and delattr not work here?

            m.__dict__['ConfigurationSettings'] = ConfigurationSettingsType(
                module, name, bases, settings)
            del m.__dict__['_settings']

            return

        #endregion

    #endregion

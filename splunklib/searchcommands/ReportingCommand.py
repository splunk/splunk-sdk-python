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

# BFR: Does Splunk redundantly store the value of a single-value list in
# the shadowing **__mv_** field?

from __future__ import absolute_import

from .StreamingCommand import StreamingCommand
from .SearchCommand import SearchCommand
from . import csv

import inspect
import sys
import logging as log


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

    def _configure(self, argv, input_file):
        if len(argv) >= 3 and argv[2] == '__map__':
            configuration = type(self).map._configuration
            operation = self.map
            argv = argv[3:]
        else:
            configuration = type(self)._configuration
            operation = self.reduce
            argv = argv[2:]
        if input_file is None:
            reader = None
        else:
            reader = csv.DictReader(input_file)
        return argv, configuration, operation, reader

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
        def __init__(self, settings, target_class):
            """ TODO: Documentation

            """
            if target_class.reduce == ReportingCommand.reduce:
                raise AttributeError(
                    'You must override the ReportingCommand.reduce method')

            # If target_class overrides the map method, configure and remember it
            map_method = target_class.map

            if map_method == ReportingCommand.map:
                self._streaming_preop = None
                self._requires_preop = None
            else:
                settings = getattr(map_method, 'configuration', None)  # decorators.Configuration sets this "raw" value
                map_method.__dict__['configuration'] = StreamingCommand.ConfigurationSettings(settings, target_class)
                # TODO: Why does this not work: setattr(map_method, 'configuration', settings)?
                self._streaming_preop = target_class.map
                self._requires_preop = False

            super(ReportingCommand.ConfigurationSettings, self).__init__(settings, target_class)

        #region Properties

        @property
        def requires_preop(self):
            """ TODO: Documentation
            """
            return self._requires_preop

        @requires_preop.setter
        def requires_preop(self, value):
            """ TODO: Documentation
            """
            # TODO: Consider complaining or prohibiting setting this property of
            # self.streaming_preop is None
            self._requires_preop = bool(value)

        @property
        def streaming_preop(self):
            """ TODO: Documentation
            """
            # TODO: Linkage between this property and the command arguments
            # passed to `target_class`. This method must return that or None, if
            # there is no preop
            return type(self)._get_streaming_preop

        @classmethod
        def _get_streaming_preop(cls, command):
            command_line = str(command)
            command_name = type(command).name
            return ' '.join([command_name, '__map__', command_line[len(command_name) + 1:]])

        #endregion

    #endregion

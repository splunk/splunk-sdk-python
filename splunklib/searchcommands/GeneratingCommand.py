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

from .SearchCommand import SearchCommand
import sys


class GeneratingCommand(SearchCommand):
    """ Generates events based on command arguments.

    Generating commands receive no input and must be the first command on a
    pipeline. By default Splunk will run your command locally on a search head:

    :<source lang=python>@Configuration()</source>

    You can change the default behavior by configuring your generating command
    for event streaming:

    :<source lang=python>@Configuration(streaming=True)</source>

    Splunk will then run your command locally on a search head and/or remotely
    on one or more indexers.

    You can tell Splunk to run your streaming-enabled generating command locally
    on a search head, never remotely on indexers:

    :<source lang=python>@Configuration(local=True, streaming=True)</source>

    If your generating command produces event records in time order, you must
    tell Splunk to ensure correct behavior:

    :<source lang=python>@Configuration(generates_timeorder=True)</source>

    """

    # TODO: process method implementation
    # TODO: Documentation

    def __init__(self):
        super(GeneratingCommand, self).__init__()

    #region Methods

    def _configure(self, argv, input_file):
        configuration = type(self)._configuration
        argv = argv[2:]
        return argv, configuration, self.generate, 'ANY'

    def _execute(self, operation, reader, writer):
        try:
            for record in operation(self):
                writer.writerow(record)
        except Exception as e:
            self.logger.error(e)

    def generate(self):
        raise NotImplementedError('GeneratingCommand.generate(self, records)')

    #endregion

    #region Types

    class ConfigurationSettings(SearchCommand.ConfigurationSettings):
        """ TODO: Documentation
        """
        def __init__(self, settings, target_class):
            self._generates_timeorder = False
            self._local = False
            self._streaming = False

        #region Properties

        @property
        def generating(self):
            """ TODO: Documentation
            """
            return True

        @property
        def generates_timeorder(self):
            """ TODO: Documentation
            """
            return self._generates_timeorder

        @generates_timeorder.setter
        def generates_timeorder(self, value):
            self._generates_timeorder = bool(value)

        @property
        def local(self):
            """ TODO: Documentation
            """
            return self._local

        @local.setter
        def local(self, value):
            self._local = bool(value)

        @property
        def streaming(self):
            """ TODO: Documentation
            """
            return self._streaming

        @streaming.setter
        def streaming(self, value):
            self._streaming = bool(value)

        #endregion

    #endregion
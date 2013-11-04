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

from . SearchCommand import SearchCommand


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

    def generate(self):
        raise NotImplementedError('GeneratingCommand.generate(self, records)')

    def _prepare(self, argv, input_file):
        ConfigurationSettings = type(self).ConfigurationSettings
        argv = argv[2:]
        return ConfigurationSettings, argv, self.generate, 'ANY'

    def _execute(self, operation, reader, writer):
        try:
            for record in operation(self):
                writer.writerow(record)
        except Exception as e:
            self.logger.error(e)

    #endregion

    #region Types

    class ConfigurationSettings(SearchCommand.ConfigurationSettings):
        """ TODO: Documentation
        """
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
            return type(self)._generates_timeorder

        _generates_timeorder = False

        @property
        def local(self):
            """ TODO: Documentation
            """
            return type(self)._local

        _local = False

        @property
        def retainsevents(self):
            """ TODO: Documentation
            """
            return type(self)._retainsevents

        _retainsevents = False

        @property
        def streaming(self):
            """ TODO: Documentation
            """
            return type(self)._streaming

        _streaming = False

        #endregion

        #region Methods

        @classmethod
        def fix_up(cls, command):
            """ TODO: Documentation

            """
            if command.reduce == GeneratingCommand.generate:
                raise AttributeError('No GeneratingCommand.generate override')
            return

        #endregion

    #endregion

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

from . search_command import SearchCommand


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

    def __init__(self):
        super(GeneratingCommand, self).__init__()

    #region Methods

    def generate(self):
        """ TODO: Documentation

        """
        raise NotImplementedError('GeneratingCommand.generate(self, records)')

    def _prepare(self, argv, input_file):
        """ TODO: Documentation

        """
        ConfigurationSettings = type(self).ConfigurationSettings
        argv = argv[2:]
        return ConfigurationSettings, argv, self.generate, 'ANY'

    def _execute(self, operation, reader, writer):
        """ TODO: Documentation

        """
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
            """ Signals that this command generates new events

            Fixed: True

            """
            return True

        @property
        def generates_timeorder(self):
            """ Specifies whether this command generates events in descending
            time order

            Default: False

            """
            return type(self)._generates_timeorder

        _generates_timeorder = False

        @property
        def local(self):
            """ Specifies whether this command should only be run on the search
            head

            This setting is used to override Splunk's default policy for running
            streamable search commands. See the `streaming` configuration
            setting.

            Default: False

            """
            return type(self)._local

        _local = False

        @property
        def retainsevents(self):
            """ Specifies whether this command retains _raw events or transforms
            them

            Default: False

            """
            return type(self)._retainsevents

        _retainsevents = False

        @property
        def streaming(self):
            """ Specifies whether this search command is streamable

            By default streamable search commands may be run on the search head
            or one or more indexers, depending on performance and scheduling
            considerations. This behavior may be overridden by setting
            `local=True`. This forces a streamable command to be run on the
            search head.

            Default: False.

            """
            return type(self)._streaming

        _streaming = False

        #endregion

        #region Methods

        @classmethod
        def fix_up(cls, command):
            """ TODO: Documentation

            """
            if command.generate == GeneratingCommand.generate:
                raise AttributeError('No GeneratingCommand.generate override')
            return

        #endregion

    #endregion

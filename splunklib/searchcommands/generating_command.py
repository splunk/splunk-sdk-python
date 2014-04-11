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

from . search_command import SearchCommand


class GeneratingCommand(SearchCommand):
    """ Generates events based on command arguments.

    Generating commands receive no input and must be the first command on a
    pipeline. By default Splunk will run your command locally on a search head:

    .. code-block:: python

        @Configuration()
        class SomeGeneratingCommand(GeneratingCommand)

    You can change the default behavior by configuring your generating command
    for event streaming:

    .. code-block:: python

        @Configuration(streaming=True)
        class SomeGeneratingCommand(GeneratingCommand)
            ...

    Splunk will then run your command locally on a search head and/or remotely
    on one or more indexers.

    You can tell Splunk to run your streaming-enabled generating command locally
    on a search head, never remotely on indexers:

    .. code-block:: python

        @Configuration(local=True, streaming=True)
        class SomeGeneratingCommand(GeneratingCommand)
            ...

    If your generating command produces event records in time order, you must
    tell Splunk to ensure correct behavior:

    .. code-block:: python

        @Configuration(generates_timeorder=True)
        class SomeGeneratingCommand(GeneratingCommand)
            ...

    :ivar input_header: :class:`InputHeader`:  Collection representing the input
        header associated with this command invocation.

    :ivar messages: :class:`MessagesHeader`: Collection representing the output
        messages header associated with this command invocation.

    """
    #region Methods

    def generate(self):
        """ A generator that yields records to the Splunk processing pipeline

        You must override this method.

        """
        raise NotImplementedError('GeneratingCommand.generate(self)')

    def _execute(self, operation, reader, writer):
        for record in operation():
            writer.writerow(record)
        return

    def _prepare(self, argv, input_file):
        ConfigurationSettings = type(self).ConfigurationSettings
        argv = argv[2:]
        return ConfigurationSettings, self.generate, argv, 'ANY'

    #endregion

    #region Types

    class ConfigurationSettings(SearchCommand.ConfigurationSettings):
        """ Represents the configuration settings for a
        :code:`GeneratingCommand` class

        """
        #region Properties

        @property
        def generating(self):
            """ Signals that this command generates new events.

            Fixed: :const:`True`

            """
            return True

        @property
        def generates_timeorder(self):
            """ Specifies whether this command generates events in descending
            time order.

            Default: :const:`False`

            """
            return type(self)._generates_timeorder

        _generates_timeorder = False

        @property
        def local(self):
            """ Specifies whether this command should only be run on the search
            head.

            This setting is used to override Splunk's default policy for running
            streamable search commands. See the `streaming` configuration
            setting.

            Default: :const:`False`

            """
            return type(self)._local

        _local = False

        @property
        def retainsevents(self):
            """ Specifies whether this command retains _raw events or transforms
            them.

            Default: :const:`False`

            """
            return type(self)._retainsevents

        _retainsevents = True

        @property
        def streaming(self):
            """ Specifies that this command is streamable.

            By default streamable search commands may be run on the search head
            or one or more indexers, depending on performance and scheduling
            considerations. This behavior may be overridden by setting
            :code:`local=True`. This forces a streamable command to be run on the
            search head.

            Fixed: :const:`True`

            """
            return True

        #endregion

        #region Methods

        @classmethod
        def fix_up(cls, command):
            """ Verifies :code:`command` class structure.

            """
            if command.generate == GeneratingCommand.generate:
                raise AttributeError('No GeneratingCommand.generate override')
            return

        #endregion

    #endregion

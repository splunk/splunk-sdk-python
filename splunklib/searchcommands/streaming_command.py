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
from . import splunk_csv


class StreamingCommand(SearchCommand):
    """ Applies a transformation to search results as they travel through the
    processing pipeline.

    Streaming commands typically filter, sort, modify, or combine search
    results. Splunk will send search results in batches of up to 50,000 records.
    Hence, a search command must be prepared to be invoked many times during the
    course of pipeline processing. Each invocation should produce a set of
    results independently usable by downstream processors.

    By default Splunk may choose to run a streaming command locally on a search
    head and/or remotely on one or more indexers concurrently. The size and
    frequency of the search result batches sent to the command will vary based
    on scheduling considerations. Streaming commands are typically invoked many
    times during the course of pipeline processing.

    You can tell Splunk to run your streaming command locally on a search head,
    never remotely on indexers.

    .. code-block:: python

        @Configuration(local=False)
        class SomeStreamingCommand(StreamingCommand):
            ...

    If your streaming command modifies the time order of event records you must
    tell Splunk to ensure correct behavior.

    .. code-block:: python

        @Configuration(overrides_timeorder=True)
        class SomeStreamingCommand(StreamingCommand):
            ...

    :ivar input_header: :class:`InputHeader`:  Collection representing the input
        header associated with this command invocation.

    :ivar messages: :class:`MessagesHeader`: Collection representing the output
        messages header associated with this command invocation.

    """
    #region Methods

    def stream(self, records):
        """ Generator function that processes and yields event records to the
        Splunk processing pipeline.

        You must override this method.

        """
        raise NotImplementedError('StreamingCommand.stream(self, records)')

    def _execute(self, operation, reader, writer):
        for record in operation(SearchCommand.records(reader)):
            writer.writerow(record)

    def _prepare(self, argv, input_file):
        ConfigurationSettings = type(self).ConfigurationSettings
        argv = argv[2:]
        if input_file is None:
            reader = None
        else:
            reader = splunk_csv.DictReader(input_file)
        return ConfigurationSettings, self.stream, argv, reader

    #endregion

    class ConfigurationSettings(SearchCommand.ConfigurationSettings):
        """ Represents the configuration settings that apply to a
        :code:`StreamingCommand`.

        """
        #region Properties

        @property
        def local(self):
            """ Specifies whether this command should only be run on the search
            head.

            Default: :const:`False`

            """
            return type(self)._local

        _local = False

        @property
        def overrides_timeorder(self):
            """ Specifies whether this command changes the time ordering of
            event records.

            Default: :const:`False`

            """
            return type(self)._overrides_timeorder

        _overrides_timeorder = False

        @property
        def retainsevents(self):
            """ Specifies whether this command retains _raw events or transforms
            them.

            Default: :const:`True`

            """
            return type(self)._retainsevents

        _retainsevents = True

        @property
        def streaming(self):
            """ Signals that this command is streamable.

            By default streamable commands may be run on the search head or one
            or more indexers, depending on performance scheduling
            considerations. This behavior may be overridden by setting
            :code:`local=True`. This forces a streamable command to be run on the
            search head.

            Fixed: True.

            """
            return True

        #endregion

        #region Methods

        @classmethod
        def fix_up(cls, command):
            """ Verifies :code:`command` class structure.

            """
            if command.stream == StreamingCommand.stream:
                raise AttributeError('No StreamingCommand.stream override')
            return

        #endregion

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
from . import csv


class StreamingCommand(SearchCommand):
    """ Applies a transformation to search results as they travel through the
    processing pipeline

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
    never remotely on indexers:

    ```
    @Configuration(local=False)
    class CountMatchesCommand(StreamingCommand):
        ...
    ```

    If your streaming command modifies the time order of event records you must
    tell Splunk to ensure correct behavior:

    ```
    @Configuration(overrides_timeorder=True)
    class CountMatchesCommand(StreamingCommand):
        ...
    ```

    """
    # TODO: process method implementation
    # TODO: Documentation

    def __init__(self):
        super(StreamingCommand, self).__init__()

    #region Methods

    def stream(self, records):
        raise NotImplementedError('StreamingCommand.stream(self, records)')

    def _prepare(self, argv, input_file):
        configuration = type(self)._configuration
        argv = argv[2:]
        if input_file is None:
            reader = None
        else:
            reader = csv.DictReader(input_file)
        return argv, configuration, self.stream, reader

    def _execute(self, operation, reader, writer):
        try:
            for record in operation(self, SearchCommand.records(reader)):
                writer.writerow(record)
        except Exception as e:
            self.logger.error(e)

    #endregion

    class ConfigurationSettings(SearchCommand.ConfigurationSettings):
        """ TODO: Documentation
        """
        #region Properties

        @property
        def local(self):
            """ TODO: Documentation
            """
            return type(self)._local

        _local = False

        @property
        def overrides_timeorder(self):
            """ TODO: Documentation
            """
            return type(self)._overrides_timeorder

        _overrides_timeorder = False

        @property
        def retainsevents(self):
            """ TODO: Documentation
            """
            return type(self)._retainsevents

        _retainsevents = True

        @property
        def streaming(self):
            """ TODO: Documentation
            """
            return True

        #endregion

        #region Methods

        @classmethod
        def fix_up(cls, command):
            """ TODO: Documentation

            """
            if command.reduce == StreamingCommand.stream:
                raise AttributeError('No StreamingCommand.stream override')
            return

        #endregion

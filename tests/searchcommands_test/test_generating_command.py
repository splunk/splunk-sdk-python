#!/usr/bin/env python
#
# Copyright 2011-2012 Splunk, Inc.
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

from searchcommands_test.utilities import chdir, data_directory, open_data_file
from splunklib.searchcommands import dispatch
import simulate

chdir(simulate)

dispatch(
    simulate.SimulateCommand,
    ['simulate', '__GETINFO__', 'csv=%s/sample.csv' % data_directory,
     'interval=00:00:01', 'rate=200', 'runtime=00:00:10'],
    predicate=lambda x: True)

dispatch(
    simulate.SimulateCommand,
    ['simulate', '__EXECUTE__', 'csv=%s/sample.csv' % data_directory,
     'interval=00:00:01', 'rate=200', 'runtime=00:00:10'],
    input_file=open_data_file('_empty_input_header.txt'),
    predicate=lambda x: True)

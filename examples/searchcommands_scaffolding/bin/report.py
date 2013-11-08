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

from splunklib.searchcommands import \
    dispatch, ReportingCommand, Configuration, Option, validators


@Configuration()
class %(command.title())Command(ReportingCommand):
    """ %(synopsis)

    ##Syntax

    %(syntax)

    ##Description

    %(description)

    """
    @Configuration()
    def map(self, events):
        # Put your streaming preop implementation here, or remove the map method,
        # if you have no need for a streaming preop
        pass

    @Configuration()
    def reduce(self, events):
        # Put your reporting implementation
        pass

dispatch(%(command.title())Command, sys.argv, sys.stdin, sys.stdout, __name__)

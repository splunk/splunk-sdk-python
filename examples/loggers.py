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

"""A command line tool lists out the Splunk logging categories and their
   current logging level."""

import sys
sys.path.insert(0, '../')

import splunklib.client as client

from utils import error, parse

def main(argv):
    usage = "usage: %prog [options]"
    opts = parse(argv, {}, ".splunkrc", usage=usage)
    service = client.connect(**opts.kwargs)

    for logger in service.loggers:
        print "%s (%s)" % (logger.name, logger['level'])

if __name__ == "__main__":
    main(sys.argv[1:])


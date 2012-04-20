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

"""A command line utility for executing oneshot Splunk searches."""

from pprint import pprint
import socket
import sys

from splunklib.client import connect
import splunklib.results as results

import utils

def pretty(response):
    reader = results.ResultsReader(response)
    while True:
        kind = reader.read()
        if kind == None: break
        if kind == results.RESULT:
            event = reader.value
            pprint(event)

def main():
    usage = "usage: oneshot.py <search>"
    opts = utils.parse(sys.argv[1:], {}, ".splunkrc", usage=usage)
    if len(opts.args) != 1:
        utils.error("Search expression required", 2)

    search = opts.args[0]
    service = connect(**opts.kwargs)
    socket.setdefaulttimeout(None)
    response = service.jobs.create(search, exec_mode="oneshot")

    pretty(response)

if __name__ == "__main__":
    main()

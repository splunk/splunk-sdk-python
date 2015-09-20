#!/usr/bin/env python
#
# Copyright 2011-2015 Splunk, Inc.
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
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from splunklib.client import connect
import splunklib.results as results

try:
    import utils
except ImportError:
    raise Exception("Add the SDK repository to your PYTHONPATH to run the examples "
                    "(e.g., export PYTHONPATH=~/splunk-sdk-python.")

def pretty(response):
    reader = results.ResultsReader(response)
    for result in reader:
        if isinstance(result, dict):
            pprint(result)

def main():
    usage = "usage: oneshot.py <search>"
    opts = utils.parse(sys.argv[1:], {}, ".splunkrc", usage=usage)
    if len(opts.args) != 1:
        utils.error("Search expression required", 2)

    search = opts.args[0]
    service = connect(**opts.kwargs)
    socket.setdefaulttimeout(None)
    response = service.jobs.oneshot(search)

    pretty(response)

if __name__ == "__main__":
    main()

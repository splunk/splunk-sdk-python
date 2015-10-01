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

"""A command line utility that uploads a file to Splunk for indexing."""

from os import path
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import splunklib.client as client

try:
    from utils import *
except ImportError:
    raise Exception("Add the SDK repository to your PYTHONPATH to run the examples "
                    "(e.g., export PYTHONPATH=~/splunk-sdk-python.")

RULES = {
    "eventhost": {
        'flags': ["--eventhost"],
        'help': "The event's host value"
    },
    "host_regex": {
        'flags': ["--host_regex"],
        'help': "A regex to use to extract the host value from the file path"
    },
    "host_segment": {
        'flags': ["--host_segment"],
        'help': "The number of the path segment to use for the host value"
    },
    "index": {
        'flags': ["--index"],
        'default': "main",
        'help': "The index name (default main)"
    },
    "rename-source": {
        'flags': ["--source"],
        'help': "The event's source value"
    },
    "sourcetype": {
        'flags': ["--sourcetype"],
        'help': "The event's sourcetype"
    }
}

def main(argv):
    usage = 'usage: %prog [options] <filename>*'
    opts = parse(argv, RULES, ".splunkrc", usage=usage)

    kwargs_splunk = dslice(opts.kwargs, FLAGS_SPLUNK)
    service = client.connect(**kwargs_splunk)

    name = opts.kwargs['index']
    if name not in service.indexes:
        error("Index '%s' does not exist." % name, 2)
    index = service.indexes[name]

    kwargs_submit = dslice(opts.kwargs, 
        {'eventhost': "host"}, 'source', 'host_regex',
        'host_segment', 'rename-source', 'sourcetype')

    for arg in opts.args: 
        fullpath = path.abspath(arg)
        if not path.exists(fullpath):
            error("File '%s' does not exist" % arg, 2)
        index.upload(fullpath, **kwargs_submit)

if __name__ == "__main__":
    main(sys.argv[1:])


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

"""A tool to generate event data to a named index."""

import socket
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import time
import datetime
from splunklib.client import connect
try:
    from utils import parse
except ImportError:
    raise Exception("Add the SDK repository to your PYTHONPATH to run the examples "
                    "(e.g., export PYTHONPATH=~/splunk-sdk-python.")

SPLUNK_HOST = "localhost"
SPLUNK_PORT = 9002

INGEST_TYPE = ["stream", "submit", "tcp"]

RULES = {
   'ingest': {
        'flags': ["--ingest"],
        'default': 'stream',
        'help': "sets the type of ingest to one of %s" % INGEST_TYPE
    },
   'inputhost': {
        'flags': ["--inputhost"],
        'default': "127.0.0.1",
        'help': "input host when using tcp ingest, default is localhost"
    },
   'type': {
        'flags': ["--inputport"],
        'default': SPLUNK_PORT,
        'help': "input host port when using tcp ingest, default is %d" % \
                SPLUNK_PORT
    },
}

def feed_index(service, opts):
    """Feed the named index in a specific manner."""

    indexname = opts.args[0]
    itype = opts.kwargs['ingest']


    # get index handle
    try:
        index = service.indexes[indexname]
    except KeyError:
        print "Index %s not found" % indexname
        return

    if itype in ["stream", "submit"]:
        stream = index.attach()
    else:
        # create a tcp input if one doesn't exist
        input_host = opts.kwargs.get("inputhost", SPLUNK_HOST)
        input_port = int(opts.kwargs.get("inputport", SPLUNK_PORT))
        input_name = "tcp:%s" % (input_port)
        if input_name not in service.inputs.list():
            service.inputs.create("tcp", input_port, index=indexname)
        # connect to socket
        ingest = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ingest.connect((input_host, input_port))

    count = 0
    lastevent = ""
    try:
        for i in range(0, 10):
            for j in range(0, 5000):
                lastevent = "%s: event bunch %d, number %d\n" % \
                             (datetime.datetime.now().isoformat(), i, j)

                if itype == "stream":
                    stream.write(lastevent + "\n")
                elif itype == "submit":
                    index.submit(lastevent + "\n")
                else:
                    ingest.send(lastevent + "\n")

                count = count + 1
            
            print "submitted %d events, sleeping 1 second" % count
            time.sleep(1)
    except KeyboardInterrupt:
        print "^C detected, last event written:"
        print lastevent

def main():
    usage = "usage: %prog [options] <command> [<args>]"

    argv = sys.argv[1:]
    if len(argv) == 0:
        print "must supply an index name"
        sys.exit(1)

    opts = parse(argv, RULES, ".splunkrc", usage=usage)
    service = connect(**opts.kwargs)

    if opts.kwargs['ingest'] not in INGEST_TYPE:
        print "ingest type must be in set %s" % INGEST_TYPE
        sys.exit(1)

    feed_index(service, opts)


if __name__ == "__main__":
    main()


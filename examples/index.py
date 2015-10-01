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

"""A command line utility for interacting with Splunk indexes."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from splunklib.client import connect

try:
    from utils import *
except ImportError:
    raise Exception("Add the SDK repository to your PYTHONPATH to run the examples "
                    "(e.g., export PYTHONPATH=~/splunk-sdk-python.")

HELP_EPILOG = """
Commands:
    clean [<index>]+
    create <index> [options]
    disable [<index>]+
    enable [<index>]+
    list [<index>]*
    update <index> [options]

Examples:
    # Create an index called 'MyIndex'
    index.py create MyIndex

    # Clean index 'MyIndex'
    index.py clean MyIndex

    # Disable indexes 'MyIndex' and 'main'
    index.py disable MyIndex main

    # Enable indexes 'MyIndex' and 'main'
    index.py enable MyIndex main

    # List all indexes
    index.py list

    # List properties of index 'MyIndex'
    index.py list MyIndex
"""

class Program:
    def __init__(self, service):
        self.service = service

    def clean(self, argv):
        self.foreach(argv, lambda index: index.clean())

    def create(self, argv):
        """Create an index according to the given argument vector."""

        if len(argv) == 0: 
            error("Command requires an index name", 2)

        name = argv[0]

        if name in self.service.indexes:
            print "Index '%s' already exists" % name
            return

        # Read index metadata and construct command line parser rules that 
        # correspond to each editable field.

        # Request editable fields
        fields = self.service.indexes.itemmeta().fields.optional

        # Build parser rules
        rules = dict([(field, {'flags': ["--%s" % field]}) for field in fields])

        # Parse the argument vector
        opts = cmdline(argv, rules)

        # Execute the edit request
        self.service.indexes.create(name, **opts.kwargs)

    def disable(self, argv):
        self.foreach(argv, lambda index: index.disable())

    def enable(self, argv):
        self.foreach(argv, lambda index: index.enable())

    def list(self, argv):
        """List available indexes if no names provided, otherwise list the
           properties of the named indexes."""

        def read(index):
            print index.name
            for key in sorted(index.content.keys()): 
                value = index.content[key]
                print "    %s: %s" % (key, value)

        if len(argv) == 0:
            for index in self.service.indexes:
                count = index['totalEventCount']
                print "%s (%s)" % (index.name, count)
        else:
            self.foreach(argv, read)

    def run(self, argv):
        """Dispatch the given command & args."""
        command = argv[0]
        handlers = { 
            'clean': self.clean,
            'create': self.create,
            'disable': self.disable,
            'enable': self.enable,
            'list': self.list,
            'update': self.update,
        }
        handler = handlers.get(command, None)
        if handler is None:
            error("Unrecognized command: %s" % command, 2)
        handler(argv[1:])

    def foreach(self, argv, func):
        """Apply the function to each index named in the argument vector."""
        opts = cmdline(argv)
        if len(opts.args) == 0:
            error("Command requires an index name", 2)
        for name in opts.args:
            if name not in self.service.indexes:
                error("Index '%s' does not exist" % name, 2)
            index = self.service.indexes[name]
            func(index)

    def update(self, argv):
        """Update an index according to the given argument vector."""

        if len(argv) == 0: 
            error("Command requires an index name", 2)
        name = argv[0]

        if name not in self.service.indexes:
            error("Index '%s' does not exist" % name, 2)
        index = self.service.indexes[name]

        # Read index metadata and construct command line parser rules that 
        # correspond to each editable field.

        # Request editable fields
        fields = self.service.indexes.itemmeta().fields.optional

        # Build parser rules
        rules = dict([(field, {'flags': ["--%s" % field]}) for field in fields])

        # Parse the argument vector
        opts = cmdline(argv, rules)

        # Execute the edit request
        index.update(**opts.kwargs)

def main():
    usage = "usage: %prog [options] <command> [<args>]"

    argv = sys.argv[1:]

    # Locate the command
    index = next((i for i, v in enumerate(argv) if not v.startswith('-')), -1)

    if index == -1: # No command
        options = argv
        command = ["list"]
    else:
        options = argv[:index]
        command = argv[index:]

    opts = parse(options, {}, ".splunkrc", usage=usage, epilog=HELP_EPILOG)
    service = connect(**opts.kwargs)
    program = Program(service)
    program.run(command)

if __name__ == "__main__":
    main()



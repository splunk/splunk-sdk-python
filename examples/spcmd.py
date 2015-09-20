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

# This tool basically provides a little sugar on top of the Python interactive
# command interpreter. It establishes a "default" connection and makes the
# properties of that connection ambient. It also picks up known local variables
# and passes those values as options to various commands. For example, you can
# set the default output_mode for a session by simply setting a local variable
# 'output_mode' to a legal output_mode value.

"""An interactive command shell for Splunk.""" 

from code import compile_command, InteractiveInterpreter
try:
    import readline # Activates readline editing, ignore for windows
except ImportError:
    pass
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import splunklib.client as client

try:
    import utils
except ImportError:
    raise Exception("Add the SDK repository to your PYTHONPATH to run the examples "
                    "(e.g., export PYTHONPATH=~/splunk-sdk-python.")

class Session(InteractiveInterpreter):
    def __init__(self, **kwargs):
        self.service = client.connect(**kwargs)
        self.delete = self.service.delete
        self.get = self.service.get
        self.post = self.service.post
        locals = {
            'service': self.service,
            'connect': client.connect,
            'delete': self.delete,
            'get': self.get,
            'post': self.post,
            'load': self.load,
        }
        InteractiveInterpreter.__init__(self, locals)

    def eval(self, expression):
        return self.runsource(expression)

    def load(self, filename):
        exec open(filename).read() in self.locals, self.locals

    # Run the interactive interpreter
    def run(self):
        print "Welcome to Splunk SDK's Python interactive shell"
        print "%s connected to %s:%s" % (
            self.service.username, 
            self.service.host, 
            self.service.port)

        while True:
            try:
                input = raw_input("> ")
            except EOFError:
                print "\n\nThanks for using Splunk>.\n"
                return

            if input is None: 
                return

            if len(input) == 0:
                continue # Ignore

            try:
                # Gather up lines until we have a fragment that compiles
                while True:
                    co = compile_command(input)
                    if co is not None: break
                    input = input + '\n' + raw_input(". ") # Keep trying
            except SyntaxError:
                self.showsyntaxerror()
                continue
            except Exception, e:
                print "Error: %s" % e
                continue

            self.runcode(co)

RULES = {
    "eval": {
        'flags': ["-e", "--eval"],
        'action': "append",
        'help': "Evaluate the given expression",
    },
    "interactive": {
        'flags': ["-i", "--interactive"], 
        'action': "store_true",
        'help': "Enter interactive mode",
    }
}

def actions(opts):
    """Ansers if the given command line options specify any 'actions'."""
    return len(opts.args) > 0 or opts.kwargs.has_key('eval') 

def main():
    opts = utils.parse(sys.argv[1:], RULES, ".splunkrc")

    # Connect and initialize the command session
    session = Session(**opts.kwargs)

    # Load any non-option args as script files
    for arg in opts.args: 
        session.load(arg)

    # Process any command line evals
    for arg in opts.kwargs.get('eval', []): 
        session.eval(arg)

    # Enter interactive mode automatically if no actions were specified or
    # or if interactive mode was specifically requested.
    if not actions(opts) or opts.kwargs.has_key("interactive"):
        session.run()

if __name__ == "__main__":
    main()


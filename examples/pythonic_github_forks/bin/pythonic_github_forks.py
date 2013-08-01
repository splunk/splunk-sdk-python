#!/usr/bin/env python
#
# Copyright 2013 Splunk, Inc.
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

from random import random
import sys, logging, urllib2, json

from splunklib.modularinput.argument import Argument
from splunklib.modularinput.event import Event
from splunklib.modularinput.scheme import Scheme
from splunklib.modularinput.script import Script

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

# set up logging suitable for splunkd consumption
logging.root
logging.root.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(levelname)s %(message)s')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logging.root.addHandler(handler)

def count_forks(owner=None, repo_name=None):
    if owner is None or repo_name is None:
        return None
    else:
        repo_url = "https://api.github.com/repos/%s/%s" % (owner, repo_name)
        response = urllib2.urlopen(repo_url).read()
        jsondata = json.loads(response)
        
        return jsondata["forks_count"]

class MyScript(Script):
    def get_scheme(self):

        scheme = Scheme("Pythonic Github Forks Counter")
        scheme.description = "Generates events containing the number of forks of a Github repository."
        scheme.use_external_validation = True
        scheme.use_single_instance = True

        min_argument = Argument("owner")
        min_argument.data_type = Argument.data_type_number
        min_argument.description = "Github user or organization that created the repository."
        min_argument.required_on_create = True
        scheme.add_argument(min_argument)

        max_argument = Argument("repo_name")
        max_argument.data_type = Argument.data_type_number
        max_argument.description = "Name of the Github repository."
        max_argument.required_on_create = True
        scheme.add_argument(max_argument)

        return scheme

    def validate_input(self, validation_definition):
        owner = validation_definition.parameters["owner"]
        repo_name = validation_definition.parameters["repo_name"]

    def stream_events(self, inputs, ew):

        for input_name in inputs.inputs:
            owner = inputs.inputs[input_name]["owner"]
            repo_name = inputs.inputs[input_name]["repo_name"]

            fork_count = count_forks(owner, repo_name)

            event = Event()
            event.stanza = input_name
            event.data = "repo_url=http://github.com/%s/%s; fork_count=%s" \
                         % (owner, repo_name, fork_count)
            ew.write_event(event)

def do_run(args):
    """
    :param args: list of command line arguments
    """
    #skip first argument "./bin/[this file name].py"
    args = args[1:]

    script = MyScript()
    script.run(args)

if __name__ == "__main__":
    do_run(sys.argv)
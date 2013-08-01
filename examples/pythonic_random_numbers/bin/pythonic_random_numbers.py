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
import sys, logging

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

class MyScript(Script):
    def get_scheme(self):

        scheme = Scheme("Pythonic Random Numbers")
        scheme.description = "Generates events containing a random number, uses the Python SDK."
        scheme.use_external_validation = True
        scheme.use_single_instance = True

        min_argument = Argument("min")
        min_argument.data_type = Argument.data_type_number
        min_argument.description = "Minimum random number to be produced by this input."
        min_argument.required_on_create = True
        scheme.add_argument(min_argument)

        max_argument = Argument("max")
        max_argument.data_type = Argument.data_type_number
        max_argument.description = "Minimum random number to be produced by this input."
        max_argument.required_on_create = True
        scheme.add_argument(max_argument)

        return scheme

    def validate_input(self, validation_definition):
        minimum = float(validation_definition.parameters["min"])
        maximum = float(validation_definition.parameters["max"])

        if minimum >= maximum:
            raise ValueError("min must be less than max; found min=%d, max=%d" % minimum, maximum)

    def stream_events(self, inputs, ew):

        for input_name in inputs.inputs:
            minimum = float(inputs.inputs[input_name]["min"])
            maximum = float(inputs.inputs[input_name]["max"])

            event = Event()
            event.stanza = input_name
            event.data = "number=" + str(random() * (maximum - minimum) + minimum)

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

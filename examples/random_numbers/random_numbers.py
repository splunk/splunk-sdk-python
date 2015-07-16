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

import random, sys

from splunklib.modularinput import *

class MyScript(Script):
    """All modular inputs should inherit from the abstract base class Script
    from splunklib.modularinput.script.
    They must override the get_scheme and stream_events functions, and,
    if the scheme returned by get_scheme has Scheme.use_external_validation
    set to True, the validate_input function.
    """
    def get_scheme(self):
        """When Splunk starts, it looks for all the modular inputs defined by
        its configuration, and tries to run them with the argument --scheme.
        Splunkd expects the modular inputs to print a description of the
        input in XML on stdout. The modular input framework takes care of all
        the details of formatting XML and printing it. The user need only
        override get_scheme and return a new Scheme object.

        :return: scheme, a Scheme object
        """
        # "random_numbers" is the name Splunk will display to users for this input.
        scheme = Scheme("Random Numbers")

        scheme.description = "Streams events containing a random number."
        # If you set external validation to True, without overriding validate_input,
        # the script will accept anything as valid. Generally you only need external
        # validation if there are relationships you must maintain among the
        # parameters, such as requiring min to be less than max in this example,
        # or you need to check that some resource is reachable or valid.
        # Otherwise, Splunk lets you specify a validation string for each argument
        # and will run validation internally using that string.
        scheme.use_external_validation = True
        scheme.use_single_instance = True

        min_argument = Argument("min")
        min_argument.title = "Minimum"
        min_argument.data_type = Argument.data_type_number
        min_argument.description = "Minimum random number to be produced by this input."
        min_argument.required_on_create = True
        # If you are not using external validation, you would add something like:
        #
        # scheme.validation = "min > 0"
        scheme.add_argument(min_argument)

        max_argument = Argument("max")
        max_argument.title = "Maximum"
        max_argument.data_type = Argument.data_type_number
        max_argument.description = "Maximum random number to be produced by this input."
        max_argument.required_on_create = True
        scheme.add_argument(max_argument)

        return scheme

    def validate_input(self, validation_definition):
        """In this example we are using external validation to verify that min is
        less than max. If validate_input does not raise an Exception, the input is
        assumed to be valid. Otherwise it prints the exception as an error message
        when telling splunkd that the configuration is invalid.

        When using external validation, after splunkd calls the modular input with
        --scheme to get a scheme, it calls it again with --validate-arguments for
        each instance of the modular input in its configuration files, feeding XML
        on stdin to the modular input to do validation. It is called the same way
        whenever a modular input's configuration is edited.

        :param validation_definition: a ValidationDefinition object
        """
        # Get the parameters from the ValidationDefinition object,
        # then typecast the values as floats
        minimum = float(validation_definition.parameters["min"])
        maximum = float(validation_definition.parameters["max"])

        if minimum >= maximum:
            raise ValueError("min must be less than max; found min=%f, max=%f" % minimum, maximum)

    def stream_events(self, inputs, ew):
        """This function handles all the action: splunk calls this modular input
        without arguments, streams XML describing the inputs to stdin, and waits
        for XML on stdout describing events.

        If you set use_single_instance to True on the scheme in get_scheme, it
        will pass all the instances of this input to a single instance of this
        script.

        :param inputs: an InputDefinition object
        :param ew: an EventWriter object
        """
        # Go through each input for this modular input
        for input_name, input_item in inputs.inputs.iteritems():
            # Get the values, cast them as floats
            minimum = float(input_item["min"])
            maximum = float(input_item["max"])

            # Create an Event object, and set its data fields
            event = Event()
            event.stanza = input_name
            event.data = "number=\"%s\"" % str(random.uniform(minimum, maximum))

            # Tell the EventWriter to write this event
            ew.write_event(event)

if __name__ == "__main__":
    sys.exit(MyScript().run(sys.argv))

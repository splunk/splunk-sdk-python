# Copyright 2011-2013 Splunk, Inc.
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

from abc import ABCMeta, abstractmethod
from splunklib.modularinput.input_definition import InputDefinition
from splunklib.modularinput.validation_definition import ValidationDefinition
from splunklib.modularinput.event_writer import EventWriter
import sys

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET


class Script(object):
    """An abstract base class for implementing modular inputs.

    Subclasses should override get_scheme, stream_events,
    and optional validate_input if the modular Input uses
    external validation.

    The important function is run, which is used to run modular inputs
    """
    __metaclass__ = ABCMeta

    def run(self, args):
        """This function is stable, call run to run a modular input

        :param args: String[] args from Java
        :return:
        """
        return self.run_script(args, EventWriter(), sys.stdin)

    def run_script(self, args, event_writer, input_stream):
        """Handles all the specifics of running a modular input

        :param args:
        :param event_writer:
        :param input_stream:
        :return:
        """

        try:
            if len(args) == 0:
                # This script is running as an input. Input definitions will be passed on stdin
                # as XML, and the script will write events on stdout and log entries on stderr.
                input_definition = InputDefinition.parse_input_definition(input_stream)
                self.stream_events(input_definition, event_writer)
                event_writer.close()
                return 0

            elif str(args[0]).lower() == "--scheme":
                # Splunk has requested XML specifying the scheme for this modular input.
                # Return it and exit.
                scheme = self.get_scheme()
                if scheme is None:
                    event_writer.log(EventWriter.FATAL, "Modular input script returned a null scheme.")
                    return 1
                else:
                    event_writer.write_xml_document(scheme.to_xml())
                    return 0

            elif args[0].lower() == "--validate-arguments":
                validation_definition = ValidationDefinition.parse_validation_definition(input_stream)
                try:
                    self.validate_input(validation_definition)
                    return 0
                except Exception as e:
                    root = ET.Element("error")
                    ET.SubElement(root, "message").text = e.message
                    event_writer.write_xml_document(root)

                    return 1

            err_string = "ERROR Invalid arguments to modular input script:" + ' '.join(args)
            event_writer._err.write(err_string)

        except Exception as e:
            err_string = EventWriter.ERROR + e.message
            event_writer._err.write(err_string)
            return 1

    @abstractmethod
    def get_scheme(self):
        """The scheme defines the parameters understood by this modular input.

        :return: a Scheme object representing the parameters for this modular input
        """

    def validate_input(self, definition):
        """Handles external validation for modular input kinds. When Splunk
        called a modular input script in validation mode, it will pass in an XML document
        giving information about the Splunk instance (so you can call back into it if needed)
        and the name and parameters of the proposed input.

        If this function does not throw an exception, the validation is assumed to succeed.
        Otherwise any error throws will be turned into a string and logged back to Splunk.

        The default implementation always passes.

        :param definition: The parameters for the proposed input passed by splunkd
        """
    @abstractmethod
    def stream_events(self, inputs, ew):
        """The method called to stream events into Splunk. It should do all of its output via
        EventWriter rather than assuming that there is a console attached.

        :param inputs: an InputDefinition object
        :param ew: an object with methods to write events and log messages to Splunk
        """
        return

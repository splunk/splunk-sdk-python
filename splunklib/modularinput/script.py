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

from __future__ import absolute_import
from splunklib.six.moves.urllib.parse import urlsplit
import sys

from ..client import Service
from .event_writer import EventWriter
from .input_definition import InputDefinition
from .validation_definition import ValidationDefinition
from splunklib import six

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET


class Script(object):
    """A base class for implementing modular inputs.

    Subclasses should override ``get_scheme``, ``stream_events``,
    and optionally ``validate_input`` if the modular input uses
    external validation.

    The ``run`` function is used to run modular inputs; it typically should
    not be overridden.
    """

    def __init__(self):
        self._input_definition = None
        self._service = None

    def run(self, args):
        """Runs this modular input

        :param args: List of command line arguments passed to this script.
        :returns: An integer to be used as the exit value of this program.
        """

        # call the run_script function, which handles the specifics of running
        # a modular input
        return self.run_script(args, EventWriter(), sys.stdin)

    def run_script(self, args, event_writer, input_stream):
        """Handles all the specifics of running a modular input

        :param args: List of command line arguments passed to this script.
        :param event_writer: An ``EventWriter`` object for writing events.
        :param input_stream: An input stream for reading inputs.
        :returns: An integer to be used as the exit value of this program.
        """

        try:
            if len(args) == 1:
                # This script is running as an input. Input definitions will be
                # passed on stdin as XML, and the script will write events on
                # stdout and log entries on stderr.
                self._input_definition = InputDefinition.parse(input_stream)
                self.stream_events(self._input_definition, event_writer)
                event_writer.close()
                return 0

            elif str(args[1]).lower() == "--spec":
                scheme = self.get_scheme()
                print("[{0}]".format(self.name))
                for argument in scheme.arguments:
                    print("{0} = <{1}>".format(argument.name, argument.data_type.lower()))
                return 0
            elif str(args[1]).lower() == "--scheme":
                # Splunk has requested XML specifying the scheme for this
                # modular input Return it and exit.
                scheme = self.get_scheme()
                if scheme is None:
                    event_writer.log(
                        EventWriter.FATAL,
                        "Modular input script returned a null scheme.")
                    return 1
                else:
                    event_writer.write_xml_document(scheme.to_xml())
                    return 0

            elif args[1].lower() == "--validate-arguments":
                validation_definition = ValidationDefinition.parse(input_stream)
                try:
                    self.validate_input(validation_definition)
                    return 0
                except Exception as e:
                    root = ET.Element("error")
                    ET.SubElement(root, "message").text = str(e)
                    event_writer.write_xml_document(root)

                    return 1
            else:
                err_string = "ERROR Invalid arguments to modular input script:" + ' '.join(
                    args)
                event_writer._err.write(err_string)
                return 1

        except Exception as e:
            err_string = EventWriter.ERROR + str(e)
            event_writer._err.write(err_string)
            return 1

    @property
    def service(self):
        """ Returns a Splunk service object for this script invocation.

        The service object is created from the Splunkd URI and session key
        passed to the command invocation on the modular input stream. It is
        available as soon as the :code:`Script.stream_events` method is
        called.

        :return: :class:`splunklib.client.Service`. A value of None is returned,
            if you call this method before the :code:`Script.stream_events` method
            is called.

        """
        if self._service is not None:
            return self._service

        if self._input_definition is None:
            return None

        splunkd_uri = self._input_definition.metadata["server_uri"]
        session_key = self._input_definition.metadata["session_key"]

        splunkd = urlsplit(splunkd_uri, allow_fragments=False)

        self._service = Service(
            scheme=splunkd.scheme,
            host=splunkd.hostname,
            port=splunkd.port,
            token=session_key,
        )

        return self._service

    # decorating a Script adds a valid decorated_get_scheme function
    def decorated_get_scheme(self):
        raise NotImplementedError('Script.get_scheme(self)')

    # overriding get_scheme results in decorated_get_scheme not being called
    def get_scheme(self):
        """The scheme defines the parameters understood by this modular input.

        You must override this method or use the Configuration decorator to use the auto-scheme.

        :return: a ``Scheme`` object representing the parameters for this modular input.
        """
        return self.decorated_get_scheme()

    def validate_input(self, definition):
        """Handles external validation for modular input kinds.

        When Splunk calls a modular input script in validation mode, it will
        pass in an XML document giving information about the Splunk instance (so
        you can call back into it if needed) and the name and parameters of the
        proposed input.

        If this function does not throw an exception, the validation is assumed
        to succeed. Otherwise any errors thrown will be turned into a string and
        logged back to Splunk.

        The default implementation always passes.

        :param definition: The parameters for the proposed input passed by splunkd.
        """
        pass

    # if Script.decorated_stream_events is called it means stream_events wasn't overridden and the class wasn't decorated
    def decorated_stream_events(self, inputs, ew):
        raise NotImplementedError('Script.stream_events(self, inputs, ew)')

    # in Script we define stream_events to call decorated_stream_events.  stream_events should either be overridden or the class should be decorated
    # to create decorated_stream_events (which calls preflight, process_input, postflight)
    def stream_events(self, inputs, ew):
        self.decorated_stream_events(inputs, ew)

    # preflight is called before each input is called with process_input
    def preflight(fn_self, inputs, ew):
        pass

    # process_input is called once per input.  it should be overridden when the class is decorated
    def process_input(fn_self, input_name, input_item, ew):
        raise Exception("Not Implemented: Script.process_input(self, input_name, input_item, ew)")

    # postflight is called after each input is called with process_input
    def postflight(fn_self, inputs, ew):
        pass

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

from splunklib.modularinput.event import Event, ET, StringIO
import sys

class EventWriter(object):
    """EventWriter writes events and error messages to Splunk from a modular input."""
    def __init__(self, output = sys.stdout, error = sys.stderr):
        """
        :param output: where to write the output, defaults to sys.stdout
        :param error:
        """
        # The severities that Splunk understands for log messages from modular inputs.
        self.DEBUG = "DEBUG"
        self.INFO = "INFO"
        self.WARN = "WARN"
        self.ERROR = "ERROR"
        self.FATAL = "FATAL"

        self.output_writer = output
        self.error_writer = error

        self.header_written = False

    def write_event(self, event):
        """Write an Event object to Splunk.

        :param event: an Event object
        """

        if not self.header_written:
            self.output_writer.write("<stream>")
            self.header_written = True
        #try:
        event.write_to(self.output_writer)
        #except ValueError as ve:
            #self.log(self.WARN, ve.message)

    def log(self, severity, message):
        """Log messages about the state of this modular input to Splunk. These messages will show up in Splunk's
        internal logs

        :param severity: string, severity of message, see severites in __init__
        :param message: message to log
        """

        self.error_writer.write("%s %s\n" % (severity, message))
        self.error_writer.flush()

    def write_xml_document(self, document):
        """Write an ElementTree to the output stream

        :param document: an ElementTree object
        """
        stream = StringIO.StringIO()
        stream.write(ET.tostring(document, "us-ascii", "xml"))
        stream.flush()
        self.output_writer.write(stream.getvalue())
        self.output_writer.flush()

    def close(self):
        """Write the closing </stream> tag to make this XML well formed."""
        self.output_writer.write("</stream>")
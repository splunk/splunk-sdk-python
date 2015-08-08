# Copyright 2011-2014 Splunk, Inc.
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
import logging
from sys import stdout
import splunklib.common.logging

from splunklib.modularinput.event import ET

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO


class EventWriter(object):
    """``EventWriter`` writes events and error messages to Splunk from a modular input.

    Its two important methods are ``writeEvent``, which takes an ``Event`` object,
    and ``log``, which takes a severity and an error message.
    """

    # Severities that Splunk understands for log messages from modular inputs.
    # DEBUG = "DEBUG"
    # INFO = "INFO"
    # WARN = "WARN"
    # ERROR = "ERROR"
    # FATAL = "FATAL"

    # CHANGED TO NUMERIC to make them more compatible with the builtin python logging module
    # Do not change these
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARN = logging.WARN
    ERROR = logging.ERROR
    FATAL = logging.FATAL

    _levelNames = {
        'FATAL': logging.CRITICAL,
        'CRITICAL': logging.CRITICAL,
        'ERROR': logging.ERROR,
        'WARN': logging.WARNING,
        'WARNING': logging.WARNING,
        'INFO': logging.INFO,
        'DEBUG': logging.DEBUG,
    }

    # This provides compatibility with python logging AND the former EventWriter...
    @staticmethod
    def get_logging_level(level, message):
        """Takes a (string or int) level and a message and converts the level.

        If the level is one of the valid EventWriter strings, it will be converted to the corresponding logging level,
        and the message will be returned unmodified.

        If the level is an integer level, both the level and message will be returned unmodified.

        If the level is another string, it will be prepended to the message, and logging.ERROR will be returned.

        This means that if you use EventWriter.log() as though it were logging.log ... it will work correctly, and you
        can still use logging.addLevelName etc. We also preserves compatibility with previous EventWriter.log and string
        messages.
        """
        level = EventWriter._levelNames.get(level, level)
        if not isinstance(level, int):
            message = str(level) + " " + message
            level = logging.ERROR
        return level, message

    def __init__(self, output=stdout, logger=None):
        """Initialize the EventWriter and a logger instance for it
        :param output:``stream``, Where output will go. Defaults to sys.stdout
        :param logger: ``logger``, Where .log messages will go. By default, calls splunklib.common.logging getLogger.
        """
        splunklib.common.logging.configureLogging()
        self._out = output
        self._logger = logger or splunklib.common.logging.getLogger()

        # has the opening <stream> tag been written yet?
        self.header_written = False

        # self._out.write("<stream>")

    def write_event(self, event):
        """Writes an ``Event`` object to Splunk.

        :param event: An ``Event`` object.
        """

        if not self.header_written:
            self._out.write("<stream>")
            self.header_written = True

        event.write_to(self._out)

    def log(self, severity, message, *args, **kwargs):
        """Logs 'message % args' information about the state of this modular input to Splunk.
        These messages will show up in Splunk's _internal index.

        To pass exception information, use the keyword argument exc_info with a true value, e.g.

        event_writer.log(level, "We have a %s", "mysterious problem", exc_info=1)

        :param severity: ``string``, severity of message, see severities defined as class constants.
        :param message: ``string``, message template to log.
        :param args: ``object array``, objects which will be inserted to the message string
        :param kwargs: ``object dictionary``, objects which will be inserted to the message string
        """
        level, message = EventWriter.get_logging_level(severity, message)
        self._logger.log(level, message, *args, **kwargs)

        #self._logger.log(level, message, args, **kwargs)

    def write_xml_document(self, document):
        """Writes a string representation of an
        ``ElementTree`` object to the output stream.

        :param document: An ``ElementTree`` object.
        """
        self._out.write(ET.tostring(document))
        self._out.flush()

    def close(self):
        """Write the closing </stream> tag to make this XML well formed."""
        self._out.write("</stream>")
        self._out.flush()

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

import sys, time

try:
    import xml.etree.cElementTree as ET
except ImportError as ie:
    import xml.etree.ElementTree as ET

try:
    import cStringIO as StringIO
except ImportError as ie:
    import StringIO

class Event(object):
    """Represents an event or fragment of an event to be written by this modular input to Splunk."""
    def __init__(self):
        self.data = None
        self.done = True
        self.host = None
        self.index = None
        self.source = None
        self.sourceType = None
        self.stanza = None
        self.time = None
        self.unbroken = True

    def write_to(self, stream):
        """Write an XML representation of self, an Event, to the given stream

        :param stream: stream to write XML to
        """
        if not self.data:
            raise ValueError("Events must have at least the data field set to be written to XML.")

        event = ET.Element("event")
        if self.stanza:
            event.set("stanza", self.stanza)
        event.set("unbroken", str(int(self.unbroken)))

        if(self.time):
            epoch_time = self.time
        else:
            epoch_time = time.time()

        create_subelement(event, "time", str(epoch_time))
        create_subelement(event, "source", self.source)
        create_subelement(event, "sourceType", self.sourceType)
        create_subelement(event, "index", self.index)
        create_subelement(event, "host", self.host)
        create_subelement(event, "data", self.data)

        if not self.unbroken and self.done:
            done = ET.SubElement(event, "done")

        stream.write(ET.tostring(event))
        sys.stdout.flush()

def create_subelement(parent, name, text):
    """Create an XML subelement with tag and text specified

    :param parent: parent XML element
    :param name: name of XML node tag
    :param text: text to go inside <name>
    """
    if not text:
        return
    subelement = ET.SubElement(parent, name)
    subelement.text = text
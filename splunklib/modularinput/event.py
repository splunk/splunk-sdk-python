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

try:
    import xml.etree.cElementTree as ET
except ImportError as ie:
    import xml.etree.ElementTree as ET

#todo: extend the docs. What would you want to know about this class if you were faced with it for the first time and had to use it?

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

        # if a time isn't set, let Splunk guess by not creating a <time> element
        if self.time:
            ET.SubElement(event, "time").text = str(self.time)

        # add all other subelements to this event
        subElements = [
            ("source", self.source),
            ("sourceType", self.sourceType),
            ("index", self.index),
            ("host", self.host),
            ("data", self.data)
        ]
        for node, value in subElements:
            if value:
                ET.SubElement(event, node).text = value

        if self.done:
            done = ET.SubElement(event, "done")

        stream.write(ET.tostring(event))
        stream.flush()
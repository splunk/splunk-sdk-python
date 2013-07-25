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

from splunklib.modularinput.argument import Argument

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

#TODO: extend docs

class Scheme(object):
    """Class representing the metadata for a modular input kind."""
    def __init__(self, title):
        """
        :param title: string identifier for this Scheme in Splunk
        """
        self.title = title
        self.description = None
        self.useExternalValidation = True
        self.useSingleInstance = False

        # Constant values, do not change
        self.streamingModeSimple = "SIMPLE"
        self.streamingModeXML = "XML"

        self.streamingMode = self.streamingModeXML

        #List of Argument objects
        self.arguments = []

    def addArgument(self, arg):
        """Add the provided argument, arg, to self.arguments

        :param arg: an Argument object to add to self.arguments
        """
        self.arguments.append(arg)

    def toXML(self):
        """Creates an ET.Element representing this scheme, then returns it

        :return root, an ET.Element representing this scheme
        """
        root = ET.Element("scheme")

        title = ET.SubElement(root, "title")
        title.text = self.title

        if self.description:
            description = ET.SubElement(root, "description")
            description.text = self.description

        use_external_validation = ET.SubElement(root, "use_external_validation")
        use_external_validation.text = str(self.useExternalValidation).lower()

        use_single_instance = ET.SubElement(root, "use_single_instance")
        use_single_instance.text = str(self.useSingleInstance).lower()

        streaming_mode = ET.SubElement(root, "streaming_mode")
        streaming_mode.text = self.streamingMode.lower()

        endpoint = ET.SubElement(root, "endpoint")

        args = ET.SubElement(endpoint, "args")

        for arg in self.arguments:
            arg.addToDocument(args)

        return root
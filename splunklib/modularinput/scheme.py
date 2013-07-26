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
except ImportError:
    import xml.etree.ElementTree as ET

class Scheme(object):
    """Class representing the metadata for a modular input kind.

    A Scheme specifies a title, description, several options of how Splunk should run modular inputs of this
    kind, and a set of arguments which define a particular modular input's properties.

    The primary use of Scheme is to abstract away the construction of XML to feed to Splunk.
    """

    # Constant values, do not change
    streamingModeSimple = "SIMPLE"
    streamingModeXML = "XML"

    def __init__(self, title):
        """
        :param title: string identifier for this Scheme in Splunk
        """
        self.title = title
        self.description = None
        self.useExternalValidation = True
        self.useSingleInstance = False
        self.streamingMode = Scheme.streamingModeXML

        # list of Argument objects, each to be represented by an <arg> tag
        self.arguments = []

    def add_argument(self, arg):
        """Add the provided argument, arg, to the self.arguments list

        :param arg: an Argument object to add to self.arguments
        """
        self.arguments.append(arg)

    def to_XML(self):
        """Creates an ET.Element representing self, then returns it

        :return root, an ET.Element representing this scheme
        """
        root = ET.Element("scheme")

        title = ET.SubElement(root, "title")
        title.text = self.title

        # add a description subelement if it's defined
        if self.description is not None:
            description = ET.SubElement(root, "description")
            description.text = self.description

        # add other subelements
        use_external_validation = ET.SubElement(root, "use_external_validation")
        use_external_validation.text = str(self.useExternalValidation).lower()

        use_single_instance = ET.SubElement(root, "use_single_instance")
        use_single_instance.text = str(self.useSingleInstance).lower()

        streaming_mode = ET.SubElement(root, "streaming_mode")
        streaming_mode.text = self.streamingMode.lower()

        endpoint = ET.SubElement(root, "endpoint")

        args = ET.SubElement(endpoint, "args")

        # add arguments as subelements to the <args> element
        for arg in self.arguments:
            arg.add_to_document(args)

        return root
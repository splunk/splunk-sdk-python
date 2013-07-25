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
    import xml.etree.ElementTree as ET
except ImportError:
    import xml.etree.cElementTree as ET

#TODO: extend docs

class Argument(object):
    """Class representing an argument to a modular input kind."""
    def __init__(self, name):
        """
        :param name: string identifier for this argument in Splunk
        """
        self.name = name
        self.description = None
        self.validation = None

        # Constant values, do not change
        self.dataTypeBoolean = "BOOLEAN"
        self.dataTypeNumber = "NUMBER"
        self.dataTypeString = "STRING"

        self.dataType = self.dataTypeString

        self.requiredOnEdit = False
        self.requiredOnCreate = False

    def addToDocument(self, parent):
        """Adds an <arg> SubElement to the Parent Element, typically <args>

        :param parent: an ET.Element to be the parent of a new <arg> SubElement
        :return: an ET.Element object representing this argument #TODO: might not need to return here..
        """
        arg = ET.SubElement(parent, "arg")
        arg.set("name", self.name)

        if self.description:
            description = ET.SubElement(arg, "description")
            description.text = self.description

        if self.validation:
            validation = ET.SubElement(arg, "validation")
            validation.text = self.validation

        data_type = ET.SubElement(arg, "data_type")
        data_type.text = self.dataType.lower()

        required_on_edit = ET.SubElement(arg, "required_on_edit")
        required_on_edit.text = str(self.requiredOnEdit).lower()

        required_on_create = ET.SubElement(arg, "required_on_create")
        required_on_create.text = str(self.requiredOnCreate).lower()

        return arg
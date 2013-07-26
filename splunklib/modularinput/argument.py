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

class Argument(object):
    """Class representing an argument to a modular input kind.
    Argument is meant to be used with Scheme to generate an XML definition of the modular input
    kind that Splunk understands."""

    # Constant values, do not change
    dataTypeBoolean = "BOOLEAN"
    dataTypeNumber = "NUMBER"
    dataTypeString = "STRING"

    def __init__(self, name, description=None, validation=None, \
                 dataType=dataTypeString, requiredOnEdit=False, requiredOnCreate=False):
        """name is the only required parameter for the constructor

        Example with least parameters:

            arg1 = Argument(name="arg1")

        Example with all parameters:

            arg2 = Argument(
                name="arg2",
                description="This is an argument with lots of parameters",
                validation="is_pos_int('some_name')",
                dataType=Argument.dataTypeNumber,
                requiredOnEdit=True,
                requiredOnCreate=True
            )

        :param name: string, identifier for this argument in Splunk
        :param description: string, human readable description of the argument
        :param validation: string, specifying how the argument should be validated, if using internal validation. If using
        external validation, this will be ignored.
        :param dataType: string, data type of this field; use the class constants
        dataTypeBoolean, dataTypeNumber, or dataTypeString
        :param requiredOnEdit: boolean, is this arg required when editing an existing modular input of this kind?
        :param requiredOnCreate: boolean, is this arg required when creating a modular input of this kind?
        """
        self.name = name
        self.description = description
        self.validation = validation
        self.dataType = dataType
        self.requiredOnEdit = requiredOnEdit
        self.requiredOnCreate = requiredOnCreate

    def add_to_document(self, parent):
        """Adds an <arg> SubElement to the Parent Element, typically <args>
        and setup its subelements with their respective text

        :param parent: an ET.Element to be the parent of a new <arg> SubElement
        :return: an ET.Element object representing this argument #TODO: might not need to return here..
        """
        arg = ET.SubElement(parent, "arg")
        arg.set("name", self.name)

        if self.description is not None:
            ET.SubElement(arg, "description").text = self.description

        if self.validation:
            ET.SubElement(arg, "validation").text = self.validation

        ET.SubElement(arg, "data_type").text = self.dataType.lower()
        ET.SubElement(arg, "required_on_edit").text = str(self.requiredOnEdit).lower()
        ET.SubElement(arg, "required_on_create").text = str(self.requiredOnCreate).lower()

        return arg
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
from malformed_data_exception import MalformedDataException

class ValidationDefinition(object):
    """
    This class represents the XML sent by Splunk for external validation of a new modular input.

    **Example**::

        v = ValidationDefinition()
    """
    def __init__(self):
        self.metadata = {}
        self.parameters = {}

    def parseDefintion(self, stream):
        """
        Creates a ValidationDefinition from a provided stream containing XML.
        The XML typically will look like

        <items>
            <server_host>myHost</server_host>
            <server_uri>https://127.0.0.1:8089</server_uri>
            <session_key>123102983109283019283</session_key>
            <checkpoint_dir>/opt/splunk/var/lib/splunk/modinputs</checkpoint_dir>
            <item name="myScheme">
                <param name="param1">value1</param>
                <param_list name="param2">
                    <value>value2</value>
                    <value>value3</value>
                    <value>value4</value>
                </param_list>
            </item>
        </items>

        :param stream: stream containing XML to parse
        :return definition: a ValidationDefinition object
        """
        try:
            definition = ValidationDefinition()

            # parse XML from the stream, then get the root node
            root = ET.parse(stream).getroot()

            for node in root:
                # lone item node
                if node.tag == "item":
                    # name from item node
                    definition.metadata["name"] = node.get("name")
                    for param_node in node:
                        # single value params
                        if param_node.tag == "param":
                            definition.parameters[param_node.get("name")] = param_node.text
                        # multi-value params
                        elif param_node.tag == "param_list":
                            definition.parameters[param_node.get("name")] = []
                            for multi_val_param in param_node:
                                definition.parameters[param_node.get("name")].append(multi_val_param.text)
                        else:
                            raise MalformedDataException("Invalid configuration scheme, %s tag unexpected." % param_node.tag)
                else:
                    # Store anything else in metadata
                    definition.metadata[node.tag] = node.text
            return definition
        except Exception as e:
            raise Exception, "Error getting validation definition: %s" % str(e)

    def __eq__(self, other):
        """
        Test the equality of self and other by comparing metadata and parameters

        :param other: a ValidationDefinition object
        :return boolean: True for equality, else False
        """
        if not isinstance(other, ValidationDefinition):
            return False
        return self.metadata == other.metadata and self.parameters == other.parameters
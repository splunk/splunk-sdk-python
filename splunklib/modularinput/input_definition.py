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

class InputDefinition:
    """ InputDefinition encodes the XML defining inputs that Splunk passes to
        a modular input script

        ``InputDefinition`` takes no arguments.

         **Example**::

            i = InputDefinition()

    """
    def __init__ (self):
        self.metadata = {}
        self.inputs = {}

    def parseDefinition(self, stream):
        """ Parse a stream containing XML into an InputDefinition.

        :param stream: stream containing XML to parse
        :return: definition: a InputDefinition object
        """
        if not isinstance(stream, file):
            raise ValueError("Stream is invalid, cannot be parsed")
        try:
            definition = InputDefinition()

            # read everything from the stream
            config_str = stream.read()

            # parse the configuration XML
            root = ET.fromstring(config_str)
            for node in root:
                if node.tag == "configuration":
                    # get config for each stanza
                    for config_stanza in node:
                        if config_stanza.tag == "stanza":
                            definition.inputs[config_stanza.get("name")] = {}

                            for param in config_stanza:
                                definition.parseParameters(param, config_stanza.get("name"))
                        else:
                            raise MalformedDataException, "Invalid configuration scheme, "+config_stanza.tag+" tag unexpected."
                else:
                    definition.metadata[node.tag] = node.text
            return definition
        except MalformedDataException:
            raise
        except Exception, e:
            raise Exception, "Error getting configuration: %s" % str(e)

    def parseParameters(self, paramNode, stanzaName):
        """A helper function to clean up the code for parsing XML parameters

        :param paramNode: XML node, it should have param or param_list tag
        :param stanzaName: string of the stanza name containing the node
        """
        if paramNode.tag == "param":
            self.inputs[stanzaName][paramNode.get("name")] = paramNode.text
        elif paramNode.tag == "param_list":
            self.inputs[stanzaName][paramNode.get("name")] = []
            # multi-value parameters
            for mvp in paramNode:
                self.inputs[stanzaName][paramNode.get("name")].append(mvp.text)
        else:
            raise MalformedDataException, "Invalid configuration scheme, "+paramNode.tag+" tag unexpected."


    def __eq__(self,other):
        if not isinstance(other, InputDefinition):
            return False
        return self.metadata == other.metadata and self.inputs == other.inputs
#!/usr/bin/env python
#
# Copyright 2011-2012 Splunk, Inc.
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

# Utility file for common functions and imports

try:
    import unittest2 as unittest
except ImportError:
    import unittest
import sys, os

sys.path.insert(0, os.path.join('../../splunklib', '..'))

# utility functions

def parse_parameters(paramNode):
    if paramNode.tag == "param":
        return paramNode.text
    elif paramNode.tag == "param_list":
        parameters = []
        for mvp in paramNode:
            parameters.append(mvp.text)
        return parameters
    else:
        raise ValueError("Invalid configuration scheme, %s tag unexpected." % paramNode.tag)

def parse_xml_data(parent_node, child_node_tag):
    data = {}
    for child in parent_node:
        if child.tag == child_node_tag:
            if child_node_tag == "stanza":
                data[child.get("name")] = {}
                for param in child:
                    data[child.get("name")][param.get("name")] = parse_parameters(param)
        elif "item" == parent_node.tag:
            data[child.get("name")] = parse_parameters(child)
    return data

def xml_compare(expected, found):
    """Checks equality of two ElementTrees

    :param expected: an ElementTree object
    :param found: an ElementTree object
    :return: boolean, equality of expected and found
    """

    # if comparing the same ET object
    if expected == found:
        return True

    # compare element attributes, ignoring order
    if set(expected.items()) != set(found.items()):
        return False

    # check for equal number of children
    expected_children = list(expected)
    found_children = list(found)
    if len(expected_children) != len(found_children):
        return False


    #todo: uncomment this bit, remove import & explicit loop
    # compare children
    #if not all([xml_compare(a, b) for a, b in zip(expected_children, found_children)]):
    #    return False

    import xml.etree.ElementTree as ET

    for i, child in enumerate(expected_children):
        if not xml_compare(child, found_children[i]):
            return False

    # compare element text if it exists, else elements are equal
    if expected.text and expected.text.strip() != "":
        if expected.tag == found.tag and expected.text == found.text:
            if expected.attrib == found.attrib:
                return True
            else:
                return False
        else:
            return False
    else:
        return True
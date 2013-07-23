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

#Utility file for common functions and imports

try:
    import unittest2 as unittest
except ImportError:
    import unittest
import sys, os

sys.path.insert(0, os.path.join('..', '..'))

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

def parse_xml_data(parentNode, childNodeTag):
    data = {}
    for child in parentNode:
        if child.tag == childNodeTag:
            if childNodeTag == "stanza":
                data[child.get("name")] = {}
                for param in child:
                    data[child.get("name")][param.get("name")] = parse_parameters(param)
        elif "item" == parentNode.tag:
            data[child.get("name")] = parse_parameters(child)
    return data
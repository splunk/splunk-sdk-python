#!/usr/bin/env python
#
# Copyright 2011-2015 Splunk, Inc.
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

# Utility file for unit tests, import common functions and modules
from __future__ import absolute_import

try:
    import unittest2 as unittest
except ImportError:
    import unittest

import io
import os
import sys

sys.path.insert(0, os.path.join("../../splunklib", ".."))

from splunklib.modularinput.utils import parse_parameters, parse_xml_data, xml_compare


def data_open(filepath):
    return io.open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), filepath), "rb"
    )

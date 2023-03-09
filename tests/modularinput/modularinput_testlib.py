#!/usr/bin/env python
#
# Copyright © 2011-2023 Splunk, Inc.
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

import io
import os
import sys
import unittest

sys.path.insert(0, os.path.join('../../splunklib', '..'))

from splunklib.modularinput.utils import xml_compare, parse_xml_data, parse_parameters

def data_open(filepath):
    return io.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), filepath), 'rb')

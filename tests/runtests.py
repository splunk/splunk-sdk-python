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

"""Runs all the Splunk Python SDK unit tests."""

import os
import sys
import unittest

# Set up the environment for coverage, even though it might not get used
os.environ["COVERAGE_PROCESS_START"] = "../tests/.coveragerc"

unittest.TextTestRunner().run(unittest.TestLoader().discover('.'))


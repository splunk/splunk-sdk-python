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

"""Runs all the Splunk SDK for Python unit tests."""

import os
try:
    import unittest2 as unittest  # We must be sure to get unittest2--not unittest--on Python 2.6
except ImportError:
    import unittest

os.chdir(os.path.dirname(os.path.abspath(__file__)))
suite = unittest.defaultTestLoader.discover('.')

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite)
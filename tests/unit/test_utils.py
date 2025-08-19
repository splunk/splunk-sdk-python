#!/usr/bin/env python
#
# Copyright © 2011-2025 Splunk, Inc.
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

import os
from pathlib import Path
import unittest

from utils import dslice

TEST_DICT = {
    "username": "admin",
    "password": "changeme",
    "port": 8089,
    "host": "localhost",
    "scheme": "https",
}


class TestUtils(unittest.TestCase):
    # Test dslice when a dict is passed to change key names
    def test_dslice_dict_args(self):
        args = {
            "username": "user-name",
            "password": "new_password",
            "port": "admin_port",
            "foo": "bar",
        }
        expected = {
            "user-name": "admin",
            "new_password": "changeme",
            "admin_port": 8089,
        }
        self.assertTrue(expected == dslice(TEST_DICT, args))

    # Test dslice when a list is passed
    def test_dslice_list_args(self):
        test_list = ["username", "password", "port", "host", "foo"]
        expected = {
            "username": "admin",
            "password": "changeme",
            "port": 8089,
            "host": "localhost",
        }
        self.assertTrue(expected == dslice(TEST_DICT, test_list))

    # Test dslice when a single string is passed
    def test_dslice_arg(self):
        test_arg = "username"
        expected = {"username": "admin"}
        self.assertTrue(expected == dslice(TEST_DICT, test_arg))

    # Test dslice using all three types of arguments
    def test_dslice_all_args(self):
        test_args = [{"username": "new_username"}, ["password", "host"], "port"]
        expected = {
            "new_username": "admin",
            "password": "changeme",
            "host": "localhost",
            "port": 8089,
        }
        self.assertTrue(expected == dslice(TEST_DICT, *test_args))


class FilePermissionTest(unittest.TestCase):
    def setUp(self):
        super().setUp()

    # Check for any change in the default file permission(i.e 644) for all files within splunklib
    def test_filePermissions(self):
        def checkFilePermissions(dir_path):
            for file in os.listdir(dir_path):
                if file.__contains__("pycache"):
                    continue
                path = os.path.join(dir_path, file)
                if os.path.isfile(path):
                    permission = oct(os.stat(path).st_mode)
                    self.assertEqual(permission, "0o100644")
                else:
                    checkFilePermissions(path)

        test_file_path = Path(__file__)
        # From tests/unit/test_file_permissions.py, go up 2 levels to project root, then to splunklib
        splunklib_path = test_file_path.parent.parent.parent / "splunklib"
        checkFilePermissions(str(splunklib_path))


if __name__ == "__main__":
    import unittest

    unittest.main()

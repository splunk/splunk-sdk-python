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

import unittest

from splunklib.ai.engines import langchain as lc


class MapRoleTests(unittest.TestCase):
    def test_map_role_from_langchain(self) -> None:
        self.assertEqual(lc._map_role_from_langchain("human"), "user")
        self.assertEqual(lc._map_role_from_langchain("system"), "system")
        self.assertEqual(lc._map_role_from_langchain("ai"), "assistant")
        self.assertEqual(lc._map_role_from_langchain("tool"), "tool")

    def test_map_role_from_langchain_invalid_raises(self) -> None:
        with self.assertRaises(Exception):
            lc._map_role_from_langchain("unknown")

    def test_map_role_to_langchain(self) -> None:
        self.assertEqual(lc._map_role_to_langchain("user"), "human")
        self.assertEqual(lc._map_role_to_langchain("system"), "system")
        self.assertEqual(lc._map_role_to_langchain("assistant"), "ai")
        self.assertEqual(lc._map_role_to_langchain("tool"), "tool")


if __name__ == "__main__":
    unittest.main()

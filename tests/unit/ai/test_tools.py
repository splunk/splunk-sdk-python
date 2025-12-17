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

from splunklib.ai import tool


def test_tool_decorator():
    @tool
    def add_tool(a: int, b: int) -> int:
        "tool that adds"

        return a + b

    assert add_tool.name == "add_tool", "Invalid tool name"
    assert add_tool.description == "tool that adds", "Invalid tool description"

    assert add_tool(1, 2) == 3, "Invalid tool result"


def test_tool_decorator_custom_metadata():
    @tool(name="adder", description="adds two ints")
    def add(a: int, b: int) -> int:
        return a + b

    assert add.name == "adder"
    assert add.description == "adds two ints"
    assert add(2, 3) == 5


def test_tool_decorator_defaults_to_empty_description():
    @tool
    def noop():
        return True

    assert noop.description == ""
    assert noop() is True

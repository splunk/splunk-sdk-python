# Copyright © 2011-2026 Splunk, Inc.
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

# pyright: reportPrivateUsage=false, reportUnusedFunction=false, reportUnusedParameter=false

import os
import sys
import unittest
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any

import pytest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.types import TextContent

from splunklib.ai.registry import ToolContext, ToolRegistry, ToolRegistryRuntimeError


class TestJSONSchemaInference(unittest.TestCase):
    def test_output_non_wrapped(self) -> None:
        r = ToolRegistry()

        @dataclass
        class Output:
            foo: int
            bar: int

        @r.tool()
        def structured_tool() -> Output:
            return Output(0, 0)

        tool = r._tools[0]
        assert tool.name == "structured_tool"
        assert tool.inputSchema == {
            "properties": {},
            "type": "object",
            "additionalProperties": False,
        }
        assert tool.outputSchema == {
            "properties": {
                "foo": {"title": "Foo", "type": "integer"},
                "bar": {"title": "Bar", "type": "integer"},
            },
            "required": ["foo", "bar"],
            "title": "Output",
            "type": "object",
        }

    def test_output_wrapped(self) -> None:
        r = ToolRegistry()

        @r.tool()
        def int_tool() -> int:
            return 0

        @r.tool()
        def str_tool() -> str:
            return ""

        tool = r._tools[0]
        assert tool.name == "int_tool"
        assert tool.inputSchema == {
            "properties": {},
            "type": "object",
            "additionalProperties": False,
        }
        assert tool.outputSchema == {
            "properties": {"result": {"title": "Result", "type": "integer"}},
            "required": ["result"],
            "title": "_WrappedResult",
            "type": "object",
        }

        tool = r._tools[1]
        assert tool.name == "str_tool"
        assert tool.inputSchema == {
            "properties": {},
            "type": "object",
            "additionalProperties": False,
        }
        assert tool.outputSchema == {
            "properties": {"result": {"title": "Result", "type": "string"}},
            "required": ["result"],
            "title": "_WrappedResult",
            "type": "object",
        }

    def test_input(self) -> None:
        r = ToolRegistry()

        @r.tool()
        def tool_int(foo: int) -> None:
            return None

        @r.tool()
        def tool_int_and_str(foo: int, bar: str) -> None:
            return None

        @dataclass
        class Input:
            foo: int
            bar: int

        @r.tool()
        def tool_input_structured(input: Input) -> None:
            return None

        tool = r._tools[0]
        assert tool.name == "tool_int"
        assert tool.inputSchema == {
            "properties": {"foo": {"title": "Foo", "type": "integer"}},
            "required": ["foo"],
            "type": "object",
            "additionalProperties": False,
        }
        assert tool.outputSchema == {
            "properties": {"result": {"title": "Result", "type": "null"}},
            "required": ["result"],
            "title": "_WrappedResult",
            "type": "object",
        }

        tool = r._tools[1]
        assert tool.name == "tool_int_and_str"
        assert tool.inputSchema == {
            "properties": {
                "foo": {"title": "Foo", "type": "integer"},
                "bar": {"title": "Bar", "type": "string"},
            },
            "required": ["foo", "bar"],
            "type": "object",
            "additionalProperties": False,
        }
        assert tool.outputSchema == {
            "properties": {"result": {"title": "Result", "type": "null"}},
            "required": ["result"],
            "title": "_WrappedResult",
            "type": "object",
        }

        tool = r._tools[2]
        assert tool.name == "tool_input_structured"
        assert tool.inputSchema == {
            "$defs": {
                "Input": {
                    "properties": {
                        "foo": {"title": "Foo", "type": "integer"},
                        "bar": {"title": "Bar", "type": "integer"},
                    },
                    "required": ["foo", "bar"],
                    "title": "Input",
                    "type": "object",
                }
            },
            "properties": {"input": {"$ref": "#/$defs/Input"}},
            "required": ["input"],
            "type": "object",
            "additionalProperties": False,
        }
        assert tool.outputSchema == {
            "properties": {"result": {"title": "Result", "type": "null"}},
            "required": ["result"],
            "title": "_WrappedResult",
            "type": "object",
        }

    def test_input_ToolContext(self) -> None:
        r = ToolRegistry()

        @r.tool()
        def tool_ctx_only(ctx: ToolContext) -> None:
            return None

        @r.tool()
        def tool_ctx_and_str(foo: ToolContext, bar: int) -> None:
            return None

        tool = r._tools[0]
        assert tool.name == "tool_ctx_only"
        assert tool.inputSchema == {
            "properties": {},
            "type": "object",
            "additionalProperties": False,
        }

        tool = r._tools[1]
        assert tool.name == "tool_ctx_and_str"
        assert tool.inputSchema == {
            "properties": {"bar": {"title": "Bar", "type": "integer"}},
            "required": ["bar"],
            "type": "object",
            "additionalProperties": False,
        }

    def test_non_inferable_types(self) -> None:
        r = ToolRegistry()

        class NonInferable:
            a: int = 0

        try:

            @r.tool()
            def tool(foo: NonInferable) -> None:
                return None

            pytest.fail("Tool annotation did not fail")
        except Exception:
            pass

        try:

            @r.tool()
            def tool2() -> NonInferable:
                return NonInferable()

            pytest.fail("Tool annotation did not fail")
        except Exception:
            pass

        assert len(r._tools) == 0
        assert len(r._tools_func) == 0
        assert len(r._tools_wrapped_result) == 0

    def test_optional_and_defaults(self) -> None:
        r = ToolRegistry()

        @dataclass
        class Data:
            foo: int | None
            bar: int | None = None
            baz: int = -1

        @r.tool()
        def fancy_tool(foo: int | None, bar: Data, baz: int = -1) -> Data:
            return bar

        tool = r._tools[0]
        assert tool.name == "fancy_tool"
        assert tool.inputSchema == {
            "$defs": {
                "Data": {
                    "properties": {
                        "foo": {
                            "anyOf": [{"type": "integer"}, {"type": "null"}],
                            "title": "Foo",
                        },
                        "bar": {
                            "anyOf": [{"type": "integer"}, {"type": "null"}],
                            "default": None,
                            "title": "Bar",
                        },
                        "baz": {"default": -1, "title": "Baz", "type": "integer"},
                    },
                    "required": ["foo"],
                    "title": "Data",
                    "type": "object",
                }
            },
            "additionalProperties": False,
            "properties": {
                "foo": {
                    "anyOf": [{"type": "integer"}, {"type": "null"}],
                    "title": "Foo",
                },
                "bar": {"$ref": "#/$defs/Data"},
                "baz": {"default": -1, "title": "Baz", "type": "integer"},
            },
            "required": ["foo", "bar"],
            "type": "object",
        }
        assert tool.outputSchema == {
            "properties": {
                "foo": {
                    "anyOf": [{"type": "integer"}, {"type": "null"}],
                    "title": "Foo",
                },
                "bar": {
                    "anyOf": [{"type": "integer"}, {"type": "null"}],
                    "default": None,
                    "title": "Bar",
                },
                "baz": {"default": -1, "title": "Baz", "type": "integer"},
            },
            "required": ["foo"],
            "title": "Data",
            "type": "object",
        }

    def test_async_tool(self) -> None:
        r = ToolRegistry()

        @r.tool()
        async def str_tool() -> str:
            return ""

        tool = r._tools[0]
        assert tool.name == "str_tool"
        assert tool.inputSchema == {
            "properties": {},
            "type": "object",
            "additionalProperties": False,
        }
        assert tool.outputSchema == {
            "properties": {"result": {"title": "Result", "type": "string"}},
            "required": ["result"],
            "title": "_WrappedResult",
            "type": "object",
        }


class TestParams(unittest.TestCase):
    def test_description_param(self) -> None:
        r = ToolRegistry()

        @r.tool(description="PARAM COMMENT")
        def tool(foo: int) -> int:
            return 0

        assert r._tools[0].description == "PARAM COMMENT"

    def test_description_doc_string(self) -> None:
        r = ToolRegistry()

        @r.tool()
        def tool(foo: int) -> int:
            """DOC COMMENT"""
            return 0

        assert r._tools[0].description == "DOC COMMENT"

    def test_description_param_override(self) -> None:
        r = ToolRegistry()

        @r.tool(description="PARAM COMMENT")
        def tool(foo: int) -> int:
            """DOC COMMENT"""
            return 0

        assert r._tools[0].description == "PARAM COMMENT"

    def test_name_param_override(self) -> None:
        r = ToolRegistry()

        @r.tool(name="cool_tool")
        def tool(foo: int) -> int:
            return 0

        assert r._tools[0].name == "cool_tool"

    def test_title(self) -> None:
        r = ToolRegistry()

        @r.tool(title="foobar")
        def tool(foo: int) -> int:
            return 0

        @r.tool()
        def tool2(foo: int) -> int:
            return 0

        assert r._tools[0].name == "tool"
        assert r._tools[0].title == "foobar"

        assert r._tools[1].name == "tool2"
        assert r._tools[1].title is None


class TestDuplicateName(unittest.TestCase):
    def test_duplicate_tool_name(self) -> None:
        r = ToolRegistry()

        def register(r: ToolRegistry) -> None:

            @r.tool()
            def tool_name(foo: int) -> int:
                return 0

        def register_name(r: ToolRegistry) -> None:
            @r.tool(name="tool_name")
            def tool(foo: int) -> int:
                return 0

        register(r)
        with pytest.raises(
            ToolRegistryRuntimeError, match="Tool tool_name already defined"
        ):
            register(r)

        with pytest.raises(
            ToolRegistryRuntimeError, match="Tool tool_name already defined"
        ):
            register_name(r)


class TestRegistryTestCase(unittest.IsolatedAsyncioTestCase):
    @asynccontextmanager
    async def connect(self, name: str) -> AsyncGenerator[ClientSession, Any]:
        server_params = StdioServerParameters(
            command=sys.executable,
            args=[os.path.join(os.path.dirname(__file__), "testdata", name)],
        )
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                yield session


class TestHelloRegistry(TestRegistryTestCase):
    async def test_list_tools(self) -> None:
        async with self.connect("hello.py") as session:
            tools = (await session.list_tools()).tools
            assert len(tools) == 1
            assert tools[0].name == "hello"
            assert tools[0].description == "Hello returns a hello message"
            assert tools[0].inputSchema == {
                "properties": {"name": {"title": "Name", "type": "string"}},
                "required": ["name"],
                "type": "object",
                "additionalProperties": False,
            }
            assert tools[0].outputSchema == {
                "properties": {"result": {"title": "Result", "type": "string"}},
                "required": ["result"],
                "title": "_WrappedResult",
                "type": "object",
            }

    async def test_call_tool(self) -> None:
        async with self.connect("hello.py") as session:
            res = await session.call_tool("hello", arguments={"name": "Mike"})
            assert not res.isError
            assert res.content == []
            assert res.structuredContent == {"result": "Hello Mike!"}


class TestFailingToolRegistry(TestRegistryTestCase):
    async def test_call_tool(self) -> None:
        async with self.connect("failing_tool.py") as session:
            res = await session.call_tool("failing_tool", arguments={})
            assert res.isError
            assert res.content == [
                TextContent(type="text", text="Some tool failure error")
            ]
            assert res.structuredContent is None


class TestToolDefiningToolsRegistry(TestRegistryTestCase):
    async def test_call_tool(self) -> None:
        async with self.connect("tool_defining_tools.py") as session:
            res = await session.call_tool("add_tool", arguments={})
            assert res.isError
            assert res.content == [
                TextContent(
                    type="text",
                    text="ToolRegistry is already running, cannot define new tools",
                )
            ]
            assert res.structuredContent is None


class TestSchemaValidationRegistry(TestRegistryTestCase):
    async def test_input_schema(self) -> None:
        async with self.connect("schema_validation.py") as session:
            res = await session.call_tool("input", arguments={})
            assert res.isError
            assert res.content == [
                TextContent(
                    type="text",
                    text="Input validation error: 'foo' is a required property",
                )
            ]
            assert res.structuredContent is None

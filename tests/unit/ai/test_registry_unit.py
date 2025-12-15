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

import json
import os
import sys
import unittest
from contextlib import asynccontextmanager
from dataclasses import dataclass

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.types import TextContent

from splunklib.ai.registry import ToolContext, ToolRegistry


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
        self.assertEqual(tool.name, "structured_tool")
        self.assertEqual(
            tool.inputSchema,
            {"properties": {}, "type": "object", "additionalProperties": False},
        )
        self.assertEqual(
            tool.outputSchema,
            {
                "properties": {
                    "foo": {"title": "Foo", "type": "integer"},
                    "bar": {"title": "Bar", "type": "integer"},
                },
                "required": ["foo", "bar"],
                "title": "Output",
                "type": "object",
            },
        )

    def test_output_wrapped(self) -> None:
        r = ToolRegistry()

        @r.tool()
        def int_tool() -> int:
            return 0

        @r.tool()
        def str_tool() -> str:
            return ""

        tool = r._tools[0]
        self.assertEqual(tool.name, "int_tool")
        self.assertEqual(
            tool.inputSchema,
            {"properties": {}, "type": "object", "additionalProperties": False},
        )
        self.assertEqual(
            tool.outputSchema,
            {
                "properties": {"result": {"title": "Result", "type": "integer"}},
                "required": ["result"],
                "title": "_WrappedResult",
                "type": "object",
            },
        )

        tool = r._tools[1]
        self.assertEqual(tool.name, "str_tool")
        self.assertEqual(
            tool.inputSchema,
            {"properties": {}, "type": "object", "additionalProperties": False},
        )
        self.assertEqual(
            tool.outputSchema,
            {
                "properties": {"result": {"title": "Result", "type": "string"}},
                "required": ["result"],
                "title": "_WrappedResult",
                "type": "object",
            },
        )

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
        self.assertEqual(tool.name, "tool_int")
        self.assertEqual(
            tool.inputSchema,
            {
                "properties": {"foo": {"title": "Foo", "type": "integer"}},
                "required": ["foo"],
                "type": "object",
                "additionalProperties": False,
            },
        )
        self.assertEqual(
            tool.outputSchema,
            {
                "properties": {"result": {"title": "Result", "type": "null"}},
                "required": ["result"],
                "title": "_WrappedResult",
                "type": "object",
            },
        )

        tool = r._tools[1]
        self.assertEqual(tool.name, "tool_int_and_str")
        self.assertEqual(
            tool.inputSchema,
            {
                "properties": {
                    "foo": {"title": "Foo", "type": "integer"},
                    "bar": {"title": "Bar", "type": "string"},
                },
                "required": ["foo", "bar"],
                "type": "object",
                "additionalProperties": False,
            },
        )
        self.assertEqual(
            tool.outputSchema,
            {
                "properties": {"result": {"title": "Result", "type": "null"}},
                "required": ["result"],
                "title": "_WrappedResult",
                "type": "object",
            },
        )

        tool = r._tools[2]
        self.assertEqual(tool.name, "tool_input_structured")
        self.assertEqual(
            tool.inputSchema,
            {
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
            },
        )
        self.assertEqual(
            tool.outputSchema,
            {
                "properties": {"result": {"title": "Result", "type": "null"}},
                "required": ["result"],
                "title": "_WrappedResult",
                "type": "object",
            },
        )

    def test_input_ToolContext(self) -> None:
        r = ToolRegistry()

        @r.tool()
        def tool_ctx_only(ctx: ToolContext) -> None:
            return None

        @r.tool()
        def tool_ctx_and_str(foo: ToolContext, bar: int) -> None:
            return None

        tool = r._tools[0]
        self.assertEqual(tool.name, "tool_ctx_only")
        self.assertEqual(
            tool.inputSchema,
            {"properties": {}, "type": "object", "additionalProperties": False},
        )

        tool = r._tools[1]
        self.assertEqual(tool.name, "tool_ctx_and_str")
        self.assertEqual(
            tool.inputSchema,
            {
                "properties": {"bar": {"title": "Bar", "type": "integer"}},
                "required": ["bar"],
                "type": "object",
                "additionalProperties": False,
            },
        )

    def test_non_inferabe_types(self) -> None:
        r = ToolRegistry()

        class NonInferable:
            a: int

        try:

            @r.tool()
            def tool(foo: NonInferable) -> None:
                return None

            self.fail("tool annotation did not fail")
        except Exception:
            pass

        try:

            @r.tool()
            def tool2() -> NonInferable:
                return NonInferable()

            self.fail("tool annotation did not fail")
        except Exception:
            pass

        self.assertEqual(len(r._tools), 0)
        self.assertEqual(len(r._tools_func), 0)
        self.assertEqual(len(r._tools_wrapped_result), 0)

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
        self.assertEqual(tool.name, "fancy_tool")
        self.assertEqual(
            tool.inputSchema,
            {
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
            },
        )
        self.assertEqual(
            tool.outputSchema,
            {
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
            },
        )


class TestParams(unittest.TestCase):
    def test_description_param(self) -> None:
        r = ToolRegistry()

        @r.tool(description="PARAM COMMENT")
        def tool(foo: int) -> int:
            return 0

        self.assertEqual(r._tools[0].description, "PARAM COMMENT")

    def test_description_doc_string(self) -> None:
        r = ToolRegistry()

        @r.tool()
        def tool(foo: int) -> int:
            """DOC COMMENT"""
            return 0

        self.assertEqual(r._tools[0].description, "DOC COMMENT")

    def test_description_param_override(self) -> None:
        r = ToolRegistry()

        @r.tool(description="PARAM COMMENT")
        def tool(foo: int) -> int:
            """DOC COMMENT"""
            return 0

        self.assertEqual(r._tools[0].description, "PARAM COMMENT")

    def test_name_param_override(self) -> None:
        r = ToolRegistry()

        @r.tool(name="cool_tool")
        def tool(foo: int) -> int:
            return 0

        self.assertEqual(r._tools[0].name, "cool_tool")

    def test_title(self) -> None:
        r = ToolRegistry()

        @r.tool(title="foobar")
        def tool(foo: int) -> int:
            return 0

        @r.tool()
        def tool2(foo: int) -> int:
            return 0

        self.assertEqual(r._tools[0].name, "tool")
        self.assertEqual(r._tools[0].title, "foobar")

        self.assertEqual(r._tools[1].name, "tool2")
        self.assertEqual(r._tools[1].title, None)


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
        self.assertRaisesRegex(
            Exception, "Tool tool_name already defined", lambda: register(r)
        )
        self.assertRaisesRegex(
            Exception, "Tool tool_name already defined", lambda: register_name(r)
        )


class TestRegistryTestCase(unittest.IsolatedAsyncioTestCase):
    @asynccontextmanager
    async def connect(self, name: str):
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
            self.assertEqual(len(tools), 1)
            self.assertEqual(tools[0].name, "hello")
            self.assertEqual(tools[0].description, "Hello returns a hello message")
            self.assertEqual(
                tools[0].inputSchema,
                {
                    "properties": {"name": {"title": "Name", "type": "string"}},
                    "required": ["name"],
                    "type": "object",
                    "additionalProperties": False,
                },
            )
            self.assertEqual(
                tools[0].outputSchema,
                {
                    "properties": {"result": {"title": "Result", "type": "string"}},
                    "required": ["result"],
                    "title": "_WrappedResult",
                    "type": "object",
                },
            )

    async def test_call_tool(self) -> None:
        async with self.connect("hello.py") as session:
            res = await session.call_tool("hello", arguments={"name": "Mike"})
            self.assertEqual(res.isError, False)
            self.assertEqual(res.content, [])
            self.assertEqual(res.structuredContent, {"result": "Hello Mike!"})


class TestFailingToolRegistry(TestRegistryTestCase):
    async def test_call_tool(self) -> None:
        async with self.connect("failing_tool.py") as session:
            res = await session.call_tool("failing_tool", arguments={})
            self.assertEqual(res.isError, True)
            self.assertEqual(
                res.content, [TextContent(type="text", text="Some tool failure error")]
            )
            self.assertEqual(res.structuredContent, None)


class TestToolDefiningToolsRegistry(TestRegistryTestCase):
    async def test_call_tool(self) -> None:
        async with self.connect("tool_defining_tools.py") as session:
            res = await session.call_tool("add_tool", arguments={})
            self.assertEqual(res.isError, True)
            self.assertEqual(
                res.content,
                [
                    TextContent(
                        type="text",
                        text="ToolRegistry is already running, cannot define new tools",
                    )
                ],
            )
            self.assertEqual(res.structuredContent, None)


class TestSchemaValidationRegistry(TestRegistryTestCase):
    async def test_input_schema(self) -> None:
        async with self.connect("schema_validation.py") as session:
            res = await session.call_tool("input", arguments={})
            self.assertEqual(res.isError, True)
            self.assertEqual(
                res.content,
                [
                    TextContent(
                        type="text",
                        text="Input validation error: 'foo' is a required property",
                    )
                ],
            )
            self.assertEqual(res.structuredContent, None)


if __name__ == "__main__":
    import unittest

    unittest.main()

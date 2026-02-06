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
import asyncio
import inspect
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from typing import Any, Callable, Generic, ParamSpec, TypeVar, get_type_hints

import mcp.types as types
from mcp.server.lowlevel import Server
from pydantic import TypeAdapter

from splunklib.binding import _spliturl
from splunklib.client import Service, connect


class ToolContext:
    """
    ToolContext provides a way to interact with the tool execution context.
    A new instance is automatically injected as a function parameter when a
    relevant type hint is detected.
    """

    _management_url: str | None = None
    _management_token: str | None = None
    _service: Service | None = None

    @property
    def service(self) -> Service:
        """
        returns a connected :class:`Service` object to the Splunk instance,
        that executed the tool.
        """
        if self._service is not None:
            return self._service

        assert all((self._management_url, self._management_token)), (
            "Invalid tool invocation, missing management_url and/or management_token"
        )

        scheme, host, port, path = _spliturl(self._management_url)
        s = connect(
            scheme=scheme,
            host=host,
            port=port,
            path=path,
            token=self._management_token,
            autologin=True,
        )
        self._service = s
        return s


_T = TypeVar("_T", default=Any)


@dataclass
class _WrappedResult(Generic[_T]):
    result: _T


_P = ParamSpec("_P")
_R = TypeVar("_R")


class ToolRegistryRuntimeError(RuntimeError):
    """Raised when a tool registry operation fails."""

    pass


class ToolRegistry:
    _server: Server
    _tools: list[types.Tool]
    _tools_func: dict[str, Callable]
    _tools_wrapped_result: dict[str, bool]
    _executing: bool = False

    def __init__(self) -> None:
        self._server = Server("Tool Registry")
        self._tools = []
        self._tools_func = {}
        self._tools_wrapped_result = {}
        self._register_handlers()

    def _register_handlers(self) -> None:
        @self._server.list_tools()
        async def _() -> list[types.Tool]:
            return self._list_tools()

        @self._server.call_tool(validate_input=True)
        async def _(name: str, arguments: dict[str, Any]) -> types.CallToolResult:
            return await self._call_tool(name, arguments)

    def _list_tools(self) -> list[types.Tool]:
        return self._tools

    async def _call_tool(
        self, name: str, arguments: dict[str, Any]
    ) -> types.CallToolResult:
        func = self._tools_func.get(name)
        if func is None:
            raise ValueError(f"Tool {name} does not exist")

        ctx = ToolContext()
        meta = self._server.request_context.meta
        if meta is not None:
            splunk_meta = meta.model_dump().get("splunk")
            if splunk_meta is not None:
                ctx._management_url = splunk_meta.get("management_url")
                ctx._management_token = splunk_meta.get("management_token")

        for k in func.__annotations__:
            if func.__annotations__[k] == ToolContext:
                assert arguments.get(k) is None, (
                    "Improper input schema was generated or schema verification is malfunctioning"
                )
                arguments[k] = ctx

        res = func(**arguments)

        # In case func was an async function, await the returned coroutine.
        # If not then we already have the result.
        if inspect.isawaitable(res):
            res = await res

        if self._tools_wrapped_result.get(name):
            res = _WrappedResult(res)

        return types.CallToolResult(
            structuredContent=asdict(res),
            content=[],
        )

    def _input_schema(self, func: Callable[_P, _R]) -> dict[str, Any]:
        """
        Generates a input schema for the provided func, skips arguments of type: `ToolContext`.
        """

        ctxs: list[str] = []
        for k in func.__annotations__:
            if func.__annotations__[k] == ToolContext:
                ctxs.append(k)

        input_schema = TypeAdapter(_drop_type_annotations_of(func, ctxs)).json_schema()

        # _drop_type_annotations_of removed the type annotation to prevent json_schema()
        # from attempting to infer type information for ToolContext (which would fail).
        # However, ToolContext fields still appear in the properties and required
        # fields of the schema (we only made sure that no type information was generated
        # in the schema, that corresponds to the ToolContext), so we need to remove those
        # references here as well.
        for ctx in ctxs:
            props = input_schema.get("properties", {})
            props.pop(ctx)

            if ctx in input_schema.get("required", []):
                input_schema["required"].remove(ctx)
                if not input_schema["required"]:
                    input_schema.pop("required")

        return input_schema

    def _output_schema(self, func: Callable[_P, _R]) -> tuple[dict[str, Any], bool]:
        """
        Generates a output schema for the provided func, if necessary wraps the
        output type with :class:`_WrappedResult`.

        Returns an output schema and a boolean that signals whether the result
        needs to be wrapped.
        """

        sig = inspect.signature(func)
        output_schema = TypeAdapter(sig.return_annotation).json_schema(
            mode="serialization"
        )

        # Since all structured results must be an object in MCP,
        # if the result type of the provided function is not an object,
        # then wrap it in a _WrappedResult to make it a object.
        is_object = (
            output_schema.get("type") == "object" or "properties" in output_schema
        )
        if not is_object:
            output_schema = TypeAdapter(
                _WrappedResult[
                    get_type_hints(func, include_extras=True).get(
                        "return", sig.return_annotation
                    )
                ]
            ).json_schema(mode="serialization")
            return output_schema, True
        return output_schema, False

    def tool(
        self,
        name: str | None = None,
        description: str | None = None,
        title: str | None = None,
        tags: Sequence[str] | None = None,
    ) -> Callable[[Callable[_P, _R]], Callable[_P, _R]]:
        """
        Decorator that registers a function with the ToolRegistry.

        The decorator automatically infers a JSON Schema from the function's
        type hints, using them to define the tool's expected input and output
        structure.

        Functions may optionally accept a :class:`ToolContext` parameter, which provides
        access to additional tool-related functionality.

        :param name: An optional name of the tool.
                     If omitted, the function's name is used.
        :param description: An optional human-readable description of the tool.
                            If omitted, the function's docstring is used.

        """

        def wrapper(func: Callable[_P, _R]) -> Callable[_P, _R]:
            nonlocal description
            if description is None:
                description = func.__doc__

            nonlocal name
            if name is None:
                name = func.__name__

            if self._executing:
                raise ToolRegistryRuntimeError(
                    "ToolRegistry is already running, cannot define new tools"
                )

            if self._tools_func.get(name) is not None:
                raise ToolRegistryRuntimeError(f"Tool {name} already defined")

            input_schema = self._input_schema(func)
            output_schema, wrapped_output = self._output_schema(func)

            self._tools.append(
                types.Tool(
                    name=name,
                    title=title,
                    description=description,
                    inputSchema=input_schema,
                    outputSchema=output_schema,
                    _meta={
                        "splunk": {"tags": tags},
                    },
                )
            )
            self._tools_func[name] = func
            self._tools_wrapped_result[name] = wrapped_output

            return func

        return wrapper

    def run(self) -> None:
        async def run() -> None:
            import mcp.server.stdio
            from mcp.server.lowlevel import NotificationOptions
            from mcp.server.models import InitializationOptions

            async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
                await self._server.run(
                    read_stream,
                    write_stream,
                    InitializationOptions(
                        server_name="Utility App - Tool Registry",
                        server_version="",
                        capabilities=self._server.get_capabilities(
                            notification_options=NotificationOptions(),
                            experimental_capabilities={},
                        ),
                    ),
                )

        self._executing = True
        asyncio.run(run())


def _drop_type_annotations_of(
    fn: Callable[..., Any], exclude_params: list[str]
) -> Callable[..., Any]:
    """
    Creates a new function, that has the type information elided for each
    param in `exclude_params`.
    """
    import types

    original_annotations = getattr(fn, "__annotations__", {})
    new_annotations = {
        k: v for k, v in original_annotations.items() if k not in exclude_params
    }

    new_func = types.FunctionType(
        fn.__code__,
        fn.__globals__,
        fn.__name__,
        fn.__defaults__,
        fn.__closure__,
    )
    new_func.__dict__.update(fn.__dict__)
    new_func.__module__ = fn.__module__
    new_func.__qualname__ = getattr(fn, "__qualname__", fn.__name__)  # ty: ignore[unresolved-attribute]
    new_func.__annotations__ = new_annotations

    return new_func

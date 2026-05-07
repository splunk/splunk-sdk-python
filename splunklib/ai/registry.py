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

import asyncio
import inspect
import logging
import string
from collections.abc import Callable, Sequence
from dataclasses import asdict, dataclass, is_dataclass
from logging import Logger
from typing import (
    Any,
    Generic,
    ParamSpec,
    TypeVar,
    get_type_hints,
    override,
)

import mcp.types as types
from mcp import LoggingLevel, ServerSession
from mcp.server.lowlevel import Server
from pydantic import TypeAdapter

from splunklib.ai.serialized_service import SerializedService
from splunklib.client import Service


def _normalize_logger_level(levelno: int) -> int:
    if levelno < logging.INFO:
        return logging.DEBUG
    elif levelno < logging.WARNING:
        return logging.INFO
    elif levelno < logging.ERROR:
        return logging.WARN
    elif levelno < logging.CRITICAL:
        return logging.ERROR
    else:
        return logging.CRITICAL


def _map_logger_to_mcp_logging_level(levelno: int) -> types.LoggingLevel:
    match _normalize_logger_level(levelno):
        case logging.FATAL:
            return "critical"
        case logging.ERROR:
            return "error"
        case logging.WARN:
            return "warning"
        case logging.INFO:
            return "info"
        case logging.DEBUG:
            return "debug"
        case _:
            raise AssertionError("invalid logging level")


def _min_logging_level(level: types.LoggingLevel) -> int:
    match level:
        case "debug":
            return logging.NOTSET
        case "info":
            return logging.INFO
        case "notice":
            return logging.INFO
        case "warning":
            return logging.WARN
        case "error":
            return logging.ERROR
        case "critical":
            return logging.CRITICAL
        case "alert":
            return logging.CRITICAL
        case "emergency":
            return logging.CRITICAL


@dataclass
class LogData:
    tool_name: str
    message: str


class _MCPLoggingHandler(logging.Handler):
    _group: asyncio.TaskGroup
    _session: ServerSession
    _request_id: types.RequestId
    _tool_name: str

    def __init__(
        self,
        group: asyncio.TaskGroup,
        session: ServerSession,
        request_id: types.RequestId,
        tool_name: str,
    ) -> None:
        self._group = group
        self._session = session
        self._request_id = request_id
        self._tool_name = tool_name
        super().__init__()

    @override
    def emit(self, record: logging.LogRecord) -> None:
        mcp_level = _map_logger_to_mcp_logging_level(record.levelno)

        async def send_log() -> None:
            await self._session.send_log_message(
                level=mcp_level,
                data=asdict(LogData(tool_name=self._tool_name, message=record.msg)),
                logger="",
                related_request_id=self._request_id,
            )

        # We can't await send_log() here, so we create a task, that will
        # send the logs concurrently.
        #
        # Note: These logs, since are executed concurrently might not be sent
        # in the same order, in which were created.
        # The root cause of this is that log Handlers cannot be async.
        #
        # We could fix this with the use of a asyncio.Queue().put_nowait, but that
        # has a problem, that it might raise an QueueFull exception, if there
        # are bunch of logs created. We would have to handle that exception with
        # a create_task(send_log()), which would still cause such unordered execution.
        #
        # Alternatively, we could maintain a set of all tasks that are not yet completed
        # and await them in send_log, before calling the send_log_message, but note
        # that this would require a clone of that set here, before creating the task
        # (also a removal of a task from that set (task.add_done_callback())
        #
        # I also wonder whether task.add_done_callback() could be leveraged to order these tasks
        # i.e. by storing the previous task (self._task) and setting self._task.add_done_callback()
        # to execute send_log() when  self._task.done == False.
        _ = self._group.create_task(send_log())


@dataclass
class _ToolContextParams:
    """
    Internal container for parameters required to initialize `ToolContext`.

    Instead of exposing these arguments directly in the `ToolContext`
    constructor, we wrap them in this private dataclass to discourage
    manual construction of `ToolContext` by end users (note the _ prefix
    in this class name i.e. internal class).
    """

    service: SerializedService | None
    logger: Logger


class ToolContext:
    """
    ToolContext provides a way to interact with the tool execution context.
    A new instance is automatically injected as a function parameter when a
    relevant type hint is detected.
    """

    _params: _ToolContextParams

    _service: Service | None = None

    def __init__(self, params: _ToolContextParams) -> None:
        self._params = params
        self._service = None

    @property
    def service(self) -> Service:
        """
        returns a connected :class:`Service` object to the Splunk instance,
        that executed the tool.
        """
        if self._service is not None:
            return self._service

        assert self._params.service is not None, (
            "Invalid tool invocation, missing serialized service details"
        )

        # TODO: Shouldn't this function be async and this use asyncio.to_thread()?
        self._service = self._params.service.connect()
        return self._service

    @property
    def logger(self) -> Logger:
        """
        This logger can be used by tools to emit logs during execution of a tool.

        Logs emitted using this logger are forwarded to the logger
        provided to the agent constructor.
        """
        return self._params.logger


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
    _tools_func: dict[str, Callable[..., Any]]
    _tools_wrapped_result: dict[str, bool]
    _executing: bool = False

    _logging_level: LoggingLevel = "warning"

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

        @self._server.set_logging_level()
        async def _(level: LoggingLevel) -> None:
            # Note: We do not update the logging level of already created loggers, see `self._call_tool`,
            # but that is fine for our use case, since we only call the set_logging_level once, before
            # tool calls.
            self._logging_level = level
            return None

    def _list_tools(self) -> list[types.Tool]:
        return self._tools

    async def _call_tool(self, name: str, arguments: dict[str, Any]) -> types.CallToolResult:
        func = self._tools_func.get(name)
        if func is None:
            raise ValueError(f"Tool {name} does not exist")

        req_ctx = self._server.request_context

        try:
            # Use a TaskGroup such that all logs are send before finishing the tool execution
            # and all errors propagated (if any).
            async with asyncio.TaskGroup() as task_group:
                handler = _MCPLoggingHandler(
                    task_group,
                    req_ctx.session,
                    req_ctx.request_id,
                    name,
                )

                # Create a logger that forwards all logs to the client over MCP.
                logger = logging.Logger(name="MCP Logger")
                logger.setLevel(_min_logging_level(self._logging_level))
                logger.addHandler(handler)

                service: SerializedService | None = None

                meta = req_ctx.meta
                if meta is not None:
                    splunk_meta = meta.model_dump().get("splunk")
                    if splunk_meta is not None:
                        service = SerializedService.model_validate(splunk_meta.get("service"))

                ctx = ToolContext(
                    params=_ToolContextParams(
                        service=service,
                        logger=logger,
                    )
                )

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

                if is_dataclass(res) and not isinstance(res, type):
                    res = asdict(res)

                if not isinstance(res, dict):
                    raise AssertionError("invalid type of tool response")

                return types.CallToolResult(
                    structuredContent=res,  # pyright: ignore[reportUnknownArgumentType]
                    content=[],
                )
        except BaseExceptionGroup as e:
            # Re-raise the first exception.
            raise e.exceptions[0]

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

    # TODO: figure out how to handle custom classes as output type
    def _output_schema(self, func: Callable[_P, _R]) -> tuple[dict[str, Any], bool]:
        """
        Generates a output schema for the provided func, if necessary wraps the
        output type with :class:`_WrappedResult`.

        Returns an output schema and a boolean that signals whether the result
        needs to be wrapped.
        """

        sig = inspect.signature(func)
        output_schema = TypeAdapter(sig.return_annotation).json_schema(mode="serialization")

        # Since all structured results must be an object in MCP,
        # if the result type of the provided function is not an object,
        # then wrap it in a _WrappedResult to make it a object.
        is_object = output_schema.get("type") == "object" or "properties" in output_schema
        if not is_object:
            output_schema = TypeAdapter(
                _WrappedResult[
                    get_type_hints(func, include_extras=True).get("return", sig.return_annotation)
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

            if not is_tool_name_valid(name):
                raise ToolRegistryRuntimeError(
                    f"Tool name {name} doesn't conform to MCP spec, see: "
                    + "https://modelcontextprotocol.io/specification/latest/server/tools#tool-names"
                )

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
    new_annotations = {k: v for k, v in original_annotations.items() if k not in exclude_params}

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


MCP_ALLOWED_CHARS = string.ascii_letters + string.digits + "_-."


def is_tool_name_valid(name: str) -> bool:
    """Checks compliance with the MCP spec restrictions, see:
    https://modelcontextprotocol.io/specification/latest/server/tools#tool-names
    """
    if not (1 <= len(name) <= 128):
        return False

    return set(name).issubset(MCP_ALLOWED_CHARS)

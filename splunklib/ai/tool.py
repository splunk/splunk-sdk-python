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

from typing import Protocol, Callable


# NOTE: those tools might be removed in the future, as we're gonna go with the
# unified tool registry. Leaving for testing purposes during development.


class Tool(Protocol):
    name: str
    description: str
    func: Callable

    def __call__(self, *args, **kwargs): ...


def tool(
    func: Callable | None = None,
    *,
    name: str | None = None,
    description: str | None = None,
) -> Tool:
    """Decorator that wraps a callable as a Tool.

    Supports both ``@tool`` and ``@tool(name="...", description="...")`` usage.
    """

    def _wrap(target: Callable) -> Tool:
        class _ToolWrapper:
            name: str
            description: str
            func: Callable

            def __init__(self):
                self.name = name or target.__name__
                self.description = description or (target.__doc__ or "")
                self.func = target

            def __call__(self, *args, **kwargs):
                return target(*args, **kwargs)

        return _ToolWrapper()

    if func is None:
        return _wrap

    return _wrap(func)

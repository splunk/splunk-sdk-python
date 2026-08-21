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

import os

import pytest

from splunklib.searchcommands.environment import (
    _find_app_root,  # pyright: ignore[reportPrivateUsage]
)

_SPLUNK_HOME = os.path.join(os.sep, "opt", "splunk")
_APPS_DIRECTORY = os.path.join(_SPLUNK_HOME, "etc", "apps")


@pytest.mark.parametrize(
    ("app_file_parts", "expected_app_root_parts"),
    [
        # A script located directly in the app's bin directory
        (("my_app", "bin", "command.py"), ("my_app",)),
        # A script located in a subdirectory of bin, including one that happens to be
        # named "bin" itself; the app root is still $SPLUNK_HOME/etc/apps/my_app
        (("my_app", "bin", "foo", "bin", "command.py"), ("my_app",)),
    ],
)
def test_find_app_root(
    app_file_parts: tuple[str, ...], expected_app_root_parts: tuple[str, ...]
) -> None:
    app_file = os.path.join(_APPS_DIRECTORY, *app_file_parts)
    expected_app_root = os.path.join(_APPS_DIRECTORY, *expected_app_root_parts)
    assert _find_app_root(app_file, _SPLUNK_HOME) == expected_app_root


def test_find_app_root_falls_back_on_nonstandard_splunk_home() -> None:
    app_file = os.path.join("some", "other", "layout", "command.py")
    expected_app_root = os.path.dirname(os.path.abspath(os.path.dirname(app_file)))
    assert _find_app_root(app_file, _SPLUNK_HOME) == expected_app_root

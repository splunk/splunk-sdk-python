# Copyright (c) 2011-2026 Splunk, Inc.
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

from collections.abc import Iterator
from unittest.mock import patch

from splunklib.results import JSONResultsReader, Message


class IterOnlyStream:
    lines: list[bytes]

    def __init__(self, lines: list[bytes]) -> None:
        self.lines = lines

    def __iter__(self) -> Iterator[bytes]:
        return iter(self.lines)

    def readlines(self) -> list[bytes]:
        raise AssertionError("JSONResultsReader should iterate over the stream")


def test_json_results_reader_iterates_stream_without_readlines() -> None:
    stream = IterOnlyStream(
        [
            b'{"preview": false, "messages": [{"type": "INFO", "text": "done"}]}\n',
            b'{"result": {"host": "localhost"}}\n',
            b'{"results": [{"count": "1"}, {"count": "2"}]}\n',
        ]
    )

    with patch("splunklib.results.BufferedReader", return_value=stream):
        reader = JSONResultsReader(object())

    assert list(reader) == [
        Message("INFO", "done"),
        {"host": "localhost"},
        {"count": "1"},
        {"count": "2"},
    ]
    assert reader.is_preview is False

"""
Reproducer for issue #687 / PR #800: streaming commands materialise the full
record iterator into a list before writing, causing high memory usage on large
result sets.

Two paths are exercised:
  1. StreamingCommand  → write_records(process(records))  via _execute_chunk_v2
                         in search_command.py (base class).
  2. GeneratingCommand → _execute_chunk_v2 in generating_command.py (own override),
                         which collected all rows into `records = []` before writing.

Protocol ceiling (SPL-103525 / DVPL-6448):
    The CEXC protocol (chunked-command-protocol.txt) is strictly request-response:
    Splunk sends one execute chunk, the SDK must reply with exactly one chunk.
    Footnote [1] of the spec notes "Pipelining may be supported in future versions".
    Until SPL-103525 ships, RecordWriterV2 must buffer the entire CSV reply in its
    StringIO buffer before flushing — partial mid-chunk writes are not possible.

    Consequence: ~1x CSV payload buffering is unavoidable and these tests are
    marked xfail(strict=False).  They will show as XFAIL (expected failure) until
    SPL-103525 is resolved and the SDK is updated to use partial chunks.

    What IS avoidable (and what PR #800 targets) is the extra Python-object-level
    copy: list(records) in write_records() and records=[] in _execute_chunk_v2.
    Removing those copies saves roughly 1x Python-object overhead on top of the
    unavoidable CSV buffer, but cannot bring RSS growth below ~1x payload.
"""

import io
import resource
import sys
from collections.abc import Generator, Iterator

import pytest

from splunklib.searchcommands import Configuration, GeneratingCommand, StreamingCommand

from . import chunked_data_stream as chunky

RECORD_SIZE_BYTES = 1_000
N_RECORDS = 50_000
EXPECTED_TOTAL_BYTES = RECORD_SIZE_BYTES * N_RECORDS  # ~50 MB

# A correctly fixed SDK still buffers ~1x CSV payload in RecordWriter._buffer
# (required by the CEXC protocol).  Flag if growth exceeds 20 % — this threshold
# can only be met once SPL-103525 ships partial chunk support.
OOM_THRESHOLD_BYTES = EXPECTED_TOTAL_BYTES * 0.20

_XFAIL_REASON = (
    "CEXC protocol requires full-chunk buffering in RecordWriter._buffer "
    "(RecordWriterV2.flush(partial=True) is a no-op until SPL-103525 ships). "
    "~1x CSV payload buffering is unavoidable regardless of list() removal. "
    "Remove xfail once SPL-103525 is resolved and partial chunk support is wired up."
)


def _rss_bytes() -> int:
    # resource.getrusage returns kilobytes on Linux, bytes on macOS.
    ru = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    if sys.platform == "darwin":
        return ru  # bytes
    return ru * 1024  # kilobytes → bytes


# ---------------------------------------------------------------------------
# Streaming command reproducer (issue #687 root cause: write_records list())
# ---------------------------------------------------------------------------


@pytest.mark.xfail(strict=False, reason=_XFAIL_REASON)
def test_streaming_command_does_not_buffer_all_records() -> None:
    """
    StreamingCommand must not materialise all records into memory before writing.

    The base-class write_records() used to call list(records), which forced full
    materialisation of the iterator on top of the unavoidable CSV buffer in
    RecordWriter._buffer.  Removing list() halves the peak RSS but cannot bring
    it below ~1x payload while CEXC partial chunk support is absent (SPL-103525).
    """
    large_value = "x" * RECORD_SIZE_BYTES

    @Configuration()
    class PassThroughCommand(StreamingCommand):
        def stream(self, records: Iterator[dict]) -> Generator[dict]:
            yield from records

    data = [{"payload": large_value} for _ in range(N_RECORDS)]

    ifile = io.BytesIO()
    ifile.write(chunky.build_getinfo_chunk())
    ifile.write(chunky.build_data_chunk(data, finished=True))
    ifile.seek(0)
    ofile = io.BytesIO()

    rss_before = _rss_bytes()
    cmd = PassThroughCommand()
    cmd._process_protocol_v2([], ifile, ofile)
    rss_after = _rss_bytes()

    rss_growth = rss_after - rss_before
    assert rss_growth < OOM_THRESHOLD_BYTES, (
        f"Streaming command buffered too much: RSS grew by {rss_growth / 1024 / 1024:.1f} MB "
        f"(threshold {OOM_THRESHOLD_BYTES / 1024 / 1024:.1f} MB). "
        f"Total payload was {EXPECTED_TOTAL_BYTES / 1024 / 1024:.1f} MB. "
        "Likely cause: write_records() is calling list(records) or SPL-103525 is still unresolved."
    )


# ---------------------------------------------------------------------------
# Generating command reproducer (generating_command._execute_chunk_v2 buffer)
# ---------------------------------------------------------------------------


@pytest.mark.xfail(strict=False, reason=_XFAIL_REASON)
def test_generating_command_does_not_buffer_all_records() -> None:
    """
    GeneratingCommand._execute_chunk_v2 must not accumulate all yielded rows
    into a Python list before writing.

    The original code collected rows into `records = []` then wrote them in a
    second pass, doubling peak memory on top of the unavoidable CSV buffer.
    Removing the list halves the peak RSS but the CSV buffer floor remains until
    SPL-103525 ships.
    """
    large_value = "x" * RECORD_SIZE_BYTES

    @Configuration()
    class LargeGeneratorCommand(GeneratingCommand):
        def generate(self) -> Generator[dict]:
            for i in range(N_RECORDS):
                yield {"index": str(i), "payload": large_value}

    ifile = io.BytesIO()
    ifile.write(chunky.build_getinfo_chunk())
    ifile.write(chunky.build_chunk({"action": "execute"}))
    ifile.seek(0)
    ofile = io.BytesIO()

    rss_before = _rss_bytes()
    generator = LargeGeneratorCommand()
    generator._process_protocol_v2([], ifile, ofile)
    rss_after = _rss_bytes()

    rss_growth = rss_after - rss_before
    assert rss_growth < OOM_THRESHOLD_BYTES, (
        f"Generating command buffered too much: RSS grew by {rss_growth / 1024 / 1024:.1f} MB "
        f"(threshold {OOM_THRESHOLD_BYTES / 1024 / 1024:.1f} MB). "
        f"Total payload was {EXPECTED_TOTAL_BYTES / 1024 / 1024:.1f} MB. "
        "Likely cause: _execute_chunk_v2 is collecting rows into records=[] or SPL-103525 is still unresolved."
    )

"""
Tests for RecordWriterV3 / DiskBufferSettings disk-spill buffering.

Two concerns:
  1. Correctness: disk_buffer produces identical output to the default StringIO path.
  2. Memory: RecordWriterV3 keeps the CSV reply buffer off the Python heap.
     Measured via tracemalloc (Python-level allocations only), which isolates the
     StringIO vs SpooledTemporaryFile difference from Python-object overhead.

Benchmark (CPU + RAM):
  test_benchmark_v2_vs_v3 prints a wall-clock + tracemalloc comparison table.
  It never asserts on performance — only on correctness — so CI always passes.

Why tracemalloc instead of ru_maxrss:
  resource.getrusage().ru_maxrss is the process-lifetime peak RSS (monotonically
  non-decreasing).  In a multi-test pytest session the baseline is already high
  from earlier tests, making delta measurements unreliable.  tracemalloc tracks
  Python-level heap allocations only, resettable per-test, which cleanly isolates
  the StringIO vs SpooledTemporaryFile buffer difference.
"""

import io
import time
import tracemalloc
from collections.abc import Generator, Iterator

import pytest

from splunklib.searchcommands import (
    Configuration,
    DiskBufferSettings,
    GeneratingCommand,
    StreamingCommand,
)

from . import chunked_data_stream as chunky

RECORD_SIZE_BYTES = 1_000
N_RECORDS = 50_000
EXPECTED_TOTAL_BYTES = RECORD_SIZE_BYTES * N_RECORDS  # ~50 MB

# RecordWriterV3 keeps the CSV bytes off the Python heap (spilled to disk).
# Allowed peak: spool_size (4 MB default) + small per-record overhead.
# We allow 10% of total payload as generous headroom for encoder buffers etc.
DISK_BUFFER_HEAP_THRESHOLD = EXPECTED_TOTAL_BYTES * 0.10


# ---------------------------------------------------------------------------
# Correctness: disk_buffer output matches default StringIO output
# ---------------------------------------------------------------------------


def test_disk_buffer_streaming_output_matches_default() -> None:
    """RecordWriterV3 must produce byte-for-byte identical output to RecordWriterV2."""
    large_value = "x" * 100
    records = [{"payload": large_value, "idx": str(i)} for i in range(200)]

    @Configuration()
    class DefaultCommand(StreamingCommand):
        def stream(self, records: Iterator[dict]) -> Generator[dict]:
            yield from records

    @Configuration(disk_buffer=DiskBufferSettings(spool_size=1024))
    class DiskCommand(StreamingCommand):
        def stream(self, records: Iterator[dict]) -> Generator[dict]:
            yield from records

    def run_command(cmd_class: type) -> bytes:
        ifile = io.BytesIO()
        ifile.write(chunky.build_getinfo_chunk())
        ifile.write(chunky.build_data_chunk(records, finished=True))
        ifile.seek(0)
        ofile = io.BytesIO()
        cmd_class()._process_protocol_v2([], ifile, ofile)
        return ofile.getvalue()

    default_out = run_command(DefaultCommand)
    disk_out = run_command(DiskCommand)

    assert default_out == disk_out, (
        f"disk_buffer output differs from default.\n"
        f"default length: {len(default_out)}, disk length: {len(disk_out)}"
    )


def test_disk_buffer_generating_output_matches_default() -> None:
    """RecordWriterV3 GeneratingCommand output must match RecordWriterV2."""

    @Configuration()
    class DefaultGenCommand(GeneratingCommand):
        def generate(self) -> Generator[dict]:
            for i in range(200):
                yield {"idx": str(i), "val": "y" * 100}

    @Configuration(disk_buffer=DiskBufferSettings(spool_size=1024))
    class DiskGenCommand(GeneratingCommand):
        def generate(self) -> Generator[dict]:
            for i in range(200):
                yield {"idx": str(i), "val": "y" * 100}

    def run_command(cmd_class: type) -> bytes:
        ifile = io.BytesIO()
        ifile.write(chunky.build_getinfo_chunk())
        ifile.write(chunky.build_chunk({"action": "execute"}))
        ifile.seek(0)
        ofile = io.BytesIO()
        cmd_class()._process_protocol_v2([], ifile, ofile)
        return ofile.getvalue()

    default_out = run_command(DefaultGenCommand)
    disk_out = run_command(DiskGenCommand)

    assert default_out == disk_out


# ---------------------------------------------------------------------------
# Memory: disk_buffer keeps CSV bytes off the Python heap (tracemalloc)
# ---------------------------------------------------------------------------


def _measure_heap_streaming(use_disk_buffer: bool) -> int:
    """Return peak Python heap growth (bytes) during a 50k-record streaming run."""
    large_value = "x" * RECORD_SIZE_BYTES
    data = [{"payload": large_value} for _ in range(N_RECORDS)]

    if use_disk_buffer:
        @Configuration(disk_buffer=DiskBufferSettings())
        class DiskStreamCmd(StreamingCommand):
            def stream(self, records: Iterator[dict]) -> Generator[dict]:
                yield from records
        cmd_class = DiskStreamCmd
    else:
        @Configuration()
        class DefaultStreamCmd(StreamingCommand):
            def stream(self, records: Iterator[dict]) -> Generator[dict]:
                yield from records
        cmd_class = DefaultStreamCmd

    ifile = io.BytesIO()
    ifile.write(chunky.build_getinfo_chunk())
    ifile.write(chunky.build_data_chunk(data, finished=True))
    ifile.seek(0)
    ofile = io.BytesIO()

    tracemalloc.start()
    cmd_class()._process_protocol_v2([], ifile, ofile)
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return peak


def _measure_heap_generating(use_disk_buffer: bool) -> int:
    """Return peak Python heap growth (bytes) during a 50k-record generating run."""
    large_value = "x" * RECORD_SIZE_BYTES

    if use_disk_buffer:
        @Configuration(disk_buffer=DiskBufferSettings())
        class DiskGenCmd(GeneratingCommand):
            def generate(self) -> Generator[dict]:
                for i in range(N_RECORDS):
                    yield {"index": str(i), "payload": large_value}
        cmd_class = DiskGenCmd
    else:
        @Configuration()
        class DefaultGenCmd(GeneratingCommand):
            def generate(self) -> Generator[dict]:
                for i in range(N_RECORDS):
                    yield {"index": str(i), "payload": large_value}
        cmd_class = DefaultGenCmd

    ifile = io.BytesIO()
    ifile.write(chunky.build_getinfo_chunk())
    ifile.write(chunky.build_chunk({"action": "execute"}))
    ifile.seek(0)
    ofile = io.BytesIO()

    tracemalloc.start()
    cmd_class()._process_protocol_v2([], ifile, ofile)
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return peak


def test_disk_buffer_streaming_heap_less_than_default() -> None:
    """RecordWriterV3 must use less Python heap than RecordWriterV2 for large payloads.

    V2 holds the full CSV in a StringIO on the Python heap.
    V3 spills CSV bytes to disk; only up to spool_size stays in RAM.
    """
    peak_v2 = _measure_heap_streaming(use_disk_buffer=False)
    peak_v3 = _measure_heap_streaming(use_disk_buffer=True)

    mb = 1024 * 1024
    assert peak_v3 < peak_v2, (
        f"RecordWriterV3 should use less Python heap than V2.\n"
        f"V2 peak: {peak_v2 / mb:.1f} MB, V3 peak: {peak_v3 / mb:.1f} MB"
    )


def test_disk_buffer_generating_heap_less_than_default() -> None:
    """RecordWriterV3 must use less Python heap than RecordWriterV2 for GeneratingCommand."""
    peak_v2 = _measure_heap_generating(use_disk_buffer=False)
    peak_v3 = _measure_heap_generating(use_disk_buffer=True)

    mb = 1024 * 1024
    assert peak_v3 < peak_v2, (
        f"RecordWriterV3 should use less Python heap than V2.\n"
        f"V2 peak: {peak_v2 / mb:.1f} MB, V3 peak: {peak_v3 / mb:.1f} MB"
    )


# ---------------------------------------------------------------------------
# Benchmark: wall-clock time + tracemalloc heap for V2 vs V3
# ---------------------------------------------------------------------------


def test_benchmark_v2_vs_v3(capsys: pytest.CaptureFixture[str]) -> None:
    """Measure and print wall-clock time + peak heap for RecordWriterV2 vs V3.

    Never fails on performance — only prints the comparison table.
    """
    mb = 1024 * 1024

    def run(use_disk: bool) -> tuple[float, int]:
        large_value = "x" * RECORD_SIZE_BYTES
        data = [{"payload": large_value} for _ in range(N_RECORDS)]

        if use_disk:
            @Configuration(disk_buffer=DiskBufferSettings())
            class BenchDisk(StreamingCommand):
                def stream(self, records: Iterator[dict]) -> Generator[dict]:
                    yield from records
            cmd_class = BenchDisk
        else:
            @Configuration()
            class BenchDefault(StreamingCommand):
                def stream(self, records: Iterator[dict]) -> Generator[dict]:
                    yield from records
            cmd_class = BenchDefault

        ifile = io.BytesIO()
        ifile.write(chunky.build_getinfo_chunk())
        ifile.write(chunky.build_data_chunk(data, finished=True))
        ifile.seek(0)
        ofile = io.BytesIO()

        tracemalloc.start()
        t0 = time.perf_counter()
        cmd_class()._process_protocol_v2([], ifile, ofile)
        wall = time.perf_counter() - t0
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        return wall, peak

    wall_v2, heap_v2 = run(use_disk=False)
    wall_v3, heap_v3 = run(use_disk=True)

    with capsys.disabled():
        print(
            f"\n"
            f"RecordWriter V2 vs V3 benchmark  "
            f"({N_RECORDS} records x {RECORD_SIZE_BYTES} B = {EXPECTED_TOTAL_BYTES / mb:.0f} MB payload)\n"
            f"{'':26s}  {'Wall (s)':>10}  {'Heap peak':>12}\n"
            f"{'RecordWriterV2 (StringIO)':26s}  {wall_v2:>10.3f}  {heap_v2 / mb:>10.1f} MB\n"
            f"{'RecordWriterV3 (SpoolFile)':26s}  {wall_v3:>10.3f}  {heap_v3 / mb:>10.1f} MB\n"
            f"{'Overhead':26s}  {(wall_v3 - wall_v2):>+10.3f}  {(heap_v3 - heap_v2) / mb:>+10.1f} MB\n"
        )

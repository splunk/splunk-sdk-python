#!/usr/bin/env python3
"""
Standalone benchmark: RecordWriterV2 (StringIO) vs RecordWriterV3 (SpooledFile).

Streams N GB of synthetic records through each writer into /dev/null.
Measures wall-clock time, peak tracemalloc heap, and peak RSS.

Usage:
    python bench_writers.py [--gb 10] [--record-bytes 1000] [--chunk-rows 50000]
"""
import argparse
import gc
import os
import resource
import shutil
import sys
import time
import tracemalloc
from io import BytesIO, TextIOWrapper
from pathlib import Path

# Make sure we can import splunklib from the worktree
sys.path.insert(0, str(Path(__file__).parent))

from splunklib.searchcommands.internals import (
    DiskBufferSettings,
    RecordWriterV2,
    RecordWriterV3,
)


# ---------------------------------------------------------------------------
# /dev/null sink (binary)
# ---------------------------------------------------------------------------
class NullFile:
    """Binary sink — accepts bytes, discards them."""
    def write(self, data: bytes) -> int:
        return len(data)
    def flush(self):
        pass


# ---------------------------------------------------------------------------
# Synthetic record generator (never materialises all records)
# ---------------------------------------------------------------------------
def record_stream(n_records: int, record_bytes: int):
    """Yield dicts with a fixed-size payload field."""
    payload = "x" * record_bytes
    for i in range(n_records):
        yield {"index": str(i), "payload": payload}


# ---------------------------------------------------------------------------
# Benchmark runner
# ---------------------------------------------------------------------------
def rss_bytes() -> int:
    ru = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return ru if sys.platform == "darwin" else ru * 1024


def run_benchmark(writer, records_iter, chunk_rows: int) -> tuple[float, int, int]:
    """
    Pump records through writer in chunks of `chunk_rows`.
    Returns (wall_seconds, peak_tracemalloc_bytes, peak_rss_bytes).
    """
    gc.collect()
    rss_before = rss_bytes()

    tracemalloc.start()
    t0 = time.perf_counter()

    count = 0
    for record in records_iter:
        writer.write_record(record)
        count += 1
        if count == chunk_rows:
            writer.write_chunk(finished=False)
            count = 0

    writer.write_chunk(finished=True)

    wall = time.perf_counter() - t0
    _, peak_heap = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    rss_after = rss_bytes()
    peak_rss_delta = max(0, rss_after - rss_before)

    return wall, peak_heap, peak_rss_delta


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--gb", type=float, default=10.0, help="Total payload GB")
    parser.add_argument("--record-bytes", type=int, default=1_000, help="Bytes per record")
    parser.add_argument("--chunk-rows", type=int, default=50_000, help="Rows per chunk (maxresultrows)")
    parser.add_argument("--spool-size", type=int, default=4 * 1024 * 1024, help="V3 spool_size bytes")
    args = parser.parse_args()

    total_bytes = int(args.gb * 1024 ** 3)
    n_records = total_bytes // args.record_bytes
    actual_gb = (n_records * args.record_bytes) / 1024 ** 3

    mb = 1024 * 1024
    gb = 1024 ** 3

    print(f"\nBenchmark: {actual_gb:.2f} GB payload  "
          f"({n_records:,} records × {args.record_bytes} B)  "
          f"chunk_rows={args.chunk_rows:,}  spool_size={args.spool_size // mb} MB\n")
    print(f"{'Writer':<30}  {'Wall (s)':>10}  {'Heap peak':>12}  {'RSS delta':>12}  {'Throughput':>14}")
    print("-" * 84)

    results = {}

    for label, make_writer in [
        ("RecordWriterV2 (StringIO)", lambda: RecordWriterV2(NullFile(), args.chunk_rows)),
        (f"RecordWriterV3 (spool={args.spool_size // mb}MB)", lambda: RecordWriterV3(
            NullFile(), args.chunk_rows, disk_buffer=DiskBufferSettings(spool_size=args.spool_size)
        )),
    ]:
        writer = make_writer()
        gen = record_stream(n_records, args.record_bytes)
        wall, heap, rss = run_benchmark(writer, gen, args.chunk_rows)
        throughput = (n_records * args.record_bytes) / wall / gb
        results[label] = (wall, heap, rss, throughput)
        print(f"{label:<30}  {wall:>10.2f}  {heap / mb:>10.1f} MB  {rss / mb:>10.1f} MB  {throughput:>12.2f} GB/s")
        gc.collect()

    # Delta row
    labels = list(results.keys())
    w2, h2, r2, tp2 = results[labels[0]]
    w3, h3, r3, tp3 = results[labels[1]]
    print("-" * 84)
    print(f"{'Delta (V3 - V2)':<30}  {w3 - w2:>+10.2f}  {(h3 - h2) / mb:>+10.1f} MB  "
          f"{(r3 - r2) / mb:>+10.1f} MB  {tp3 - tp2:>+12.2f} GB/s")
    print()

    heap_reduction_pct = (h2 - h3) / h2 * 100 if h2 else 0
    print(f"V3 heap reduction: {heap_reduction_pct:.1f}% vs V2")
    print(f"Total CSV written: ~{n_records * args.record_bytes * 2 / gb:.1f} GB "  # ~2x due to __mv_ columns
          f"(raw payload × ~2 for __mv_ encoding)")


if __name__ == "__main__":
    main()

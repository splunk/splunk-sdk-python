#!/usr/bin/env python3
"""
Compare the two PR fixes independently and combined:
  A) Baseline  — list() + StringIO  (V2, no declare_fields)
  B) list-fix  — no list() via declare_fields, still StringIO (V2)
  C) spool-fix — list() still present, but SpooledTemporaryFile (V3)
  D) both      — declare_fields + V3

Measures wall-clock, tracemalloc peak heap, and RSS delta.
Uses GeneratingCommand path so list() materialisation in _execute_chunk_v2
is actually exercised.
"""
import gc
import resource
import sys
import time
import tracemalloc
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from splunklib.searchcommands.internals import (
    DiskBufferSettings,
    RecordWriterV2,
    RecordWriterV3,
)

GB = 1024 ** 3
MB = 1024 * 1024

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
RECORD_BYTES = 1_000
GB_TARGET = 2.0
CHUNK_ROWS = 50_000
SPOOL_SIZE = 4 * MB

N_RECORDS = int(GB_TARGET * GB / RECORD_BYTES)
PAYLOAD = "x" * RECORD_BYTES


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
class NullFile:
    def write(self, d): return len(d)
    def flush(self): pass


def rss_bytes() -> int:
    ru = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return ru if sys.platform == "darwin" else ru * 1024


def record_gen(n: int):
    for i in range(n):
        yield {"index": str(i), "payload": PAYLOAD}


# ---------------------------------------------------------------------------
# Simulate GeneratingCommand._execute_chunk_v2 for each case
# ---------------------------------------------------------------------------
def run_baseline(n: int) -> tuple[float, int, int]:
    """A: list() accumulation + StringIO (original behaviour)."""
    w = RecordWriterV2(NullFile(), CHUNK_ROWS)
    process = record_gen(n)

    gc.collect()
    rss_before = rss_bytes()
    tracemalloc.start()
    t0 = time.perf_counter()

    while True:
        count = 0
        records = []
        for row in process:
            records.append(row)
            count += 1
            if count == CHUNK_ROWS:
                break
        for row in records:
            w.write_record(row)
        finished = count < CHUNK_ROWS
        w.write_chunk(finished=finished)
        if finished:
            break

    wall = time.perf_counter() - t0
    _, heap = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return wall, heap, max(0, rss_bytes() - rss_before)


def run_list_fix(n: int) -> tuple[float, int, int]:
    """B: declare_fields removes list(), still StringIO."""
    w = RecordWriterV2(NullFile(), CHUNK_ROWS)
    w.custom_fields.update(["index", "payload"])
    w.fields_declared = True
    process = record_gen(n)

    gc.collect()
    rss_before = rss_bytes()
    tracemalloc.start()
    t0 = time.perf_counter()

    while True:
        count = 0
        # fields_declared path: stream directly
        for row in process:
            w.write_record(row)
            count += 1
            if count == CHUNK_ROWS:
                break
        finished = count < CHUNK_ROWS
        w.write_chunk(finished=finished)
        if finished:
            break

    wall = time.perf_counter() - t0
    _, heap = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return wall, heap, max(0, rss_bytes() - rss_before)


def run_spool_fix(n: int) -> tuple[float, int, int]:
    """C: list() still used, but SpooledTemporaryFile (V3)."""
    w = RecordWriterV3(NullFile(), CHUNK_ROWS, disk_buffer=DiskBufferSettings(spool_size=SPOOL_SIZE))
    process = record_gen(n)

    gc.collect()
    rss_before = rss_bytes()
    tracemalloc.start()
    t0 = time.perf_counter()

    while True:
        count = 0
        records = []
        for row in process:
            records.append(row)
            count += 1
            if count == CHUNK_ROWS:
                break
        for row in records:
            w.write_record(row)
        finished = count < CHUNK_ROWS
        w.write_chunk(finished=finished)
        if finished:
            break

    wall = time.perf_counter() - t0
    _, heap = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return wall, heap, max(0, rss_bytes() - rss_before)


def run_both(n: int) -> tuple[float, int, int]:
    """D: declare_fields + V3."""
    w = RecordWriterV3(NullFile(), CHUNK_ROWS, disk_buffer=DiskBufferSettings(spool_size=SPOOL_SIZE))
    w.custom_fields.update(["index", "payload"])
    w.fields_declared = True
    process = record_gen(n)

    gc.collect()
    rss_before = rss_bytes()
    tracemalloc.start()
    t0 = time.perf_counter()

    while True:
        count = 0
        for row in process:
            w.write_record(row)
            count += 1
            if count == CHUNK_ROWS:
                break
        finished = count < CHUNK_ROWS
        w.write_chunk(finished=finished)
        if finished:
            break

    wall = time.perf_counter() - t0
    _, heap = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return wall, heap, max(0, rss_bytes() - rss_before)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print(f"\nFix comparison: {GB_TARGET:.1f} GB payload  "
          f"({N_RECORDS:,} records × {RECORD_BYTES} B)  "
          f"chunk_rows={CHUNK_ROWS:,}  spool={SPOOL_SIZE // MB} MB\n")

    hdr = f"{'Variant':<35}  {'Wall (s)':>8}  {'Heap peak':>11}  {'RSS delta':>11}"
    print(hdr)
    print("-" * len(hdr))

    cases = [
        ("A  baseline  (list + StringIO)",     run_baseline),
        ("B  list-fix  (no list, StringIO)",   run_list_fix),
        ("C  spool-fix (list + SpoolFile)",    run_spool_fix),
        ("D  both      (no list + SpoolFile)", run_both),
    ]

    results = {}
    for label, fn in cases:
        wall, heap, rss = fn(N_RECORDS)
        results[label] = (wall, heap, rss)
        print(f"{label:<35}  {wall:>8.2f}  {heap / MB:>9.1f} MB  {rss / MB:>9.1f} MB")
        gc.collect()

    baseline_wall, baseline_heap, baseline_rss = results[cases[0][0]]
    print()
    print("Savings vs baseline:")
    for label, _ in cases[1:]:
        w, h, r = results[label]
        dw = w - baseline_wall
        dh = h - baseline_heap
        dr = r - baseline_rss
        print(f"  {label:<35}  wall {dw:>+7.2f}s  heap {dh / MB:>+7.1f} MB ({dh / baseline_heap * 100:>+5.1f}%)  "
              f"rss {dr / MB:>+7.1f} MB")

    print()
    # Which fix dominates heap savings?
    _, h_b, _ = results[cases[1][0]]  # list-fix
    _, h_c, _ = results[cases[2][0]]  # spool-fix
    list_saving = (baseline_heap - h_b) / baseline_heap * 100
    spool_saving = (baseline_heap - h_c) / baseline_heap * 100
    print(f"Heap: list-fix alone saves {list_saving:.1f}%,  spool-fix alone saves {spool_saving:.1f}%")


if __name__ == "__main__":
    main()

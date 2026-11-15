"""
/proc-based CPU and memory metrics - mirrors process_status.rs
"""
from __future__ import annotations

import os
import time


def get_page_size_kb() -> int:
    """Return the kernel page size in KB (reads /proc/self/smaps like the Rust version)."""
    with open("/proc/self/smaps") as f:
        for line in f:
            if line.startswith("KernelPageSize:"):
                return int(line.split()[1])
    raise RuntimeError("Cannot determine KernelPageSize from /proc/self/smaps")


def get_memory_usage_kb(pid: int, page_size_kb: int) -> int:
    """
    Return private memory usage of *pid* in KB.

    Formula from QPS: (rss_pages - shared_pages) * page_size_kb
    Reads /proc/<pid>/statm: total rss shared text lib data dirty
    """
    with open(f"/proc/{pid}/statm") as f:
        fields = f.read().split()
    rss_pages = int(fields[1])
    shared_pages = int(fields[2])
    return (rss_pages - shared_pages) * page_size_kb


def get_cpu_time(pid: int) -> int:
    """
    Return total CPU time (utime + stime) in clock ticks for *pid*.
    Fields 14 and 15 of /proc/<pid>/stat (1-indexed).
    """
    with open(f"/proc/{pid}/stat") as f:
        fields = f.read().split()
    utime = int(fields[13])  # 0-indexed
    stime = int(fields[14])
    return utime + stime


def clock_ticks_per_second() -> int:
    """SC_CLK_TCK - usually 100 on x86_64."""
    return os.sysconf("SC_CLK_TCK")


def measure_cpu_percent(pid: int, interval_ms: int = 100) -> float:
    """
    Sample CPU time twice over *interval_ms* ms and return usage as a percentage.
    Returns 0.0 for dead/unreadable processes.
    """
    tps = clock_ticks_per_second()
    try:
        t0 = get_cpu_time(pid)
        time.sleep(interval_ms / 1000)
        t1 = get_cpu_time(pid)
    except (FileNotFoundError, ProcessLookupError, ValueError):
        return 0.0

    delta_ticks = t1 - t0
    usage_ms = delta_ticks * 1000 / tps
    return usage_ms * 100.0 / interval_ms

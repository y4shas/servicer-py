"""
Show status table for all servicer-managed services - mirrors handle_show_status.rs

Uses rich.Table instead of cli_table, and humanize for byte formatting.
CPU measurement uses the same two-sample /proc approach as the Rust version.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field

import humanize
from rich.console import Console
from rich.table import Table

from ser.utils.process_status import (
    clock_ticks_per_second,
    get_cpu_time,
    get_memory_usage_kb,
    get_page_size_kb,
)
from ser.utils.service_names import get_short_name, list_servicer_services
from ser.utils.systemd import get_active_state, get_main_pid, get_unit_file_state

SLEEP_MS = 100  # CPU sampling interval - matches Rust constant


@dataclass
class ServiceStatus:
    pid: int
    name: str
    active: str
    enabled_on_boot: bool
    cpu: float
    memory: str


def handle_show_status() -> None:
    """Print a rich table of all .ser.service services, with PID, state, CPU %, memory."""
    try:
        page_size_kb = get_page_size_kb()
    except Exception:
        page_size_kb = 4  # sane default

    full_names = list_servicer_services()
    statuses: list[ServiceStatus] = []

    for full_name in full_names:
        active = get_active_state(full_name)
        unit_state = get_unit_file_state(full_name)
        enabled = unit_state in ("enabled", "enabled-runtime")

        if active == "active":
            pid = get_main_pid(full_name)
            try:
                mem_kb = get_memory_usage_kb(pid, page_size_kb)
                memory_str = humanize.naturalsize(mem_kb * 1024, binary=False)
            except Exception:
                memory_str = "0"
        else:
            pid = 0
            memory_str = "0"

        statuses.append(ServiceStatus(
            pid=pid,
            name=get_short_name(full_name),
            active=active,
            enabled_on_boot=enabled,
            cpu=0.0,
            memory=memory_str,
        ))

    # CPU sampling: take two snapshots SLEEP_MS apart
    tps = clock_ticks_per_second()
    initial_times: list[int] = []
    for s in statuses:
        if s.active == "active" and s.pid:
            try:
                initial_times.append(get_cpu_time(s.pid))
            except Exception:
                initial_times.append(0)
        else:
            initial_times.append(0)

    time.sleep(SLEEP_MS / 1000)

    for i, s in enumerate(statuses):
        if s.active == "active" and s.pid:
            try:
                final_time = get_cpu_time(s.pid)
            except Exception:
                final_time = initial_times[i]
            delta = final_time - initial_times[i]
            usage_ms = delta * 1000 / tps
            s.cpu = usage_ms * 100.0 / SLEEP_MS

    # Render table
    table = Table(show_header=True, header_style="bold")
    table.add_column("pid")
    table.add_column("name")
    table.add_column("active")
    table.add_column("enable on boot")
    table.add_column("cpu %")
    table.add_column("memory")

    for s in statuses:
        active_color = "green" if s.active == "active" else "red"
        table.add_row(
            str(s.pid) if s.pid else "-",
            s.name,
            f"[{active_color}]{s.active}[/{active_color}]",
            str(s.enabled_on_boot).lower(),
            f"{s.cpu:.1f}",
            s.memory,
        )

    console = Console()
    if not statuses:
        console.print("[dim]No servicer-managed services found.[/dim]")
    else:
        console.print(table)

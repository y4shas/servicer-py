"""
Stream journald logs for a service - mirrors handle_show_logs.rs
"""
from __future__ import annotations

import subprocess

import typer

from ser.utils.service_names import get_full_name


def handle_show_logs(name: str, lines: int = 15, follow: bool = False) -> None:
    """Display journalctl logs for a service."""
    full_name = get_full_name(name)
    cmd = ["journalctl", "-u", full_name, "-n", str(lines)]
    if follow:
        cmd.append("--follow")

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        typer.echo(f"Error viewing logs: {e}", err=True)
        raise typer.Exit(1)
    except FileNotFoundError:
        typer.echo("journalctl not found. Is systemd installed?", err=True)
        raise typer.Exit(1)

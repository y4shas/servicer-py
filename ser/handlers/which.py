"""
Print file paths for a service — mirrors handle_print_paths.rs
"""
from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

from ser.utils.service_names import get_full_name, get_service_file_path
from ser.utils.systemd import get_unit_path


def handle_print_paths(name: str) -> None:
    """Print the .service file path and D-Bus unit object path."""
    full_name = get_full_name(name)
    service_file = get_service_file_path(full_name)
    unit_path = get_unit_path(full_name)

    if not service_file.exists():
        typer.echo(f"Service '{name}' not found at {service_file}.", err=True)
        raise typer.Exit(1)

    table = Table(show_header=True, header_style="bold")
    table.add_column("name")
    table.add_column("path")
    table.add_row("Service file", str(service_file))
    table.add_row("Unit file", unit_path)

    Console().print(table)

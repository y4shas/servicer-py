"""
Delete a service — mirrors handle_delete_service.rs

Stops and disables the service, removes the .service file, then daemon-reloads.
"""
from __future__ import annotations

import typer

from ser.utils.service_actions import daemon_reload, disable_service, stop_service
from ser.utils.service_names import get_full_name, get_service_file_path
from ser.utils.systemd import get_active_state, get_unit_file_state


def handle_delete_service(name: str, print_status: bool = True) -> None:
    full_name = get_full_name(name)
    path = get_service_file_path(full_name)

    if not path.exists():
        typer.echo(f"Service '{name}' not found.", err=True)
        raise typer.Exit(1)

    # Stop if running
    if get_active_state(full_name) == "active":
        stop_service(full_name)
        typer.echo(f"Stopped '{name}'.")

    # Disable if enabled
    unit_state = get_unit_file_state(full_name)
    if unit_state in ("enabled", "enabled-runtime"):
        disable_service(full_name)
        typer.echo(f"Disabled '{name}'.")

    path.unlink()
    daemon_reload()
    typer.echo(f"Service '{name}' deleted.")

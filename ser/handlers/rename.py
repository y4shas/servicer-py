"""
Rename a service — mirrors handle_rename_service.rs

If the service is running, stops it, renames the .service file, then restarts.
Always daemon-reloads after the rename.
"""
from __future__ import annotations

import shutil

import typer

from ser.utils.service_actions import daemon_reload, start_service, stop_service
from ser.utils.service_names import get_full_name, get_service_file_path
from ser.utils.systemd import get_active_state


def handle_rename_service(name: str, new_name: str) -> None:
    old_full = get_full_name(name)
    new_full = get_full_name(new_name)
    old_path = get_service_file_path(old_full)
    new_path = get_service_file_path(new_full)

    if not old_path.exists():
        typer.echo(f"Service '{name}' not found.", err=True)
        raise typer.Exit(1)

    if new_path.exists():
        typer.echo(f"A service named '{new_name}' already exists.", err=True)
        raise typer.Exit(1)

    was_active = get_active_state(old_full) == "active"

    if was_active:
        stop_service(old_full)
        typer.echo(f"Stopped '{name}'.")

    shutil.copy2(str(old_path), str(new_path))
    old_path.unlink()
    daemon_reload()
    typer.echo(f"Renamed '{name}' → '{new_name}'.")

    if was_active:
        start_service(new_full)
        typer.echo(f"Started '{new_name}'.")

    from ser.handlers.status import handle_show_status
    handle_show_status()

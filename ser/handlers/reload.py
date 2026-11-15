"""
Reload a service - mirrors handle_reload_service.rs
"""
from __future__ import annotations

import typer

from ser.utils.service_actions import reload_service
from ser.utils.service_names import get_full_name


def handle_reload_service(name: str, print_status: bool = True) -> None:
    full_name = get_full_name(name)
    reload_service(full_name)
    typer.echo(f"Service '{name}' reloaded.")

    if print_status:
        from ser.handlers.status import handle_show_status
        handle_show_status()

"""
Start a service — mirrors handle_start_service.rs
"""
from __future__ import annotations

import typer

from ser.utils.service_actions import start_service
from ser.utils.service_names import get_full_name


def handle_start_service(name: str, print_status: bool = True) -> None:
    full_name = get_full_name(name)
    start_service(full_name)
    typer.echo(f"Service '{name}' started.")

    if print_status:
        from ser.handlers.status import handle_show_status
        handle_show_status()

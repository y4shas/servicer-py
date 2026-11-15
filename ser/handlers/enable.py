"""
Enable a service on boot — mirrors handle_enable_service.rs
"""
from __future__ import annotations

import typer

from ser.utils.service_actions import enable_service
from ser.utils.service_names import get_full_name


def handle_enable_service(name: str, print_status: bool = True) -> None:
    full_name = get_full_name(name)
    enable_service(full_name)
    typer.echo(f"Service '{name}' enabled on boot.")

    if print_status:
        from ser.handlers.status import handle_show_status
        handle_show_status()

"""
Open a text editor to create or edit a .service file - mirrors handle_edit_service_file.rs
"""
from __future__ import annotations

import os
import subprocess
import textwrap

import typer

from ser.utils.service_names import get_full_name, get_service_file_path, get_short_name

_TEMPLATE = textwrap.dedent("""\
    # Generated with Servicer
    [Unit]
    Description=My Service
    After=network.target

    [Service]
    Type=simple
    User={user}

    WorkingDirectory=/path/to/workdir
    ExecStart=/path/to/executable

    [Install]
    WantedBy=multi-user.target
""")


def handle_edit_service(name: str, editor: str = "nano") -> None:
    """Open the .service file in a text editor; create a template if it doesn't exist."""
    full_name = get_full_name(name)
    path = get_service_file_path(full_name)

    # Write a template if the file doesn't exist
    if not path.exists():
        user = os.environ.get("SUDO_USER") or os.environ.get("USER", "root")
        path.write_text(_TEMPLATE.format(user=user))
        typer.echo(f"Created template at {path}")

    try:
        subprocess.run([editor, str(path)], check=True)
    except FileNotFoundError:
        typer.echo(f"Editor '{editor}' not found. Install it or pass --editor <name>.", err=True)
        raise typer.Exit(1)

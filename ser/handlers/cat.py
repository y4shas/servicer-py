"""
Print contents of a .service file - mirrors handle_print_service_file.rs
"""
from __future__ import annotations

import typer
from rich.console import Console
from rich.syntax import Syntax

from ser.utils.service_names import get_full_name, get_service_file_path


def handle_cat_service(name: str) -> None:
    """Print the contents of the .service file with syntax highlighting."""
    full_name = get_full_name(name)
    path = get_service_file_path(full_name)

    if not path.exists():
        typer.echo(f"Service '{name}' not found at {path}.", err=True)
        raise typer.Exit(1)

    content = path.read_text()
    console = Console()
    # INI-style highlighting works well for .service files
    syntax = Syntax(content, "ini", theme="monokai", line_numbers=True)
    console.print(syntax)

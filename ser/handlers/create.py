"""
Create a new systemd service - mirrors handle_create_service.rs
"""
from __future__ import annotations

import os
import sys
import textwrap
from pathlib import Path

import typer

from ser.utils.find_binary_path import find_binary_path
from ser.utils.service_actions import daemon_reload
from ser.utils.service_names import get_full_name, get_service_file_path


# Map file extensions to default interpreters (matches Rust version)
_INTERPRETER_MAP: dict[str, str] = {
    "js": "node",
    "py": "python3",
}


def _detect_interpreter(extension: str | None) -> str | None:
    """Return the default interpreter for the given file extension, or None for binaries."""
    if extension is None:
        return None
    interp = _INTERPRETER_MAP.get(extension)
    if interp is None:
        typer.echo(
            f"No interpreter found for extension '.{extension}'. "
            "Provide one with --interpreter.",
            err=True,
        )
        raise typer.Exit(1)
    return interp


def _build_service_file(
    *,
    user: str,
    working_directory: str,
    exec_start: str,
    auto_restart: bool,
    env_vars: str | None,
) -> str:
    """Render the .service file content (equivalent to formatdoc! in Rust)."""
    restart_line = "Restart=always" if auto_restart else ""

    env_lines = ""
    if env_vars:
        env_lines = "\n".join(
            f"Environment={pair}" for pair in env_vars.split()
        )

    return textwrap.dedent(f"""\
        # Generated with Servicer
        [Unit]
        After=network.target

        [Service]
        Type=simple
        User={user}

        WorkingDirectory={working_directory}
        ExecStart={exec_start}
        {restart_line}
        {env_lines}

        [Install]
        WantedBy=multi-user.target
    """)


def handle_create_service(
    path: Path,
    custom_name: str | None,
    start: bool,
    enable: bool,
    auto_restart: bool,
    custom_interpreter: str | None,
    env_vars: str | None,
    internal_args: list[str],
) -> None:
    """Create a systemd .ser.service file for the given script/binary."""
    if not path.is_file():
        typer.echo(f"Error: {path} is not a file.", err=True)
        raise typer.Exit(1)

    file_name = path.name
    service_name = custom_name or file_name
    full_name = get_full_name(service_name)
    service_file_path = get_service_file_path(full_name)

    if service_file_path.exists():
        typer.echo(
            f"Service '{service_name}' already exists at {service_file_path}. "
            f"Use --name for a custom name or `ser delete {service_name}` to remove it.",
            err=True,
        )
        raise typer.Exit(1)

    # Resolve interpreter
    if custom_interpreter:
        interpreter = custom_interpreter
    else:
        ext = path.suffix.lstrip(".") or None
        interpreter = _detect_interpreter(ext if ext else None)

    # Resolve working directory (handle bare `index.js` with no ./)
    parent = path.parent
    if str(parent) == ".":
        parent = Path.cwd()
    working_directory = str(parent.resolve())

    # Build ExecStart
    sudo_user = os.environ.get("SUDO_USER")
    if interpreter:
        if not sudo_user:
            typer.echo("Warning: not in sudo mode - using interpreter name as-is.", err=True)
            interp_path = interpreter
        else:
            interp_path = find_binary_path(interpreter, sudo_user)
            typer.echo(f"Interpreter path: {interp_path}")
        exec_start = f"{interp_path} {file_name}"
    else:
        exec_start = str(path.resolve())

    if internal_args:
        exec_start += " " + " ".join(internal_args)

    # Determine user for the service (non-root user even when called via sudo)
    service_user = sudo_user or os.environ.get("USER", "root")

    content = _build_service_file(
        user=service_user,
        working_directory=working_directory,
        exec_start=exec_start,
        auto_restart=auto_restart,
        env_vars=env_vars,
    )

    service_file_path.write_text(content)
    daemon_reload()
    typer.echo(
        f"Service '{service_name}' created at {service_file_path}. "
        f"To start run `ser start {service_name}`"
    )

    if start:
        from ser.handlers.start import handle_start_service
        handle_start_service(service_name, print_status=False)
    if enable:
        from ser.handlers.enable import handle_enable_service
        handle_enable_service(service_name, print_status=False)

    from ser.handlers.status import handle_show_status
    handle_show_status()

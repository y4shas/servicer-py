"""
servicer CLI â€” mirrors main.rs (clap â†’ typer)

Entry point: `ser` (defined in pyproject.toml [project.scripts])
"""
from __future__ import annotations

from pathlib import Path
from typing import Annotated, Optional

import typer

app = typer.Typer(
    name="ser",
    help="servicer â€” Simplify service management on systemd.",
    no_args_is_help=True,
    add_completion=False,
)


# create

@app.command()
def create(
    path: Annotated[Path, typer.Argument(help="Path to the script or binary to run")],
    name: Annotated[Optional[str], typer.Option("--name", "-n", help="Custom service name")] = None,
    start: Annotated[bool, typer.Option("--start", "-s", help="Start the service immediately")] = False,
    enable: Annotated[bool, typer.Option("--enable", "-e", help="Enable the service on boot")] = False,
    auto_restart: Annotated[bool, typer.Option("--auto-restart", "-r", help="Restart on failure")] = False,
    interpreter: Annotated[Optional[str], typer.Option("--interpreter", "-i", help="Custom interpreter (name or full path)")] = None,
    env_vars: Annotated[Optional[str], typer.Option("--env-vars", "-v", help='Env vars, e.g. "FOO=BAR GG=WP"')] = None,
    internal_args: Annotated[Optional[list[str]], typer.Argument(help="Args passed to the script (after --)")] = None,
) -> None:
    """Create a systemd service for a file at the given path."""
    from ser.handlers.create import handle_create_service
    handle_create_service(
        path=path,
        custom_name=name,
        start=start,
        enable=enable,
        auto_restart=auto_restart,
        custom_interpreter=interpreter,
        env_vars=env_vars,
        internal_args=internal_args or [],
    )


# edit

@app.command()
def edit(
    name: Annotated[str, typer.Argument(help="Service name, e.g. hello-world")],
    editor: Annotated[str, typer.Option("--editor", help="Text editor to use")] = "nano",
) -> None:
    """Open a text editor to create or edit the .service file for a service."""
    from ser.handlers.edit import handle_edit_service
    handle_edit_service(name, editor=editor)


# start

@app.command()
def start(
    name: Annotated[str, typer.Argument(help="Service name")],
) -> None:
    """Start a service."""
    from ser.handlers.start import handle_start_service
    handle_start_service(name)


# stop

@app.command()
def stop(
    name: Annotated[str, typer.Argument(help="Service name")],
) -> None:
    """Stop a service."""
    from ser.handlers.stop import handle_stop_service
    handle_stop_service(name)


# enable

@app.command()
def enable(
    name: Annotated[str, typer.Argument(help="Service name")],
) -> None:
    """Enable a service to start on boot."""
    from ser.handlers.enable import handle_enable_service
    handle_enable_service(name)


# disable

@app.command()
def disable(
    name: Annotated[str, typer.Argument(help="Service name")],
) -> None:
    """Disable a service from starting on boot."""
    from ser.handlers.disable import handle_disable_service
    handle_disable_service(name)


# delete / rm / remove

@app.command(name="delete")
def delete(
    name: Annotated[str, typer.Argument(help="Service name")],
) -> None:
    """Delete a service (stop + disable + remove .service file). Aliases: rm, remove."""
    from ser.handlers.delete import handle_delete_service
    handle_delete_service(name)


@app.command(name="rm", hidden=True)
def rm(name: Annotated[str, typer.Argument(help="Service name")]) -> None:
    """Alias for delete."""
    from ser.handlers.delete import handle_delete_service
    handle_delete_service(name)


@app.command(name="remove", hidden=True)
def remove(name: Annotated[str, typer.Argument(help="Service name")]) -> None:
    """Alias for delete."""
    from ser.handlers.delete import handle_delete_service
    handle_delete_service(name)


# status / ls

@app.command(name="status")
def status() -> None:
    """View the status of all servicer-managed services."""
    from ser.handlers.status import handle_show_status
    handle_show_status()


@app.command(name="ls", hidden=True)
def ls() -> None:
    """Alias for status."""
    from ser.handlers.status import handle_show_status
    handle_show_status()


# logs

@app.command()
def logs(
    name: Annotated[str, typer.Argument(help="Service name")],
    lines: Annotated[int, typer.Option("--lines", "-n", help="Number of lines to show")] = 15,
    follow: Annotated[bool, typer.Option("--follow", "-f", help="Follow live logs")] = False,
) -> None:
    """View logs for a service (via journalctl)."""
    from ser.handlers.logs import handle_show_logs
    handle_show_logs(name, lines=lines, follow=follow)


# reload

@app.command()
def reload(
    name: Annotated[str, typer.Argument(help="Service name")],
) -> None:
    """Reload a service (requires ExecReload in the unit file)."""
    from ser.handlers.reload import handle_reload_service
    handle_reload_service(name)


# cat

@app.command()
def cat(
    name: Annotated[str, typer.Argument(help="Service name")],
) -> None:
    """Display the contents of the .service file."""
    from ser.handlers.cat import handle_cat_service
    handle_cat_service(name)


# which

@app.command()
def which(
    name: Annotated[str, typer.Argument(help="Service name")],
) -> None:
    """Print the .service file path and D-Bus unit object path."""
    from ser.handlers.which import handle_print_paths
    handle_print_paths(name)


# rename / mv

@app.command(name="rename")
def rename(
    name: Annotated[str, typer.Argument(help="Current service name")],
    new_name: Annotated[str, typer.Argument(help="New service name")],
) -> None:
    """Rename a service. A running service will be restarted. Alias: mv."""
    from ser.handlers.rename import handle_rename_service
    handle_rename_service(name, new_name)


@app.command(name="mv", hidden=True)
def mv(
    name: Annotated[str, typer.Argument(help="Current service name")],
    new_name: Annotated[str, typer.Argument(help="New service name")],
) -> None:
    """Alias for rename."""
    from ser.handlers.rename import handle_rename_service
    handle_rename_service(name, new_name)


# Entry point

if __name__ == "__main__":
    app()

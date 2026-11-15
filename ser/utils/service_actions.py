"""
High-level service control actions - mirrors service_actions.rs
"""
from ser.utils.systemd import (
    manager_disable_unit_files,
    manager_enable_unit_files,
    manager_reload,
    manager_reload_unit,
    manager_start_unit,
    manager_stop_unit,
)


def start_service(full_name: str) -> None:
    """Start a service via D-Bus."""
    manager_start_unit(full_name)


def stop_service(full_name: str) -> None:
    """Stop a service via D-Bus."""
    manager_stop_unit(full_name)


def enable_service(full_name: str) -> None:
    """Enable a service to start on boot."""
    manager_enable_unit_files([full_name])
    manager_reload()


def disable_service(full_name: str) -> None:
    """Disable a service from starting on boot."""
    manager_disable_unit_files([full_name])
    manager_reload()


def reload_service(full_name: str) -> None:
    """Reload a service (requires ExecReload in the unit file)."""
    manager_reload_unit(full_name)


def daemon_reload() -> None:
    """Reload the systemd manager configuration."""
    manager_reload()

"""
D-Bus wrappers for org.freedesktop.systemd1 â€” mirrors systemd.rs

Uses dasbus for clean, Pythonic D-Bus access.
"""
from __future__ import annotations

import re
from functools import lru_cache

from dasbus.connection import SystemMessageBus


# Bus / proxy helpers

@lru_cache(maxsize=1)
def _get_bus() -> SystemMessageBus:
    return SystemMessageBus()


def _manager_proxy():
    """Proxy for org.freedesktop.systemd1.Manager."""
    bus = _get_bus()
    return bus.get_proxy(
        "org.freedesktop.systemd1",
        "/org/freedesktop/systemd1",
    )


def _unit_proxy(object_path: str):
    """Proxy for org.freedesktop.systemd1.Unit at the given D-Bus object path."""
    bus = _get_bus()
    return bus.get_proxy(
        "org.freedesktop.systemd1",
        object_path,
        "org.freedesktop.systemd1.Unit",
    )


def _service_proxy(object_path: str):
    """Proxy for org.freedesktop.systemd1.Service at the given D-Bus object path."""
    bus = _get_bus()
    return bus.get_proxy(
        "org.freedesktop.systemd1",
        object_path,
        "org.freedesktop.systemd1.Service",
    )


# Object-path encoding (matches encode_as_dbus_object_path in systemd.rs)

def _encode_dbus_path(s: str) -> str:
    """Encode a string as a valid D-Bus object path segment (hex-escaping special chars)."""
    result = []
    for c in s:
        if c.isalnum() or c in ("_", "/"):
            result.append(c)
        else:
            result.append(f"_{ord(c):x}")
    return "".join(result)


def get_unit_path(full_service_name: str) -> str:
    """Return the D-Bus object path for a service unit."""
    return f"/org/freedesktop/systemd1/unit/{_encode_dbus_path(full_service_name)}"


# State queries

def get_active_state(full_service_name: str) -> str:
    """Return the ActiveState of a unit, e.g. 'active', 'failed', 'inactive'."""
    try:
        proxy = _unit_proxy(get_unit_path(full_service_name))
        return str(proxy.ActiveState)
    except Exception:
        return "invalid-unit-path"


def get_unit_file_state(full_service_name: str) -> str:
    """Return the UnitFileState, e.g. 'enabled', 'disabled'."""
    try:
        proxy = _unit_proxy(get_unit_path(full_service_name))
        return str(proxy.UnitFileState)
    except Exception:
        return "invalid-unit-path"


def get_main_pid(full_service_name: str) -> int:
    """Return the MainPID of a running service (0 if not running)."""
    try:
        proxy = _service_proxy(get_unit_path(full_service_name))
        return int(proxy.MainPID)
    except Exception:
        return 0


# Manager actions (used by service_actions.py)

def manager_start_unit(full_name: str) -> None:
    _manager_proxy().StartUnit(full_name, "replace")


def manager_stop_unit(full_name: str) -> None:
    _manager_proxy().StopUnit(full_name, "replace")


def manager_reload_unit(full_name: str) -> None:
    _manager_proxy().ReloadUnit(full_name, "replace")


def manager_enable_unit_files(full_names: list[str]) -> None:
    _manager_proxy().EnableUnitFiles(full_names, False, True)


def manager_disable_unit_files(full_names: list[str]) -> None:
    _manager_proxy().DisableUnitFiles(full_names, False)


def manager_reload() -> None:
    """Equivalent to `systemctl daemon-reload`."""
    _manager_proxy().Reload()

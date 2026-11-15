"""
Service name helpers — mirrors service_names.rs
"""
from pathlib import Path

SUFFIX = ".ser.service"
SERVICE_DIR = Path("/etc/systemd/system")


def get_full_name(short: str) -> str:
    """Return the full service name, e.g. 'hello-world' → 'hello-world.ser.service'."""
    return f"{short}{SUFFIX}"


def get_short_name(full: str) -> str:
    """Strip the .ser.service suffix, e.g. 'hello-world.ser.service' → 'hello-world'."""
    return full.removesuffix(SUFFIX)


def is_full_name(name: str) -> bool:
    """Return True if the name ends with .ser.service."""
    return name.endswith(SUFFIX)


def get_service_file_path(full_name: str) -> Path:
    """Absolute path to the .service file."""
    return SERVICE_DIR / full_name


def list_servicer_services() -> list[str]:
    """Return all full service names managed by servicer in /etc/systemd/system/."""
    return sorted(
        p.name
        for p in SERVICE_DIR.iterdir()
        if p.is_file() and is_full_name(p.name)
    )

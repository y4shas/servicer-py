"""
Find the absolute path of a binary as a non-root user - mirrors find_binary_path.rs

`ser create` must run in sudo mode. $PATH in sudo mode doesn't include the
regular user's PATH (e.g. nvm, pyenv), so we run `which` as SUDO_USER.
"""
from __future__ import annotations

import subprocess


def find_binary_path(binary_name: str, user: str) -> str:
    """
    Run `sudo -u <user> bash -i -c 'which <binary>'` and return the resolved path.
    Raises RuntimeError if the binary is not found.
    """
    result = subprocess.run(
        ["sudo", "-u", user, "bash", "-i", "-c", f"which {binary_name}"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"Failed to find '{binary_name}' in PATH for user '{user}'. "
            f"Provide the full path with --interpreter."
        )
    return result.stdout.strip()

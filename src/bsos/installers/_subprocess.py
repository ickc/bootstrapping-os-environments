"""Subprocess helpers with command detection and controlled environments."""

import shutil
import subprocess
from typing import Dict, List, Optional


def find_command(name: str) -> Optional[str]:
    """Locate an executable on ``PATH``, like ``which``."""
    return shutil.which(name)


def require_command(name: str) -> str:
    """Locate an executable or raise :class:`RuntimeError`."""
    path = find_command(name)
    if path is None:
        raise RuntimeError(f"Required command not found: {name}")
    return path


def run(
    cmd: List[str],
    env: Optional[Dict[str, str]] = None,
    check: bool = True,
    **kwargs: object,
) -> "subprocess.CompletedProcess":
    """Run *cmd* with an explicit environment.

    Pass *env* from :meth:`EnvConfig.subprocess_env` to isolate the child
    from the caller's full environment.  *check* defaults to ``True``;
    pass ``check=False`` when the caller wants to inspect ``returncode``.
    """
    return subprocess.run(cmd, env=env, check=check, **kwargs)

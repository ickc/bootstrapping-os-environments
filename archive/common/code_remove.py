#!/usr/bin/env python

import subprocess
from pathlib import Path

import defopt

from bsos import logger


def read(data: str) -> list[str]:
    """Loads list of packages from a string, ignoring those start with a comment."""
    return [line.strip() for line in data.splitlines() if not line.startswith("#")]


def get_vscode_extensions() -> list[str]:
    """Returns a list of installed VSCode extensions."""
    return read(subprocess.check_output(["code", "--list-extensions"]).decode())


def code_remove(packages: list[str]) -> None:
    """Removes VSCode extensions."""
    for package in packages:
        args = ["code", "--uninstall-extension", package]
        logger.info("Running %s", subprocess.list2cmdline(args))
        subprocess.run(args, check=True)


def main(path: Path = Path("code.txt")) -> None:
    """Remove VSCode extensions that are not listed in the given file."""
    with path.open("r", encoding="utf8") as f:
        config_target = read(f.read())
    config_current = get_vscode_extensions()
    code_remove(list(set(config_current) - set(config_target)))


if __name__ == "__main__":
    defopt.run(main)

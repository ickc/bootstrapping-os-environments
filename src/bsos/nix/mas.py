#!/usr/bin/env python3

"""Update flake.nix with the latest mas apps."""

from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path
from typing import cast


def mas_list(
    regex: re.Pattern[str] = re.compile(r" {2,}"),
) -> list[tuple[str, str, str]]:
    """Parse the output of `mas list` and return a list of tuples with the app id, name, and version."""
    out = subprocess.check_output(["/opt/homebrew/bin/mas", "list"], text=True)
    lines = out.split("\n")
    return [cast(tuple[str, str, str], tuple(regex.split(line))) for line in lines if line]


def format_mas_to_nix(apps: list[tuple[str, str, str]]) -> list[str]:
    """Format the list of mas apps to a list of strings that can be written to a flake.nix file."""
    res = [f'  "{app[1]}" = {app[0].strip()};\n' for app in apps]
    res.sort(key=str.lower)
    return res


def write_nix_from_nas(
    path: Path,
    nix_content: list[str],
) -> None:
    """Write the nix content to the flake.nix file."""
    path = Path(path)
    with path.open("w") as file:
        print("{", file=file)
        for line in nix_content:
            file.write(line)
        print("}", file=file)


def main(path: Path) -> None:
    """Update the flake.nix file with the latest mas apps."""
    apps = mas_list()
    nix_content = format_mas_to_nix(apps)
    write_nix_from_nas(path, nix_content)


def cli() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Update flake.nix with the latest mas apps")
    parser.add_argument("path", type=Path, help="The path to the flake.nix file")
    args = parser.parse_args()
    main(args.path)


if __name__ == "__main__":
    cli()

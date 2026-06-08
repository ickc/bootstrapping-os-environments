#!/usr/bin/env python3

import json
import re
import subprocess
from collections import defaultdict
from pathlib import Path
from typing import Any, cast

import defopt
import pandas as pd
import yaml
import yamlloader


def get_executable_paths(
    nix_bin_dir: Path = Path("/run/current-system/sw/bin"),
) -> list[Path]:
    """Get realpath to executables in the nix bin directory."""
    return [path.readlink() for path in nix_bin_dir.iterdir()]


def get_package_install_name(name: str) -> str:
    """Get the package install name by looking it up in a dictionary."""
    return {
        "bash-interactive": "bashInteractive",
        "batdiff": "bat-extras.batdiff",
        "batgrep": "bat-extras.batgrep",
        "batman": "bat-extras.batman",
        "batpipe": "bat-extras.batpipe",
        "batwatch": "bat-extras.batwatch",
        "gcc-wrapper": "gcc14",
        "Image-ExifTool": "exiftool",
        "mpv-with-scripts": "mpv",
        "pam_reattach": "pam-reattach",
        "pandoc-cli": "pandoc",
        "patch": "gnupatch",
        "prettybat": "bat-extras.prettybat",
    }.get(name, name)


def parse_nix_path(
    path: Path,
    version_regex: re.Pattern[str] = re.compile(
        r"^(?P<interpreter>(python|perl)[.0-9]+-)?(?P<package>.+?)(?P<version>-[-_.0-9p]+(pre)?)?(?P<date>\+date=[-0-9]+)?(?P<git>\+git[-0-9]+)?(?P<bin>-bin)?$"
    ),
) -> list[str | bool | Path | None]:
    """Parse a nix path."""
    command = path.name
    parent = path.parent
    assert parent.name == "bin"
    parent = parent.parent
    name = parent.name
    assert parent.parent == Path("/nix/store")
    assert name[32] == "-"
    symbolink_name = name[33:]
    match = version_regex.match(symbolink_name)
    if not match:
        raise ValueError(f"Invalid format for: {symbolink_name}")
    groups = match.groupdict()

    interpreter = groups["interpreter"]
    package = groups["package"]
    version = groups["version"]
    date = groups["date"]
    git = groups["git"]
    is_bin = not groups["bin"]
    if interpreter:
        interpreter = interpreter[:-1]
    if version:
        version = version[1:]
    if date:
        date = date[6:]
    if git:
        git = git[5:]
    return [
        command,
        get_package_install_name(package),
        interpreter,
        package,
        version,
        date,
        git,
        is_bin,
        path,
    ]


def parse_nix_paths(
    nix_bin_dir: Path = Path("/run/current-system/sw/bin"),
) -> pd.DataFrame:
    paths = get_executable_paths(nix_bin_dir)
    df = pd.DataFrame(
        (parse_nix_path(path) for path in paths),
        columns=pd.Index(
            [
                "executable",
                "install",
                "interpreter",
                "package",
                "version",
                "date",
                "git",
                "is_bin",
                "path",
            ]
        ),
    )
    df.set_index("executable", inplace=True)
    return df


def get_package_descriptions() -> dict[str, dict[str, Any]]:
    """Get a mapping of package names to their descriptions from nix."""
    try:
        result = subprocess.run(
            ["nix", "search", "--json", "nixpkgs", ".*"],
            capture_output=True,
            text=True,
            check=True,
        )
        packages = cast(dict[str, dict[str, Any]], json.loads(result.stdout))
        # It is currently expecting it to begin with legacyPackages.aarch64-darwin.
        return {".".join(key.split(".")[2:]): value for key, value in packages.items()}
    except (subprocess.CalledProcessError, FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Warning: Could not fetch package descriptions: {e}")
        return {}


def get_nix_package_meta(name: str) -> dict[str, Any]:
    """Evaluate and return the Nix package meta as a dict.

    Runs:
        nix eval --json f'nixpkgs#{name}.meta'
    """
    cmd = ["nix", "eval", "--json", f"nixpkgs#{name}.meta"]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return cast(dict[str, Any], json.loads(result.stdout))


def read_environment_systemPackages(
    path: Path = Path("flake.nix"),
) -> list[str]:
    """Read environment.systemPackages from flake.nix.

    Read the lines between these:

        with pkgs;
        [
        ...
        ];
    """
    with path.open("r", encoding="utf-8") as f:
        lines = f.readlines()
    # Find the indices of the lines to replace
    start_index = -1
    end_index = -1

    for i, line in enumerate(lines):
        if line.strip() == "with pkgs;":
            start_index = i + 2
        elif start_index != -1 and line.strip().startswith("]"):
            end_index = i
            break

    if start_index == -1 or end_index == -1:
        raise ValueError("Could not find the target lines in the file.")

    return [line.strip() for line in lines[start_index:end_index]]


def command2package(
    path: Path,
    *,
    nix_bin_dir: Path = Path("/run/current-system/sw/bin"),
) -> None:
    """Write the command to package mapping to a file."""
    df = parse_nix_paths(nix_bin_dir)
    df.to_csv(path)


def check_package_supported(
    flake_path: Path,
) -> None:
    packages = (p for p in read_environment_systemPackages(flake_path) if not p.startswith("#"))
    for package in packages:
        if get_nix_package_meta(package)["unsupported"]:
            print(package)


def package2command(
    path: Path,
    *,
    flake_path: Path = Path("flake.nix"),
    nix_bin_dir: Path = Path("/run/current-system/sw/bin"),
) -> None:
    """Write the package to command mapping to a file."""
    packages = set(p.split("_")[0] for p in read_environment_systemPackages(flake_path))
    df = parse_nix_paths(nix_bin_dir)

    installed = set(df.install.tolist())
    excess = installed - packages
    if excess:
        print(f"Installed but not in {flake_path}:")
        for i in sorted(excess):
            print(f"\t{i}")
    no_bin = packages - installed
    if no_bin:
        print(f"Installed but not in {nix_bin_dir}:")
        for i in sorted(no_bin):
            print(f"\t{i}")

    descriptions = get_package_descriptions()
    commands_by_install: defaultdict[str, list[str]] = defaultdict(list)
    for name, row in df.iterrows():
        commands_by_install[str(row.install)].append(str(name))

    # sort dict and its values
    result: dict[str, dict[str, Any]] = {}
    for k, commands in sorted(commands_by_install.items()):
        temp: dict[str, Any] = {
            "command": sorted(commands),
        }
        desc = descriptions.get(k)
        if desc:
            temp.update(desc)
        result[k] = temp
    with path.open("w", encoding="utf-8") as f:
        yaml.dump(result, f, Dumper=yamlloader.ordereddict.CSafeDumper)


def cli() -> None:
    defopt.run([command2package, package2command, check_package_supported])


if __name__ == "__main__":
    cli()

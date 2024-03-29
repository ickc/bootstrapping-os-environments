#!/usr/bin/env python

"""Create a conda environment YAML file from our config files.

This should be a self-contained, stdlib only script to be runnable on
new systems with just Python and conda.
"""

from __future__ import annotations

import argparse
import csv
import os
import platform
import sys
from logging import getLogger
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any

__version__: str = "0.6"

PY2_PACKAGES: list[str] = [
    "weave",
    "functools32",
    "future",
    "futures",
    "subprocess32",
    "backports.weakref",
    "backports.functools_lru_cache",
    "backports_abc",
    "pathlib2",
    "funcsigs",
    "pathlib2",
]
DARWIN_PACKAGES: list[str] = ["python.app"]
CHANNEL_LUT: dict[str, list[str]] = {
    "conda-forge": ["conda-forge"],
    "defaults": ["defaults", "conda-forge"],
    "intel": ["intel", "defaults", "conda-forge"],
}
MPICH_EXTERNAL: str = "mpich={version}.*=external_*"

logger = getLogger(__name__)


def read_txt(path: Path) -> list[str]:
    with open(path, "r") as f:
        return [line_ for line in f if (line_ := line.strip()) and not line_.startswith("#")]


def _str_to_bool(string: str) -> bool:
    """Help casting boolean from CSV to bool type."""
    s = string.lower()
    if s == "true":
        return True
    elif s == "false":
        return False
    elif s == "none":
        return None
    else:
        raise ValueError(f"Cannot convert to bool: {string}")


def read_csv(path: Path, version: str) -> list[str]:
    with path.open("r") as f:
        data = list(csv.reader(f))
    columns = data[0]
    if version not in columns:
        raise ValueError(f"Version {version} not specified in file {path}.")
    override_key = f"{version}-override"
    packages: list[dict[str, str | bool]] = [dict(zip(columns, datum)) for datum in data[1:]]
    package_specs: list[str] = []
    for package in packages:
        # version, channel, *-override can be empty string
        if not _str_to_bool(package["ignored"]) and _str_to_bool(package[version]):
            package_spec = ""
            if override_key in package:
                package_spec = package[override_key]  # type: ignore[assignment]
            if not package_spec:
                n = package["name"]
                v = package["version"]
                c = package["channel"]
                package_spec = f"{c}::{n}{v}" if c else f"{n}{v}"
            package_specs.append(package_spec)
    return package_specs


def read_env(path: Path, version: str) -> list[str]:
    ext = path.suffix
    if ext == ".txt":
        return read_txt(path)
    elif ext == ".csv":
        return read_csv(path, version)
    else:
        raise ValueError(f"Unknown suffix {ext}.")


def cook_yaml(
    python_version: str = "3",
    channel: str = "defaults",
    name: str = "all",
    prefix: str | None = None,
    conda_paths: list[Path] = [],
    pip_paths: list[Path] = [],
    mpi: str | None = None,
    pypy: bool = False,
) -> dict:
    python_full_version = f"pypy{python_version}" if pypy else python_version
    conda_envs: list[str] = sum((read_env(conda_path, python_full_version) for conda_path in conda_paths), [])
    pip_envs: list[str] = sum((read_env(pip_path, python_full_version) for pip_path in pip_paths), [])

    dict_: dict[str, Any] = {}

    # channel
    dict_["channels"] = CHANNEL_LUT[channel]

    dict_["dependencies"] = conda_envs
    if platform.system() == "Darwin":
        dict_["dependencies"] += DARWIN_PACKAGES

    # python_version
    python_version_major = python_version[0]
    if pypy:
        dict_["dependencies"] += ["pypy", f"pypy{python_version}"]
    else:
        dict_["dependencies"].append(f"python={python_version}")
    if channel == "intel":
        dict_["dependencies"].append(f"intelpython{python_version_major}_core")
    if python_version_major == 2:
        dict_["dependencies"] += PY2_PACKAGES
        # conda cannot resolve subprocess32 and mypy in python2
        try:
            dict_["dependencies"].remove("mypy")
        except ValueError:
            pass

    if mpi is None:
        pass
    elif mpi in ("mpich", "openmpi"):
        dict_["dependencies"].append(mpi)
    elif mpi == "cray":
        logger.warning("Please run cray-mpi4py.sh to install mpi4py compiled using Cray compiler.")
    # e.g. external-3.4
    elif mpi.startswith("external"):
        # https://conda-forge.org/docs/user/tipsandtricks.html?highlight=hpc#using-external-message-passing-interface-mpi-libraries
        version = mpi.split("-")[-1]
        dict_["dependencies"].append(MPICH_EXTERNAL.format(version=version))
    else:
        raise ValueError(f"Unknown mpi choice {mpi}.")
    if mpi is not None and mpi != "cray":
        dict_["dependencies"].append("mpi4py")

    if pip_envs:
        dict_["dependencies"] += [
            "pip",
            {"pip": pip_envs},
        ]

    # name
    dict_["name"] = f'{name}{"".join(python_version.split("."))}-{channel}'
    # prefix
    if prefix:
        dict_["prefix"] = os.path.join(prefix, dict_["name"])
    return dict_


def cli() -> None:
    parser = argparse.ArgumentParser(description="Generate conda environment YAML file.")

    parser.add_argument("-o", "--yaml", type=argparse.FileType("w"), default=sys.stdout, help="Output YAML.")
    parser.add_argument("-v", "--version", type=str, default="3", help="python version. 2, 3, or 3.x. Default: 3")
    parser.add_argument(
        "-c", "--channel", type=str, default="defaults", help="conda channel. e.g. intel, defaults. Default: defaults"
    )
    parser.add_argument("-n", "--name", type=str, default="all", help="prefix of the name of environment. Default: all")
    parser.add_argument(
        "-p",
        "--prefix",
        type=str,
        help="Full path to conda environment prefix. If not specified, conda's default will be used.",
    )
    parser.add_argument(
        "-C",
        "--conda-txt",
        type=Path,
        nargs="+",
        help="path to a file that contains the list of conda packages to be installed. Can be more than 1.",
        default=[],
    )
    parser.add_argument(
        "-P",
        "--pip-txt",
        nargs="+",
        help="path to a file that contains the list of pip packages to be installed. Can be more than 1.",
        default=[],
    )
    parser.add_argument(
        "-m",
        "--mpi",
        type=str,
        help=(
            "custom version of mpi4py if sepecified. Valid options: mpich/openmpi; external-* for using external mpich"
            " e.g. external-3.4 means mpich=3.4.*=external_*; cray for custom build using cray compiler."
        ),
    )
    parser.add_argument("--pypy", action="store_true", help="install pypy, install CPython if not specified")

    parser.add_argument("-V", action="version", version="%(prog)s {}".format(__version__))

    args = parser.parse_args()

    dict_ = cook_yaml(
        python_version=args.version,
        channel=args.channel,
        name=args.name,
        prefix=args.prefix,
        conda_paths=args.conda_txt,
        pip_paths=args.pip_txt,
        mpi=args.mpi,
        pypy=args.pypy,
    )
    try:
        import yaml

        yaml.dump(dict_, args.yaml, default_flow_style=False)
    except ImportError:
        import json

        print(json.dumps(dict_), file=args.yaml)


if __name__ == "__main__":
    cli()

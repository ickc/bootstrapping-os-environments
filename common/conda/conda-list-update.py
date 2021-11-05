# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.13.0
#   kernelspec:
#     display_name: all39-defaults
#     language: python
#     name: all39-defaults
# ---

# %%
from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
from itertools import product
from collections import OrderedDict
from functools import partial
from logging import getLogger
from typing import Iterable, Sequence

from IPython.display import display

import numpy as np
import pandas as pd
import ujson
import yaml
import yamlloader
from conda.cli.python_api import run_command, Commands
from conda.history import History
from map_parallel import map_parallel

from conda_env import PY2_PACKAGES

logger = getLogger(__name__)

CONDA = "mamba"
conda_path = Path("~/mambaforge/bin").expanduser()
os.environ["PATH"] = os.pathsep.join((str(conda_path), os.environ["PATH"]))


def get_all_conda_envs() -> list[str]:
    """Obtain all conda environment paths excluding base/root using conda's Python API."""
    return [
        env
        for env in ujson.loads(run_command(Commands.INFO, "--json")[0])["envs"]
        if "/envs/" in env  # filter out the root/base env
    ]


def conda_list(env: str) -> pd.DataFrame:
    """`conda list` of environment as a DataFrame using conda's Python API.

    This one uses the conda Python API that excludes pip installed packages.
    """
    data = ujson.loads(run_command(Commands.LIST, "--prefix", env, "--json")[0])
    df = pd.DataFrame(data)
    df.set_index("name", inplace=True)
    return df


def conda_list_subprocess(env: str) -> pd.DataFrame:
    """`conda list` of environment as a DataFrame using cli.

    This one uses the cli directly that includes pip installed packages.
    """
    cmd = (
        CONDA,
        "list",
        "--prefix",
        env,
        "--json",
    )
    res = subprocess.run(cmd, stdout=subprocess.PIPE)
    if res.returncode != 0:
        logger.critical(f"Failed at command {subprocess.list2cmdline(cmd)}")
        raise RuntimeError(res)
    data = ujson.loads(res.stdout)
    df = pd.DataFrame(data)
    df.set_index("name", inplace=True)
    return df


def conda_check_compat_python_version(
    version: str,
    package: str,
    channels: list[str] = ["defaults", "conda-forge"],
    debug: bool = False,
) -> bool:
    """Check if a package is compatible with a Python version.

    :param version: can be a dot-delimited version string for CPython, or a pypy version such as pypy3.6.
    """
    args = [
        CONDA,
        "create",
        "--dry-run",
        "--json",
        "-n",
        "conda_check_compat_python_version",
        package,
    ]
    if version.startswith("pypy"):
        args += [
            "pypy",
            version,
        ]
        if len(channels) != 1 or channels[0] != "conda-forge":
            logger.warn(
                f"channels should be set to conda-forge only for {version}, continue..."
            )
    else:
        args.append(f"python={version}")
    if channels:
        for ch in channels:
            args += ["--channel", ch]
    res = subprocess.run(args, stdout=subprocess.PIPE)
    if debug:
        logger.debug(subprocess.list2cmdline(args))
        yaml.dump(ujson.loads(res.stdout), stream=sys.stderr)
    return not bool(res.returncode)


def conda_check_compat_python_versions(
    version: str,
    packages: list[str],
    channels: list[str] = ["defaults", "conda-forge"],
    debug: bool = False,
    processes: int = os.cpu_count(),
) -> list[bool]:
    return map_parallel(
        partial(
            conda_check_compat_python_version,
            version,
            channels=channels,
            debug=debug,
        ),
        packages,
        mode="multithreading",
        processes=processes,
    )


def get_user_installed_packages(env: str) -> list[str]:
    """return user installed packages in prefix `env`.

    using undocumented conda Python API, see
    https://github.com/conda/conda/issues/4545#issuecomment-469984684
    """
    history = History(env)
    return history.get_requested_specs_map().keys()


def filter_channels(env, channels=("pypi",)) -> Sequence[str]:
    """return packages from `channels` in environment `env`."""
    df = conda_list_subprocess(env)
    return df[df.channel.isin(channels)].index


def map_union(func: callable, iterables: Iterable) -> set:
    """set union of the results from `func` applied to items in `iterables`."""
    return set().union(*(set(func(item)) for item in iterables))


def get_url(version: str, os: str) -> str:
    """Get url to Anaconda's webpage listing a table of supported packages.

    This should be updated often as Anaconda's webpages evolved.
    """
    assert os in ("linux", "osx")
    if version == "2.7":
        # from https://docs.anaconda.com/anaconda/packages/oldpkglists/
        url = "https://docs.anaconda.com/anaconda/packages/old-pkg-lists/2019.10/py{version}_{os}-64/"
    else:
        # from https://docs.anaconda.com/anaconda/packages/pkg-docs/
        url = "https://docs.anaconda.com/anaconda/packages/py{version}_{os}-64/"
    return url.format(version=version, os=os)


def get_df(version: str, os: str) -> pd.DataFrame:
    """Get table of packages from Anaconda's support page in DataFrame."""
    df = pd.read_html(get_url(version, os), header=0, index_col=0)[0]
    assert np.all(df["In Installer"].isna())
    df.drop("In Installer", axis=1, inplace=True)
    return df


def diff(left: pd.DataFrame, right: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return a DataFrame where the index is exclusive to each on the left & right."""
    df_left = get_df(*left)
    df_right = get_df(*right)

    idx_left = set(df_left.index)
    idx_right = set(df_right.index)

    idx_left_only = idx_left - idx_right
    idx_right_only = idx_right - idx_left
    return df_left.loc[idx_left_only], df_right.loc[idx_right_only]


def parse_txt(path: str) -> set[str]:
    """Parse the txt format used in specifying packages.

    the convention is that

    - starts with ``#`` is a package to be ignored in installation
    - starts with ``#*`` is a comment
    - optionally has `::` for conda channel delimiter and channel will be ignored here
    - optionally has version pinned by `=` and will be ignored here
    """
    with open(path, "r") as f:
        return set(
            package
            for word in f.readlines()
            if (package := word.lstrip("#").strip().split("::")[-1].split("=")[0])
            and not package.startswith("*")
        )


# %%
all_conda_envs = get_all_conda_envs()
all_conda_envs

# %% [markdown]
# List of environments that will be inspected:

# %%
envs = [env for env in all_conda_envs if "-" in (env_name := env.split("/")[-1])]
envs


# %% [markdown]
# # Conda


# %%
# set of all user installed packages in envs
conda_packages = map_union(get_user_installed_packages, envs)
conda_all = (
    parse_txt("conda.txt") | parse_txt("conda-all.txt") | parse_txt("conda-CPython.txt")
)
conda_all2 = conda_all | set(PY2_PACKAGES)

# %% [markdown]
# User installed packages not in `conda-all.txt` or `conda.txt`

# %%
list(map(print, sorted(conda_packages - conda_all2)));

# %% [markdown]
# in `conda-all.txt` or `conda.txt` but not installed

# %%
list(map(print, sorted(conda_all2 - conda_packages)));

# %% [markdown]
# # pip

# %%
# all pypi packages from envs
pip_packages = map_union(filter_channels, envs)
pip_all = parse_txt("pip.txt")

# %% [markdown]
# pypi packages not in `pip.txt`

# %%
list(map(print, sorted(pip_packages - pip_all)));

# %% [markdown]
# in `pip.txt` but not installed

# %%
list(map(print, sorted(pip_all - pip_packages)));

# %% [markdown]
# # Inspect packages not compatible with a Python version

# %%
version_check = "3.10"
conda_all_tuple = tuple(conda_all)
conda_compat = conda_check_compat_python_versions(version_check, conda_all_tuple)
df_compat = pd.DataFrame(conda_compat, index=conda_all_tuple, columns=["is_compat"])
print(
    f"These are not compatible with {version_check}:\n",
    df_compat[~df_compat.is_compat].index.values,
)
print(
    f"{df_compat.is_compat.sum()} packages are compatible with {version_check} out of {df_compat.shape[0]}."
)

# %% [markdown]
# # Inspect packages not compatible with pypy3.6
#
# Warning: this is not correct. conda might actually install both pypy and CPython in the same env. Giving this up for now.

# %%
conda_compat_pypy = conda_check_compat_python_versions(
    "pypy3.6",
    conda_all_tuple,
    channels=["conda-forge"],
)
df_compat_pypy = pd.DataFrame(
    conda_compat_pypy,
    index=conda_all_tuple,
    columns=["is_compat"],
)
print(
    "These are not compatible with pypy3.6:\n",
    df_compat_pypy[~df_compat_pypy.is_compat].index.values,
)
print(
    f"{df_compat_pypy.is_compat.sum()} packages are compatible with pypy3.6 out of {df_compat_pypy.shape[0]}."
)

# %% [markdown]
# # Inspect packages not supported by Anaconda

# %%
versions = ("2.7", "3.6", "3.7", "3.8", "3.9")
oses = ("osx", "linux")

# %% [raw]
# for version in versions:
#     for os_ in oses:
#         print(version, os_)
#         display(get_df(version, os_))

# %% [raw]
# versions_oses = list(product(versions, oses))
# n = len(versions_oses)
# for i in range(n):
#     for j in range(i + 1, n):
#         version, os_ = versions_oses[i]
#         version_right, os_right = versions_oses[j]
#
#         df_left, df_right = diff((version, os_), (version_right, os_right))
#         print((version, os_), (version_right, os_right))
#         display(df_left)
#         display(df_right)

# %%
version = "3.9"
os_ = "linux"

# %%
df = get_df(version, os_)
conda_all - set(df.index.values)

# %% [markdown]
# # Intersection of Anaconda supported packages
#
# Create an environment named `acx`, which stands for Anaconda extended, as an intersection of packages installed and those supported by Anaconda

# %%
df_linux = get_df(version, "linux")

# %%
df_mac = get_df(version, "osx")

# %%
conda_supported_packages_linux = set(df_linux.index)
conda_supported_packages_mac = set(df_mac.index)
conda_supported_packages = conda_supported_packages_linux | conda_supported_packages_mac

# %%
len(conda_supported_packages_mac), len(conda_supported_packages_linux), len(
    conda_supported_packages
)

# %%
# packages in conda_all.txt or conda.txt, that's supported by Anaconda
conda_filtered_linux = conda_all & conda_supported_packages_linux
conda_filtered_mac = conda_all & conda_supported_packages_mac
conda_filtered = conda_filtered_mac & conda_filtered_linux
len(conda_filtered), len(conda_filtered_mac), len(
    conda_filtered_linux
), conda_filtered_linux - conda_filtered_mac
conda_filtered.update({"anaconda", "panflute", "cytoolz"})
conda_filtered = sorted(conda_filtered)
len(conda_filtered)

# %%
with open("acx.yml", "w") as f:
    yaml.dump(
        OrderedDict(
            (
                ("name", "acx"),
                ("channels", ["defaults"]),
                ("dependencies", conda_filtered),
            )
        ),
        f,
        Dumper=yamlloader.ordereddict.CSafeDumper,
        default_flow_style=False,
    )

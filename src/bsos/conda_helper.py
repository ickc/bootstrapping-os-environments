from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import subprocess  # nosec
from functools import partial
from logging import getLogger
from typing import Generator, Iterable, Sequence

import psutil
import numpy as np
import pandas as pd
import json
from conda.cli.python_api import run_command, Commands
from conda.history import History
from map_parallel import map_parallel
from shutil import which
from functools import cached_property

logger = getLogger(__name__)

CONDA: str = "mamba"
temp = which(CONDA)
if temp is None:
    CONDA = "conda"
    temp = which(CONDA)
if temp is None:
    raise RuntimeError("Cannot find mamba/conda in your PATH.")
CONDA_PATH = Path(temp)
del temp


class CondaPath:

    def __init__(self):
        #: Base directory of conda installation.
        #: E.g. ~/.mambaforge
        self.conda_base: Path = CONDA_PATH.parent.parent
        #: Base directory of conda installation.
        #: E.g. ~/.mambaforge/envs
        self.conda_envs_base: Path = self.conda_base / "envs"

    def is_sub_env(self, path: str) -> bool:
        """Check if a path is a sub-directory under `conda_envs_base`."""
        return path.startswith(str(self.conda_envs_base))


class CondaRun:
    """Run conda commands using conda API."""
    command: str = ""
    default_args: Sequence[str] = ("--json",)
    log_returncode = logger.warning

    def __init__(self, *args: str) -> None:
        self.args: tuple[str, ...] = args

        cmd = [self.command]
        cmd += list(self.default_args) + [str(arg) for arg in args]
        logger.info("running conda %s", subprocess.list2cmdline(cmd))
        stdout, stderr, returncode = run_command(*cmd)
        self.stdout: str = stdout
        self.stderr: str = stderr
        self.returncode: int = returncode

        self.__post_init__()

    def __post_init__(self) -> None:
        if self.returncode != 0:
            self.log_returncode(f"Return code is non-zero.")

    @property
    def to_dict(self) -> dict:
        return {
            "stdout": self.stdout,
            "stderr": self.stderr,
            "returncode": self.returncode,
        }

    @cached_property
    def data(self) -> dict:
        return json.loads(self.stdout)


class CondaRunSubprocess(CondaRun):
    """Run conda commands using subprocess.

    This means that we can use mamba when it is in the PATH.
    """

    def __init__(self, *args: str) -> None:
        self.args: tuple[str, ...] = args

        cmd = [CONDA, self.command]
        cmd += list(self.default_args) + [str(arg) for arg in args]
        logger.info("running %s", subprocess.list2cmdline(cmd))
        res = subprocess.run(cmd, capture_output=True)  # nosec
        self.stdout: str = res.stdout.decode()
        self.stderr: str = res.stderr.decode()
        self.returncode: int = res.returncode

        self.__post_init__()


class CondaInfo(CondaRun):
    command: str = Commands.INFO

    def envs(self, sub_env_only: bool = False) -> list[Path]:
        """Obtain all conda environment paths.
        
        :param sub_env_only: if True, include sub-environments under base conda directory only.
            This excludes base/root conda environment and other prefix environments."""
        res = self.data["envs"]
        if sub_env_only:
            res = filter(CondaPath().is_sub_env, res)
        return list(map(Path, res))


class CondaInfoSubprocess(CondaRunSubprocess, CondaInfo):
    pass


class CondaList(CondaRun):
    """Conda list a prefix."""
    command: str = Commands.LIST
    default_args: Sequence[str] = ("--json", "--prefix")

    @property
    def prefix(self) -> str:
        args = self.args
        if len(args) != 1:
            raise ValueError("Expecting only 1 specified argument: prefix.")
        return args[0]

    @cached_property
    def dataframe(self) -> pd.DataFrame:
        """`conda list` of environment as a DataFrame using conda's Python API.

        This one uses the conda Python API that excludes pip installed packages.
        """
        df = pd.DataFrame(self.data)
        df.set_index("name", inplace=True)  # type: ignore[call-arg] # stub limitation
        return df

    @property
    def user_installed_packages(self) -> Iterable[str]:
        """return user installed packages in prefix.

        using undocumented conda Python API, see
        https://github.com/conda/conda/issues/4545#issuecomment-469984684
        """
        history = History(self.prefix)
        return history.get_requested_specs_map().keys()

    def filter_channel(self, channel: str) -> Generator[str, None, None]:
        """Get name from those that are from channel `channel`."""
        return (datum["name"] for datum in self.data if datum["channel"] == channel)


class CondaListSubprocess(CondaRunSubprocess, CondaList):
    pass


class CondaCreate(CondaRun):
    command: str = Commands.CREATE
    default_args: Sequence[str] = ("--json", "--dry-run", "-n", "conda_create_dry-run")
    log_returncode = logger.info


class CondaCreateSubprocess(CondaRunSubprocess, CondaCreate):
    pass


@dataclass
class AnacondaSupport:
    """Get url to Anaconda's webpage listing a table of supported packages.

    This should be updated often as Anaconda's webpages evolved.
    """
    version: str
    os: str

    @property
    def url(self) -> str:
        version = self.version
        os = self.os

        if not os in ("linux", "osx"):
            raise ValueError(f"os has to be either linux or osx")
        if version == "2.7":
            # from https://docs.anaconda.com/anaconda/packages/oldpkglists/
            url = "https://docs.anaconda.com/anaconda/packages/old-pkg-lists/2019.10/py{version}_{os}-64/"
        else:
            # from https://docs.anaconda.com/anaconda/packages/pkg-docs/
            url = "https://docs.anaconda.com/anaconda/packages/py{version}_{os}-64/"
        return url.format(version=version, os=os)

    @cached_property
    def dataframe(self) -> pd.DataFrame:
        """Get table of packages from Anaconda's support page in DataFrame."""
        dfs = pd.read_html(self.url, header=0, index_col=0)  # type: ignore[attr-defined] # stub limitation
        if len(dfs) != 1:
            raise RuntimeError("Cannot obtain a unique table from %s", self.url)
        df = dfs[0]
        if np.all(df["In Installer"].isna()):
            df.drop("In Installer", axis=1, inplace=True)
        else:
            logger.info('Not all "In Installer" are empty, not removing column...')
        return df

    def diff(self, other: AnacondaSupport) -> tuple[pd.DataFrame, pd.DataFrame]:
        df_left = self.dataframe
        df_right = other.dataframe

        idx_left = set(df_left.index)
        idx_right = set(df_right.index)

        idx_left_only = idx_left - idx_right
        idx_right_only = idx_right - idx_left
        return df_left.loc[idx_left_only], df_right.loc[idx_right_only]  # type: ignore[call-overload] # stub limitation


def conda_check_compat_python_version_args(
    version: str,
    package: str,
    channels: list[str] = ["conda-forge"],
) -> list[str]:
    args = [package]
    if version.startswith("pypy"):
        args += [
            "pypy",
            version,
        ]
        if len(channels) != 1 or channels[0] != "conda-forge":
            logger.warning(
                "channels should be set to conda-forge only for pypy, continue..."
            )
    else:
        args.append(f"python={version}")
    if channels:
        for ch in channels:
            args += ["--channel", ch]
    return args


def conda_check_compat_python_version(
    version: str,
    package: str,
    channels: list[str] = ["conda-forge"],
) -> bool:
    """Check if a package is compatible with a Python version.

    :param version: can be a dot-delimited version string for CPython (e.g. 3.10), or a pypy version (e.g. pypy3.8).
    """
    args = conda_check_compat_python_version_args(version, package, channels=channels)
    conda_create = CondaCreateSubprocess(*args)
    return conda_create.returncode == 0


def conda_check_compat_python_versions(
    version: str,
    packages: list[str],
    channels: list[str] = ["conda-forge"],
    processes: int = psutil.cpu_count(logical=False),
) -> list[bool]:
    return map_parallel(
        partial(
            conda_check_compat_python_version,
            version,
            channels=channels,
        ),
        packages,
        mode="multithreading",
        processes=processes,
    )

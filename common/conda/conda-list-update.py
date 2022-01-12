# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.13.6
#   kernelspec:
#     display_name: simple
#     language: python
#     name: simple
# ---

# %%
from __future__ import annotations

import logging
from collections import OrderedDict

import pandas as pd
import plotly.express as px
import yaml
import yamlloader
from IPython.display import display
from map_parallel import map_parallel

from bsos.conda_env import PY2_PACKAGES
from bsos.conda_helper import AnacondaSupport, CondaInfo, CondaList, conda_check_compat_python_versions
from bsos.core import Config

logging.getLogger("bsos.conda_helper").setLevel(logging.WARNING)

# %%
# %load_ext autoreload
# %autoreload 2

# %%


def parse_config(path: str) -> set[str]:
    """A convenient function to call Config.packages_including_ingored directly."""
    return Config.from_file(path).packages_including_ingored


def get_df(version: str, os: str) -> pd.DataFrame:
    """A convenient function to call AnacondaSupport.dataframe directly."""
    return AnacondaSupport(version, os).dataframe


# %%
conda_info = CondaInfo()
all_conda_envs = conda_info.envs(sub_env_only=True)
all_conda_envs

# %% [markdown]
# List of environments that will be inspected: (Do you own filtering here.)

# %%
envs = [env for env in all_conda_envs if env.name.startswith("all")]
envs


# %% [markdown]
# # Conda


# %%
conda_list = dict(zip((env.name for env in envs), map_parallel(CondaList, envs)))
conda_list

# %%
conda_packages: set[str] = set().union(*(set(env.user_installed_packages) for env in conda_list.values()))  # type: ignore[assignment]
len(conda_packages)
config = Config.from_csv("conda.csv")
conda_all = config.packages_including_ingored
conda_all2 = conda_all | set(PY2_PACKAGES)

# %% [markdown]
# User installed packages not in `conda-all.txt` or `conda.txt`

# %%
for i in sorted(conda_packages - conda_all2):
    print(i)

# %% [markdown]
# in `conda-all.txt` or `conda.txt` but not installed

# %%
for i in sorted(conda_all - conda_packages):
    print(i)

# %% [markdown]
# # pip

# %%
pip_packages: set[str] = set().union(*(set(env.filter_channel("pypi")) for env in conda_list.values()))  # type: ignore[assignment]
pip_all = parse_config("pip.txt")

# %% [markdown]
# pypi packages not in `pip.txt`

# %%
for i in sorted(pip_packages - pip_all):
    print(i)

# %% [markdown]
# in `pip.txt` but not installed

# %%
for i in sorted(pip_all - pip_packages):
    print(i)

# %% [markdown]
# # Inspect packages not compatible with a Python version

# %%
packages = config.package_spec
df_config = config.dataframe
for version_check in ("3.7", "3.8", "3.9", "3.10", "pypy3.6", "pypy3.7"):
    conda_compat = conda_check_compat_python_versions(version_check, packages)
    df_config[version_check] = conda_compat
    print(
        f"These are not compatible with {version_check}:\n",
        df_config[~df_config[version_check]].index.values,
    )
    print(f"{df_config[version_check].sum()} packages are compatible with {version_check} out of {df_config.shape[0]}.")
config = config.from_dataframe(df_config)
config.to_csv("conda.csv")

# %% [markdown]
# # Inspect packages not supported by Anaconda

# %%
versions = ("2.7", "3.6", "3.7", "3.8", "3.9")
oses = ("osx", "linux")
n_packages = {}
for version in versions:
    for os_ in oses:
        # print(version, os_)
        # display(get_df(version, os_))
        n_packages[(version, os_)] = get_df(version, os_).shape[0]

# %%
df_n_packages = pd.Series(n_packages).unstack()  # type:ignore[attr-defined,arg-type] # stub limitation
df_n_packages

# %%
df_tidy = pd.Series(n_packages).to_frame("n_packages").reset_index()  # type:ignore[arg-type] # stub limitation
df_tidy.columns = ["version", "os", "n_packages"]  # type:ignore[assignment] # stub limitation
px.line(df_tidy, x="version", y="n_packages", color="os")

# %%
version = "3.9"
for os_ in ("linux", "osx"):
    df = get_df(version, os_)
    print(
        f"These packages are listed in txt but not supported by Anaconda on platform {os_}:\n",
        conda_all - set(df.index.values),  # type:ignore[arg-type] # stub limitation
    )

# %% [markdown]
# # Intersection of Anaconda supported packages
#
# Create an environment named `acx`, which stands for Anaconda extended, as an intersection of packages installed and those supported by Anaconda

# %%
version = "3.9"
df_linux = get_df(version, "linux")
df_mac = get_df(version, "osx")
conda_supported_packages_linux = set(df_linux.index)
conda_supported_packages_mac = set(df_mac.index)
conda_supported_packages = conda_supported_packages_linux | conda_supported_packages_mac
len(conda_supported_packages_mac), len(conda_supported_packages_linux), len(conda_supported_packages)

# %%
# packages in conda_all.txt or conda.txt, that's supported by Anaconda
conda_filtered_linux = conda_all & conda_supported_packages_linux
conda_filtered_mac = conda_all & conda_supported_packages_mac
conda_filtered = conda_filtered_mac & conda_filtered_linux
len(conda_filtered), len(conda_filtered_mac), len(conda_filtered_linux), conda_filtered_linux - conda_filtered_mac

# %%
conda_filtered.update({"anaconda", "panflute", "cytoolz"})
len(conda_filtered)

# %%
with open("acx.yml", "w") as f:
    yaml.dump(
        OrderedDict(
            (
                ("name", "acx"),
                ("channels", ["defaults"]),
                ("dependencies", sorted(conda_filtered)),
            )
        ),
        f,
        Dumper=yamlloader.ordereddict.CSafeDumper,
        default_flow_style=False,
    )

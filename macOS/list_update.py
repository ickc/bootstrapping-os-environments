# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.16.0
#   kernelspec:
#     display_name: all310-conda-forge
#     language: python
#     name: all310-conda-forge
# ---

# %%
import re
import subprocess
from io import StringIO
from pathlib import Path
from pprint import pprint

import numpy as np
import pandas as pd
from IPython.display import display

# %% [markdown]
# `is_installed`
# : is installed on the system
#
# `will_be_installed`
# : is in our config file, supposed to be some packages that will be installed
#
# `should_be_installed`
# : is in our config file, and are not commented out (which means that it should not be installed)
#
# # mas

# %%
def read_mas_txt(path: Path) -> pd.DataFrame:
    """Read mas packages file and return a DataFrame of packages."""
    names = []
    packages = []
    should_be_installeds = []
    with path.open("r") as f:
        data = f.read().splitlines()
    data = [d for datum in data if (d := datum.strip())]
    for name, package in zip(data[::2], data[1::2]):
        # name is a comment
        names.append(name[1:].strip())

        if package.startswith("#"):
            packages.append(int(package[1:].strip()))
            should_be_installeds.append(False)
        else:
            packages.append(int(package))
            should_be_installeds.append(True)
    return pd.DataFrame({"name": names, "package": packages, "should_be_installed": should_be_installeds})


# %%
def get_mas_installed() -> pd.DataFrame:
    """Return a list of installed mas packages."""
    res = subprocess.run(["mas", "list"], check=True, capture_output=True)
    df = pd.read_fwf(StringIO(res.stdout.decode()), header=None)
    df.columns = ["package", "name", "version"]
    return df


# %%
df_in = read_mas_txt(Path("mas.txt"))
df_in["will_be_installed"] = True

# %%
df_installed = get_mas_installed()
df_installed["is_installed"] = True
df = df_installed.merge(df_in, how="outer", on="package")
df["name"] = np.where(df.name_x.isna(), df.name_y, df.name_x)
for col in ("name_x", "name_y"):
    df.drop(col, inplace=True, axis=1)
for col in ("is_installed", "should_be_installed", "will_be_installed"):
    df[col].fillna(False, inplace=True)
df = df[["package", "name", "version", "is_installed", "should_be_installed", "will_be_installed"]]

# %%
df_add = df[df.is_installed & ~df.should_be_installed]
if not df_add.empty:
    print("Consider adding these packages to mas.txt:")
    display(df_add)

# %%
df_remove = df[df.should_be_installed & ~df.is_installed]
if not df_remove.empty:
    print("Consider removing these packages from mas.txt")
    display(df_remove)


# %% [markdown]
# # port

# %%
def read_port_txt(path: Path) -> pd.DataFrame:
    with path.open("r") as f:
        data = f.read().splitlines()
    data = [d for datum in data if (d := datum.strip())]
    names = []
    args = []
    should_be_installeds = []
    for line in data:
        should_be_installed = True
        if line.startswith("#"):
            line = line[1:].strip()
            should_be_installed = False
        name, *arg = line.split()
        names.append(name)
        args.append(" ".join(arg))
        should_be_installeds.append(should_be_installed)
    return pd.DataFrame({"package": names, "args": args, "should_be_installed": should_be_installeds})


# %%
def get_port_installed() -> pd.DataFrame:
    res = subprocess.run(["port", "installed", "requested"], check=True, capture_output=True)
    # 1st line is "The following ports are currently installed:"
    lines = res.stdout.decode().splitlines()[1:]
    regex = re.compile(r"^ +([^ ]+) @([^ ]+)( \(active\))?$")
    packages = []
    versions = []
    is_active = []
    for line in lines:
        match = regex.match(line)
        if match:
            packages.append(match.group(1))
            versions.append(match.group(2))
            is_active.append(match.group(3) is not None)
    return pd.DataFrame({"package": packages, "version": versions, "is_active": is_active})


# %%
df_in = read_port_txt(Path("port.txt"))
df_in["will_be_installed"] = True

# %%
df_installed = get_port_installed()
df_active = df_installed[df_installed.is_active].copy()
df_active["is_installed"] = True
df_active.drop("is_active", inplace=True, axis=1)

# %%
df = df_active.merge(df_in, how="outer", on="package")
for col in ("is_installed", "should_be_installed", "will_be_installed"):
    df[col].fillna(False, inplace=True)

# %%
df_add = df[df.is_installed & ~df.should_be_installed]
if not df_add.empty:
    print("Consider adding these packages to port.txt:")
    display(df_add)

# %%
df_remove = df[df.should_be_installed & ~df.is_installed]
if not df_remove.empty:
    print("Consider removing these packages from port.txt")
    display(df_remove)


# %% [markdown]
# # brew

# %%
def read_brew_txt(path: Path) -> set[str]:
    packages = []
    with path.open("r") as f:
        for line in f:
            if line.startswith("#"):
                continue
            if package := line.strip():
                packages.append(package.split("/")[-1])
    return set(packages)


# %%
def get_brew_installed() -> set[str]:
    res = subprocess.run(["brew", "leaves", "--installed-on-request"], check=True, capture_output=True)
    packages = res.stdout.decode().splitlines()
    return set(package.split("/")[-1] for package in packages)


# %%
packages_in = read_brew_txt(Path("brew.txt"))

# %%
packages_installed = get_brew_installed()

# %%
packages_add = packages_installed - packages_in
if packages_add:
    print("Consider adding these packages to brew.txt:")
    pprint(packages_add)

# %%
packages_remove = packages_in - packages_installed
if packages_remove:
    print("Consider removing these packages from brew.txt")
    pprint(packages_remove)

# %% [markdown]
# # brew cask

# %%
def get_brew_cask_installed() -> set[str]:
    res = subprocess.run(["brew", "list", "--cask", "-1"], check=True, capture_output=True)
    packages = res.stdout.decode().splitlines()
    return set(packages)


# %%
packages_in = read_brew_txt(Path("brew-cask.txt")) | read_brew_txt(Path("brew-cask-fonts.txt"))

# %%
packages_installed = get_brew_cask_installed()

# %%
packages_add = packages_installed - packages_in
if packages_add:
    print("Consider adding these packages to brew-cask.txt or brew-cask-font.txt:")
    pprint(packages_add)

# %%
packages_remove = packages_in - packages_installed
if packages_remove:
    print("Consider removing these packages from brew-cask.txt or brew-cask-font.txt")
    pprint(packages_remove)

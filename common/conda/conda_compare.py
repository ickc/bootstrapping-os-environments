#!/usr/bin/env python

from pathlib import Path

import defopt
import yaml

__version__ = "0.1"


def get_dep(path: Path):
    with open(path) as f:
        data = yaml.load(f, Loader=yaml.CSafeLoader)
    # ignoring pip dependencies
    return {dep.split("::")[0].split("=")[0] for dep in data["dependencies"] if type(dep) is str}


def print_diff(path1, path2, dep1, dep2):
    print("=" * 80)
    print(f"Packages in {path1} and not in {path2}:")
    print("-" * 80)
    for i in dep1 - dep2:
        print(i)


def main(path1: Path, path2: Path):
    dep1 = get_dep(path1)
    dep2 = get_dep(path2)
    print_diff(path1, path2, dep1, dep2)
    print_diff(path2, path1, dep2, dep1)


def cli():
    defopt.run(main)


if __name__ == "__main__":
    cli()

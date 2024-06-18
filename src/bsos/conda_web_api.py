from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path

import httpx
import pandas as pd
import platformdirs
import yaml
import yamlloader  # type: ignore


def parse_conda_build(build: str) -> tuple[int, int]:
    """Parse conda build string and return python version as tuple.

    This does not attempt to be robust, just quick and dirty getting the job done here.

    TODO: py313
    """
    if "py312" in build:
        return 3, 12
    if "py311" in build:
        return 3, 11
    if "py310" in build:
        return 3, 10
    if "py39" in build:
        return 3, 9
    if "py38" in build:
        return 3, 8
    if "py37" in build:
        return 3, 7
    if "py36" in build:
        return 3, 6
    if "py35" in build:
        return 3, 5
    if "py34" in build:
        return 3, 4
    if "py27" in build:
        return 2, 7
    else:
        raise ValueError(f"Cannot parse {build}")


async def get_package_info(
    username_package_pairs: list[tuple[str, str]],
    # html page is at https://anaconda.org/{owner}/{name}
    url_format: str = "https://api.anaconda.org/package/{owner}/{name}",
) -> list[dict]:
    """
    Fetch package information from the Anaconda API and return a list of dictionaries.

    Args:
        username_package_pairs (list[tuple[str, str]]): A list of tuples containing owner and package name.

    Returns:
        list[dict]: A list of dictionaries containing package information.
    """

    async def fetch_package_info(owner: str, name: str) -> dict:
        cache_dir: Path = Path(platformdirs.user_cache_dir(appname="bsos", ensure_exists=True))
        file_path: Path = cache_dir / owner / f"{name}.json"

        # Try to load from cache
        if file_path.is_file():
            with file_path.open("r") as f:
                return json.load(f)

        # Fetch from API and cache
        file_path.parent.mkdir(parents=True, exist_ok=True)
        async with httpx.AsyncClient(timeout=None) as client:
            try:
                response = await client.get(url_format.format(owner=owner, name=name))
                response.raise_for_status()
                data = response.json()
            except Exception as e:
                print(f"Failed to fetch {owner}/{name}: {e}")
                raise e

        with file_path.open("w", encoding="utf-8") as f:
            f.write(response.text)

        return data

    tasks = [fetch_package_info(owner, name) for owner, name in username_package_pairs]
    return await asyncio.gather(*tasks)


@dataclass
class CondaPackage:
    data: dict

    @property
    def name(self) -> str:
        return self.data["name"]

    @property
    def owner(self) -> str:
        return self.data["owner"]["login"]

    @property
    def summary(self) -> str:
        return self.data["summary"]

    @property
    def latest_version(self) -> str:
        return self.data["latest_version"]

    @property
    def platforms(self) -> dict[str, str]:
        return self.data["platforms"]

    @cached_property
    def platform_set(self) -> set[tuple[str, str]]:
        return set(self.platforms.items())

    @property
    def doc_url(self) -> str:
        return self.data["doc_url"]

    @cached_property
    def latest_files(self) -> list[dict]:
        files = self.data["files"]
        platforms = self.platform_set
        res = [file for file in files if (file["attrs"]["subdir"], file["version"]) in platforms]
        return res

    @cached_property
    def latest_build_number(self) -> int:
        res = 0
        for file in self.latest_files:
            if n := file["attrs"]["build_number"] > res:
                res = n
        return res

    @cached_property
    def latest_files_with_latest_build_number(self) -> list[dict]:
        return [file for file in self.latest_files if file["attrs"]["build_number"] == self.latest_build_number]

    @cached_property
    def depends_on_python(self) -> bool:
        for file in self.latest_files_with_latest_build_number:
            for dep in file["attrs"]["depends"]:
                if dep.startswith("python "):
                    return True
        return False

    def support(self, platform: str, python_version: tuple[int, int]) -> bool:
        for file in reversed(self.data["files"]):
            platform_cur = file["attrs"]["subdir"]
            if platform_cur == "noarch":
                return True
            # matching platform
            if platform == platform_cur:
                depends_on_python = False
                for dep in file["attrs"]["depends"]:
                    if dep.startswith("python "):
                        depends_on_python = True
                        break
                if not depends_on_python:
                    return True
                # matching python version
                if python_version == parse_conda_build(file["attrs"]["build"]):
                    return True
        return False

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "owner": self.owner,
            "summary": self.summary,
            "latest_version": self.latest_version,
            "platforms": self.platforms,
            "doc_url": self.doc_url,
            "depends_on_python": self.depends_on_python,
            "latest_files_with_latest_build_number": self.latest_files_with_latest_build_number,
        }

    def write_yaml(self, path: Path) -> None:
        path = Path(path)
        with path.open("w", encoding="utf-8") as f:
            yaml.dump(self.to_dict(), f, Dumper=yamlloader.ordereddict.CSafeDumper)


@dataclass
class CondaPackages:
    df: pd.DataFrame
    default_channel: str = "conda-forge"

    @classmethod
    def read_csv(cls, path: Path) -> CondaPackages:
        df = pd.read_csv(
            path,
            index_col=0,
            dtype={
                "version": str,
                "channel": str,
                "ignored": bool,
                "dep-of": str,
                "notes": str,
            },
            na_filter=False,
        )
        return cls(df[["version", "channel", "ignored", "dep-of", "notes"]].copy())

    @cached_property
    def username_package_pairs(self) -> list[tuple[str, str]]:
        return [(row.channel or self.default_channel, name) for name, row in self.df.iterrows()]

    @cached_property
    def data(self) -> list[dict]:
        return asyncio.run(get_package_info(self.username_package_pairs))

    @cached_property
    def packages(self) -> list[CondaPackage]:
        return [CondaPackage(d) for d in self.data]

    def expand_from_data(self) -> None:
        self.df["summary"] = [p.summary for p in self.packages]
        self.df["latest_version"] = [p.latest_version for p in self.packages]
        self.df["doc_url"] = [p.doc_url for p in self.packages]
        self.df["depends_on_python"] = [p.depends_on_python for p in self.packages]

    def to_csv(self, path: Path) -> None:
        self.df.to_csv(path)

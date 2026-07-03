#!/usr/bin/env python

from __future__ import annotations

import asyncio
import json
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from datetime import datetime
from functools import cached_property
from pathlib import Path
from typing import Any, cast

import defopt
import httpx
import pandas as pd
import platformdirs
import tomlkit
import yaml
import yamlloader

CACHE_DIR: Path = Path(platformdirs.user_cache_dir(appname="bsos", ensure_exists=True))

CSV_SOURCE_PACKAGE_COLUMNS: tuple[str, ...] = (
    "channel",
    "ignored",
    "version",
)

CSV_SOURCE_ANNOTATION_COLUMNS: tuple[str, ...] = (
    "depended",
    "notes",
)

CSV_SOURCE_COLUMNS: tuple[str, ...] = CSV_SOURCE_PACKAGE_COLUMNS + CSV_SOURCE_ANNOTATION_COLUMNS

ANACONDA_API_VERSION_COLUMNS: tuple[str, ...] = (
    "latest_version",
    "latest_upload_time",
)

ANACONDA_API_DETAILS_COLUMNS: tuple[str, ...] = (
    "summary",
    "home_url",
    "dev_url",
    "doc_url",
    "license",
    # "runtime_depends",
    "direct_dep_count",
    "direct_dep_names",
    # "virtual_dep_count",
    # "virtual_dep_names",
    "depends_on_python",
    "depends_on_nodejs",
    "depends_on_perl",
    "depends_on_ruby",
    "depends_on_java",
)

ANACONDA_API_METADATA_COLUMNS: tuple[str, ...] = ANACONDA_API_VERSION_COLUMNS + ANACONDA_API_DETAILS_COLUMNS

CSV_METADATA_COLUMNS: tuple[str, ...] = (
    *CSV_SOURCE_PACKAGE_COLUMNS,
    *ANACONDA_API_VERSION_COLUMNS,
    *CSV_SOURCE_ANNOTATION_COLUMNS,
    *ANACONDA_API_DETAILS_COLUMNS,
)


def parse_conda_build(build: str, regex: re.Pattern[str] = re.compile(r"py(\d)(\d+)")) -> tuple[int, int]:
    """Parse conda build string and return python version as tuple.

    This does not attempt to be robust, just quick and dirty getting the job done here.
    """
    match = regex.search(build)
    if match:
        major_version = int(match.group(1))
        minor_version = int(match.group(2))
        return major_version, minor_version
    else:
        raise ValueError(f"Cannot parse {build}")


def parse_conda_dependency_name(dependency: str, regex: re.Pattern[str] = re.compile(r"^\s*([^\s=<>!~]+)")) -> str:
    """Parse a conda match spec enough to extract the package name."""
    match = regex.search(dependency)
    if match:
        return match.group(1).split("::")[-1]
    return dependency.strip()


def format_upload_date(upload_time: str) -> str:
    """Return the date component of an Anaconda upload timestamp."""
    if not upload_time:
        return ""
    return datetime.fromisoformat(upload_time).date().isoformat()


async def get_package_info(
    username_package_pairs: list[tuple[str, str]],
    # html page is at https://anaconda.org/{owner}/{name}
    url_format: str = "https://api.anaconda.org/package/{owner}/{name}",
) -> list[dict[str, Any]]:
    """
    Fetch package information from the Anaconda API and return a list of dictionaries.

    Args:
        username_package_pairs (list[tuple[str, str]]): A list of tuples containing owner and package name.

    Returns:
        list[dict]: A list of dictionaries containing package information.
    """

    async def fetch_package_info(owner: str, name: str) -> dict[str, Any]:
        cache_dir: Path = CACHE_DIR
        file_path: Path = cache_dir / owner / f"{name}.json"

        # Try to load from cache
        if file_path.is_file():
            with file_path.open("r") as f:
                return cast(dict[str, Any], json.load(f))

        # Fetch from API and cache
        file_path.parent.mkdir(parents=True, exist_ok=True)
        async with httpx.AsyncClient(timeout=None) as client:
            try:
                response = await client.get(url_format.format(owner=owner, name=name))
                response.raise_for_status()
                data = cast(dict[str, Any], response.json())
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
    data: dict[str, Any]
    version: str = ""
    channel: str = ""
    ignored: bool = False
    dep_of: str = ""
    notes: str = ""

    @property
    def name(self) -> str:
        return cast(str, self.data["name"])

    @property
    def owner(self) -> str:
        return cast(str, self.data["owner"]["login"])

    @property
    def summary(self) -> str:
        summary = cast(str, self.data["summary"])
        return summary.strip().replace("\n", " ")

    @property
    def home_url(self) -> str:
        return (self.data.get("home") or "").strip()

    @property
    def dev_url(self) -> str:
        return (self.data.get("dev_url") or "").strip()

    @cached_property
    def latest_uploaded_file(self) -> dict[str, Any]:
        files = [file for file in cast(list[dict[str, Any]], self.data.get("files", [])) if file.get("upload_time")]
        return max(files, key=lambda file: file["upload_time"]) if files else {}

    @cached_property
    def latest_version(self) -> str:
        return cast(str, self.latest_uploaded_file.get("version") or self.data["latest_version"])

    @property
    def license(self) -> str:
        return (self.data.get("license") or "").strip()

    @cached_property
    def platforms(self) -> dict[str, str]:
        platforms = {
            cast(str, file["attrs"]["subdir"]): cast(str, file["version"]) for file in self.latest_version_files
        }
        return platforms or cast(dict[str, str], self.data["platforms"])

    @cached_property
    def platform_set(self) -> set[tuple[str, str]]:
        return set(self.platforms.items())

    @cached_property
    def latest_version_files(self) -> list[dict[str, Any]]:
        files = cast(list[dict[str, Any]], self.data["files"])
        return [file for file in files if file["version"] == self.latest_version]

    @property
    def doc_url(self) -> str:
        return cast(str, self.data["doc_url"])

    @cached_property
    def latest_files(self) -> list[dict[str, Any]]:
        files = cast(list[dict[str, Any]], self.data["files"])
        platforms = self.platform_set
        res = [file for file in files if (file["attrs"]["subdir"], file["version"]) in platforms]
        return res

    @cached_property
    def latest_build_number(self) -> int:
        res = 0
        for file in self.latest_files:
            if (n := file["attrs"]["build_number"]) > res:
                res = n
        return res

    @cached_property
    def latest_files_with_latest_build_number(self) -> list[dict[str, Any]]:
        return [file for file in self.latest_files if file["attrs"]["build_number"] == self.latest_build_number]

    @property
    def latest_upload_time(self) -> str:
        upload_time = self.latest_uploaded_file.get("upload_time")
        if upload_time:
            return format_upload_date(upload_time)
        upload_times = [
            file["upload_time"] for file in self.latest_files_with_latest_build_number if file.get("upload_time")
        ]
        return format_upload_date(max(upload_times, default=""))

    @cached_property
    def direct_dep_specs(self) -> tuple[str, ...]:
        specs = {dep for file in self.latest_files_with_latest_build_number for dep in file["attrs"].get("depends", [])}
        return tuple(sorted(specs))

    @cached_property
    def direct_dep_name_set(self) -> set[str]:
        return {parse_conda_dependency_name(dep) for dep in self.direct_dep_specs}

    @cached_property
    def installable_direct_dep_names(self) -> tuple[str, ...]:
        return tuple(sorted(name for name in self.direct_dep_name_set if not name.startswith("__")))

    @cached_property
    def virtual_direct_dep_names(self) -> tuple[str, ...]:
        return tuple(sorted(name for name in self.direct_dep_name_set if name.startswith("__")))

    @property
    def runtime_depends(self) -> str:
        return "/".join(self.direct_dep_specs)

    @property
    def direct_dep_names(self) -> str:
        return "/".join(self.installable_direct_dep_names)

    @property
    def direct_dep_count(self) -> int:
        return len(self.installable_direct_dep_names)

    @property
    def virtual_dep_names(self) -> str:
        return "/".join(self.virtual_direct_dep_names)

    @property
    def virtual_dep_count(self) -> int:
        return len(self.virtual_direct_dep_names)

    @cached_property
    def depends_on_python(self) -> bool:
        return "python" in self.direct_dep_name_set or "python_abi" in self.direct_dep_name_set

    @property
    def depends_on_nodejs(self) -> bool:
        return "nodejs" in self.direct_dep_name_set

    @property
    def depends_on_perl(self) -> bool:
        return "perl" in self.direct_dep_name_set

    @property
    def depends_on_ruby(self) -> bool:
        return "ruby" in self.direct_dep_name_set

    @property
    def depends_on_java(self) -> bool:
        return bool({"java-jdk", "java-jre", "jdk", "openjdk"} & self.direct_dep_name_set)

    def support(self, platform: str, python_version: tuple[int, int]) -> bool:
        for file in reversed(self.data["files"]):
            platform_cur = file["attrs"]["subdir"]
            if platform_cur == "noarch":
                return True
            # matching platform
            if platform == platform_cur:
                depends_on_python = False
                for dep in file["attrs"].get("depends", []):
                    if dep.startswith("python "):
                        depends_on_python = True
                        break
                if not depends_on_python:
                    return True
                # matching python version
                if python_version == parse_conda_build(file["attrs"]["build"]):
                    return True
        return False

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "owner": self.owner,
            "summary": self.summary,
            "latest_version": self.latest_version,
            "latest_upload_time": self.latest_upload_time,
            "platforms": self.platforms,
            "home_url": self.home_url,
            "dev_url": self.dev_url,
            "doc_url": self.doc_url,
            "license": self.license,
            "runtime_depends": self.runtime_depends,
            "direct_dep_count": self.direct_dep_count,
            "direct_dep_names": self.direct_dep_names,
            "virtual_dep_count": self.virtual_dep_count,
            "virtual_dep_names": self.virtual_dep_names,
            "depends_on_python": self.depends_on_python,
            "depends_on_nodejs": self.depends_on_nodejs,
            "depends_on_perl": self.depends_on_perl,
            "depends_on_ruby": self.depends_on_ruby,
            "depends_on_java": self.depends_on_java,
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

    def __post_init__(self) -> None:
        self.df.sort_index(inplace=True)

    @classmethod
    def read_csv(
        cls,
        path: Path,
        default_channel: str = "conda-forge",
    ) -> CondaPackages:
        df = pd.read_csv(
            path,
            index_col=0,
            dtype={
                "version": str,
                "channel": str,
                "ignored": bool,
                "depended": str,
                "notes": str,
            },
            na_filter=False,
        )
        df = cast(pd.DataFrame, df.loc[:, list(CSV_SOURCE_COLUMNS)])
        return cls(df, default_channel=default_channel)

    @cached_property
    def username_package_pairs(self) -> list[tuple[str, str]]:
        return [(cast(str, row["channel"]) or self.default_channel, str(name)) for name, row in self.df.iterrows()]

    @cached_property
    def data(self) -> list[dict[str, Any]]:
        return asyncio.run(get_package_info(self.username_package_pairs))

    @cached_property
    def packages(self) -> list[CondaPackage]:
        res = []
        for d, (_, row) in zip(self.data, self.df.iterrows()):
            p = CondaPackage(d)
            p.version = row.version
            p.channel = row.channel
            p.ignored = row.ignored
            p.dep_of = row.depended
            p.notes = row.notes
            res.append(p)
        return res

    @cached_property
    def platforms(self) -> pd.DataFrame:
        """Get all platforms from the packages."""
        platforms = cast(
            pd.DataFrame,
            pd.get_dummies(pd.Series((package.platforms.keys() for package in self.packages)).explode())
            .groupby(level=0)
            .max(),
        )
        platforms.index = self.df.index
        return platforms

    def expand_from_data(self) -> None:
        df = self.df
        platforms = self.platforms
        df = pd.concat([df, platforms], axis=1)

        for col in ANACONDA_API_METADATA_COLUMNS:
            df[col] = [getattr(p, col) for p in self.packages]

        columns = list(CSV_METADATA_COLUMNS) + sorted(str(column) for column in platforms.columns.tolist())
        df = cast(pd.DataFrame, df.loc[:, columns])
        self.df = df

    def to_csv(self, path: Path) -> None:
        self.df.to_csv(path)

    def supports_platform(self, package_name: str, platform: str) -> bool:
        if platform in self.df.columns and bool(self.df.at[package_name, platform]):
            return True
        if "noarch" in self.df.columns and bool(self.df.at[package_name, "noarch"]):
            return True
        return False


def _pixi_dependency(package: CondaPackage) -> Any:
    """Value for one pixi.toml dependency entry.

    Versions are never pinned here — the lockfile is what pins. A non-default
    channel is declared per package (``{ version = "*", channel = "bioconda" }``);
    pixi additionally requires that channel to appear in the workspace channel
    list (it refuses "unavailable" channels), so the caller appends the extra
    channels there — after the default, so they never shadow conda-forge.
    """
    if package.channel:
        dep = tomlkit.inline_table()
        dep["version"] = "*"
        dep["channel"] = package.channel
        return dep
    return "*"


def _write_pixi_manifest(
    manifest: Path,
    *,
    workspace_name: str,
    channels: list[str],
    archs: list[str],
    envs: dict[str, tuple[dict[str, Any], dict[str, dict[str, Any]]]],
) -> None:
    """Write a pixi.toml declaring one feature + named environment per env.

    *envs* maps environment name to ``(common_deps, per_arch_deps)``:
    *common_deps* for packages available on every arch, *per_arch_deps* for
    packages only available on a subset (emitted under
    ``[feature.<env>.target.<arch>]``).
    """
    doc = tomlkit.document()
    doc.add(tomlkit.comment("Generated by bsos.conda.web_api — do not edit by hand."))
    doc["workspace"] = {"name": workspace_name, "channels": channels, "platforms": archs}
    features = tomlkit.table(True)
    for env_name, (common, per_arch) in envs.items():
        feature = tomlkit.table(True)
        feature["dependencies"] = common
        targets = {arch: {"dependencies": deps} for arch, deps in per_arch.items() if deps}
        if targets:
            feature["target"] = targets
        features[env_name] = feature
    doc["feature"] = features
    environments = tomlkit.table()
    for env_name in envs:
        entry = tomlkit.inline_table()
        entry["features"] = [env_name]
        entry["no-default-feature"] = True
        environments[env_name] = entry
    doc["environments"] = environments
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(tomlkit.dumps(doc), encoding="utf-8")


def _toposort_lock_packages(packages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Order each platform's packages so dependencies precede their dependents.

    micromamba installs a conda-lock file in file order (there is no solve, so
    no transaction sorting), and pixi-to-conda-lock emits alphabetical order —
    which runs post-link scripts before their libraries are linked (e.g.
    gdk-pixbuf's cache update failing to load libglib). A stable depth-first
    topological sort per platform restores the order a solver-driven install
    would use; dependency cycles in conda metadata are broken at the
    back-edge, keeping the original relative order for the cycle members.
    """
    by_platform: dict[str, list[dict[str, Any]]] = {}
    for package in packages:
        by_platform.setdefault(package["platform"], []).append(package)
    result: list[dict[str, Any]] = []
    for platform in by_platform:
        plist = by_platform[platform]
        by_name = {p["name"]: p for p in plist}
        seen: set[str] = set()

        def visit(package: dict[str, Any], by_name: dict[str, dict[str, Any]] = by_name, seen: set[str] = seen) -> None:
            if package["name"] in seen:
                return
            seen.add(package["name"])
            for dep in package.get("dependencies") or {}:
                # keys are matchspec-ish; the first token is the package name
                target = by_name.get(dep.split(" ")[0])
                if target is not None:
                    visit(target)
            result.append(package)

        for package in plist:
            visit(package)
    return result


def _lock_and_convert(manifest: Path, env_names: list[str], out_dir: Path) -> None:
    """Solve the pixi manifest and emit one conda-lock file per environment.

    ``pixi lock`` writes ``pixi.lock`` next to *manifest* without creating any
    environment; ``pixi-to-conda-lock`` then converts each named environment
    to ``<out_dir>/<env>-lock.yml``, the unified multi-platform conda-lock
    format that micromamba/mamba consume directly (the ``-lock.yml`` suffix is
    how they recognize it). Package entries are topologically sorted per
    platform so install order respects dependencies.
    """
    subprocess.run(["pixi", "lock", "--manifest-path", str(manifest)], check=True)
    pixi_lock = manifest.parent / "pixi.lock"
    for env_name in env_names:
        with tempfile.TemporaryDirectory(prefix="bsos-conda-lock-") as tmp:
            subprocess.run(
                ["pixi-to-conda-lock", str(pixi_lock), "--output", tmp, "--environment", env_name],
                check=True,
            )
            produced = sorted(Path(tmp).glob("*.yml"))
            if len(produced) != 1:
                raise RuntimeError(f"Expected exactly one conda-lock file for {env_name!r}, got {produced}")
            with produced[0].open(encoding="utf-8") as f:
                lock_data = yaml.safe_load(f)
        lock_data["package"] = _toposort_lock_packages(lock_data["package"])
        with (out_dir / f"{env_name}-lock.yml").open("w", encoding="utf-8") as f:
            yaml.dump(lock_data, f, Dumper=yamlloader.ordereddict.CSafeDumper)


def generate(
    csv: Path,
    *,
    out_dir: Path = Path("conda"),
    # https://conda.io/projects/conda/en/latest/commands/env/create.html#named-arguments
    archs: list[str] = ["linux-64", "linux-aarch64", "osx-64", "osx-arm64"],
    versions: list[str] = ["3.10", "3.11", "3.12", "3.13", "3.14"],
    default_channel: str = "conda-forge",
    name_format: str = "py{version}",
    name_replace_from: str = ".",
    name_replace_to: str = "",
    python: bool = True,
    lock: bool = False,
) -> None:
    """Generate conda environment files.

    With *lock*, instead of per-arch ``<name>_<arch>.yml`` files, write a pixi
    manifest at ``<out_dir>/<csv-stem>/pixi.toml`` (one feature/environment
    per name), solve it with ``pixi lock``, and convert each environment to a
    unified multi-platform ``<out_dir>/<name>-lock.yml`` via
    ``pixi-to-conda-lock``. Both the pixi.lock and the conda-lock files are
    meant to be committed, pinning the environments in git.
    """
    packages = CondaPackages.read_csv(csv)

    # update the csv
    packages.expand_from_data()
    packages.to_csv(csv)

    if lock:
        extra_channels = sorted(
            {package.channel for package in packages.packages if package.channel and not package.ignored}
        )
        envs: dict[str, tuple[dict[str, Any], dict[str, dict[str, Any]]]] = {}
        for version in versions:
            version_parts = version.split(".")
            python_version = (int(version_parts[0]), int(version_parts[1]))
            name = name_format.format(version=version).replace(name_replace_from, name_replace_to)
            common: dict[str, Any] = {}
            per_arch: dict[str, dict[str, Any]] = {arch: {} for arch in archs}
            if python:
                # the one deliberate version pin: each env is a python-version variant
                common["python"] = f"{version}.*"
            for package in packages.packages:
                if package.ignored:
                    continue
                supported = [
                    arch
                    for arch in archs
                    if packages.supports_platform(package.name, arch) and package.support(arch, python_version)
                ]
                if not supported:
                    continue
                if len(supported) == len(archs):
                    common[package.name] = _pixi_dependency(package)
                else:
                    for arch in supported:
                        per_arch[arch][package.name] = _pixi_dependency(package)
            envs[name] = (common, per_arch)
        manifest = out_dir / csv.stem / "pixi.toml"
        _write_pixi_manifest(
            manifest,
            workspace_name=csv.stem,
            channels=[default_channel] + extra_channels,
            archs=archs,
            envs=envs,
        )
        _lock_and_convert(manifest, list(envs), out_dir)
        return

    for arch in archs:
        for version in versions:
            version_parts = version.split(".")
            python_version = (int(version_parts[0]), int(version_parts[1]))
            name = name_format.format(arch=arch, version=version).replace(name_replace_from, name_replace_to)
            dependencies: list[str] = []
            if python:
                dependencies.append(f"python={version}")
            res = {
                "name": name,
                "channels": [default_channel],
                "dependencies": dependencies,
            }
            for package in packages.packages:
                if (
                    not package.ignored
                    and packages.supports_platform(package.name, arch)
                    and package.support(arch, python_version)
                ):
                    temp: list[str] = []
                    if package.channel:
                        temp.append(f"{package.channel}::")
                    temp.append(package.name)
                    if package.version:
                        temp.append(f"={package.version}")
                    dependencies.append("".join(temp))
            with (out_dir / f"{name}_{arch}.yml").open("w", encoding="utf-8") as f:
                yaml.dump(res, f, Dumper=yamlloader.ordereddict.CSafeDumper)


def clean(
    cache_dir: Path = CACHE_DIR,
) -> None:
    """Delete the cache directory."""
    shutil.rmtree(cache_dir, ignore_errors=True)


def cli() -> None:
    defopt.run([generate, clean])


if __name__ == "__main__":
    cli()

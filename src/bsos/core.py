from __future__ import annotations

from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
from typing import ClassVar

import numpy as np
import pandas as pd
from conda.models.match_spec import MatchSpec


@dataclass
class Package:
    """Parse a single line of the txt format used in specifying packages.

    the convention is that

    - starts with ``#`` is a package to be ignored in installation
    - starts with ``#*`` is a comment
    - optionally has `::` for conda channel delimiter and channel will be ignored here
    - optionally has version pinned by `=` and will be ignored here
    """

    match_spec: MatchSpec
    ignored: bool = False
    kwargs: dict[str, str | bool] = field(default_factory=dict)
    KEYS: ClassVar[list[str]] = ["name", "version", "channel", "ignored"]

    @property
    def to_dict(self) -> dict[str, str | bool]:
        res = {key: getattr(self, key) for key in self.KEYS}
        res.update(self.kwargs)
        return res

    @classmethod
    def from_txt_line(cls, line: str) -> Package | None:
        if not line or line.startswith("#*"):
            return None
        ignored = False
        if line.startswith("#"):
            ignored = True
            line = line.lstrip("#").strip()
        match_spec = MatchSpec(line)
        return cls(match_spec, ignored)

    @property
    def name(self) -> str:
        return self.match_spec.name

    @property
    def version(self) -> str:
        return "" if (temp := self.match_spec.version) is None else temp.spec

    @property
    def channel(self) -> str:
        return m["channel"] if "channel" in (m := self.match_spec._match_components) else ""


@dataclass
class Config:
    """Parse the txt format used in specifying packages.

    the convention is that

    - starts with ``#`` is a package to be ignored in installation
    - starts with ``#*`` is a comment
    - optionally has `::` for conda channel delimiter and channel will be ignored here
    - optionally has version pinned by `=` and will be ignored here
    """

    packages: list[Package]

    @property
    def to_dict(self) -> list[dict[str, str | bool]]:
        return [p.to_dict for p in self.packages]

    @cached_property
    def dataframe(self) -> pd.DataFrame:
        df = pd.DataFrame(self.to_dict)
        df.set_index("name", inplace=True)
        return df

    @classmethod
    def from_txt(cls, path: Path) -> Config:
        with open(path, "r") as f:
            return cls([p for line in f if (p := Package.from_txt_line(line.strip())) is not None])

    @classmethod
    def from_csv(cls, path: Path) -> Config:
        df = pd.read_csv(path, index_col=0)
        df.replace(np.nan, "", inplace=True)
        return cls.from_dataframe(df)

    @classmethod
    def from_dataframe(cls, df: pd.DataFrame) -> Config:
        keys = set(Package.KEYS)

        packages = []
        for name, row in df.iterrows():
            kwargs = {"name": name}
            if row.version:
                kwargs["version"] = row.version
            if row.channel:
                kwargs["channel"] = row.channel
            match_spec = MatchSpec(**kwargs)
            ignored = row.ignored
            kwargs = {key: row[key] for key in row.index if key not in keys}
            packages.append(Package(match_spec, ignored=ignored, kwargs=kwargs))
        return cls(packages)

    @classmethod
    def from_file(cls, path: Path) -> Config:
        path = Path(path)

        ext = path.suffix
        if ext == ".txt":
            return cls.from_txt(path)
        elif ext == ".csv":
            return cls.from_csv(path)
        else:
            raise ValueError(f"Unknown extension: {ext}")

    def to_csv(self, path: Path) -> None:
        self.dataframe.to_csv(path)

    @cached_property
    def packages_including_ingored(self) -> set[str]:
        return set(p.name for p in self.packages)

    @property
    def package_spec(self) -> list[str]:
        return [str(p.match_spec) for p in self.packages]


def normalize(path: Path, out_path: Path) -> None:
    c = Config.from_file(path)
    c.to_csv(out_path)

from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from pathlib import Path

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

    @property
    def to_dict(self) -> dict[str, str | bool]:
        return {
            "name": self.name,
            "version": self.version,
            "channel": self.channel,
            "ignored": self.ignored,
        }

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
    def to_dict(self) -> list[dict[str, str]]:
        return [p.to_dict for p in self.packages]

    @cached_property
    def dataframe(self) -> pd.DataFrame:
        return pd.DataFrame(self.to_dict)

    @classmethod
    def from_file(cls, path: Path) -> Config:
        with open(path, "r") as f:
            return cls([p for line in f if (p := Package.from_txt_line(line.strip())) is not None])

    @cached_property
    def packages_including_ingored(self) -> set[str]:
        return set(p.name for p in self.packages)

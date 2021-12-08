from __future__ import annotations

from pathlib import Path
from dataclasses import dataclass
from functools import cached_property


@dataclass
class Config:
    """Parse the txt format used in specifying packages.

    the convention is that

    - starts with ``#`` is a package to be ignored in installation
    - starts with ``#*`` is a comment
    - optionally has `::` for conda channel delimiter and channel will be ignored here
    - optionally has version pinned by `=` and will be ignored here
    """
    text: list[str]

    @classmethod
    def from_file(cls, path: Path) -> Config:
        with open(path, "r") as f:
            return cls(f.readlines())

    @cached_property
    def packages_including_ingored(self) -> set[str]:
        return set(
            package
            for word in self.text
            if (package := word.lstrip("#").strip().split("::")[-1].split("=")[0])
            and not package.startswith("*")
        )

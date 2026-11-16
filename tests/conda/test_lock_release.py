"""Tests for publishing the conda locks as a release (bsos.conda.locks) — no network."""

from datetime import date
from pathlib import Path

import pytest

from bsos.conda.locks import choose_tag, download_base, lock_checksums, stage_assets, update_pointer
from bsos.installers._locks import read_pointer, sha256_file

TODAY = date(2026, 11, 16)
REPO = "owner/repo"


def _conda_dir(tmp_path: Path, **locks: str) -> Path:
    conda = tmp_path / "conda"
    conda.mkdir()
    for name, content in locks.items():
        (conda / f"{name}-lock.yml").write_text(content)
    return conda


def test_choose_tag_is_the_utc_date() -> None:
    assert choose_tag(TODAY, []) == "conda-2026.11.16"
    assert choose_tag(TODAY, ["conda-2026.11.09"]) == "conda-2026.11.16"


def test_choose_tag_suffixes_when_the_dates_tag_exists() -> None:
    assert choose_tag(TODAY, ["conda-2026.11.16"]) == "conda-2026.11.16.2"
    assert choose_tag(TODAY, ["conda-2026.11.16", "conda-2026.11.16.2"]) == "conda-2026.11.16.3"


def test_lock_checksums_cover_only_conda_lock_files(tmp_path: Path) -> None:
    conda = _conda_dir(tmp_path, system="s", py311="p")
    (conda / "system.csv").write_text("csv")
    (conda / "system").mkdir()
    (conda / "system" / "pixi.lock").write_text("pixi")
    assert set(lock_checksums(conda)) == {"py311-lock.yml", "system-lock.yml"}


def test_update_pointer_writes_a_new_release(tmp_path: Path) -> None:
    conda = _conda_dir(tmp_path, system="s", py311="p")
    assert update_pointer(conda, REPO, TODAY, ["conda-2026.11.16"]) == "conda-2026.11.16.2"
    pointer = read_pointer(conda / "locks.sha256")
    assert pointer.tag == "conda-2026.11.16.2"
    assert pointer.url == "https://github.com/owner/repo/releases/download/conda-2026.11.16.2"
    assert pointer.sha256 == {
        "py311-lock.yml": sha256_file(conda / "py311-lock.yml"),
        "system-lock.yml": sha256_file(conda / "system-lock.yml"),
    }


def test_update_pointer_leaves_unchanged_locks_alone(tmp_path: Path) -> None:
    conda = _conda_dir(tmp_path, system="s")
    update_pointer(conda, REPO, date(2026, 11, 9), [])
    before = (conda / "locks.sha256").read_bytes()
    assert update_pointer(conda, REPO, TODAY, ["conda-2026.11.09"]) is None
    assert (conda / "locks.sha256").read_bytes() == before


def test_update_pointer_changes_only_tag_url_and_checksums(tmp_path: Path) -> None:
    conda = _conda_dir(tmp_path, system="s", py311="p")
    update_pointer(conda, REPO, date(2026, 11, 9), [])
    before = (conda / "locks.sha256").read_text().splitlines()
    (conda / "system-lock.yml").write_text("s2")
    assert update_pointer(conda, REPO, TODAY, ["conda-2026.11.09"]) == "conda-2026.11.16"
    after = (conda / "locks.sha256").read_text().splitlines()
    changed = [(old, new) for old, new in zip(before, after) if old != new]
    assert len(before) == len(after)
    assert [new.split(":")[0] if new.startswith("#") else new.split("  ")[1] for _, new in changed] == [
        "# tag",
        "# url",
        "system-lock.yml",
    ]


def test_update_pointer_without_locks_fails(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        update_pointer(_conda_dir(tmp_path), REPO, TODAY, [])


def test_stage_assets_flattens_the_pixi_locks(tmp_path: Path) -> None:
    conda = _conda_dir(tmp_path, system="s", py311="p")
    for stem in ("system", "conda"):
        (conda / stem).mkdir()
        (conda / stem / "pixi.lock").write_text(stem)
        (conda / stem / "pixi.toml").write_text("toml")
    (conda / "system.csv").write_text("csv")
    out = tmp_path / "assets"
    staged = stage_assets(conda, out)
    assert sorted(path.name for path in staged) == [
        "conda-pixi.lock",
        "py311-lock.yml",
        "system-lock.yml",
        "system-pixi.lock",
    ]
    assert (out / "conda-pixi.lock").read_text() == "conda"


def test_download_base_is_a_plain_release_url() -> None:
    assert download_base(REPO, "conda-2026.11.16") == "https://github.com/owner/repo/releases/download/conda-2026.11.16"

"""Tests for aggregate installer CLI dispatch."""

import sys

import pytest

from bsos.installers import __main__ as installers_main
from bsos.installers._recipe import supports_version_override
from bsos.installers.code import RECIPE as CODE_RECIPE
from bsos.installers.codex import RECIPE as CODEX_RECIPE


def test_version_override_supported_for_tag_only_recipe() -> None:
    assert supports_version_override(CODEX_RECIPE)


def test_version_override_rejected_for_unversioned_recipe() -> None:
    assert not supports_version_override(CODE_RECIPE)


def test_aggregate_cli_accepts_tag_only_version_recipe(monkeypatch: pytest.MonkeyPatch) -> None:
    captured = {}

    def fake_dispatch(action: str, names: list[str], version_override: str | None = None) -> int:
        captured["action"] = action
        captured["names"] = names
        captured["version_override"] = version_override
        return 0

    monkeypatch.setattr(installers_main, "_dispatch", fake_dispatch)
    monkeypatch.setattr(
        sys,
        "argv",
        ["python -m bsos.installers", "install", "codex", "--version", "rust-v0.46.0"],
    )

    with pytest.raises(SystemExit) as exc:
        installers_main.main()

    assert exc.value.code == 0
    assert captured == {
        "action": "install",
        "names": ["codex"],
        "version_override": "rust-v0.46.0",
    }

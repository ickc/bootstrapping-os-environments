from pathlib import Path
from typing import Any

import yaml

import bsos.conda.web_api as web_api


def _package_data(name: str, files: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "name": name,
        "owner": {"login": "conda-forge"},
        "summary": name,
        "home": "",
        "dev_url": "",
        "doc_url": "",
        "license": "MIT",
        "latest_version": files[-1]["version"],
        "platforms": {},
        "files": files,
    }


def _dependencies(path: Path) -> list[str]:
    return yaml.safe_load(path.read_text())["dependencies"]


def _fake_lmod_setup(monkeypatch, tmp_path: Path) -> Path:
    """CSV + stubbed API data: lmod's latest version only exists on linux-64."""

    async def fake_get_package_info(username_package_pairs: list[tuple[str, str]]) -> list[dict[str, Any]]:
        assert username_package_pairs == [("conda-forge", "lmod")]
        return [
            _package_data(
                "lmod",
                [
                    {
                        "version": "1.0.0",
                        "upload_time": "2020-01-01T00:00:00.000Z",
                        "attrs": {
                            "subdir": "osx-64",
                            "build": "h123_0",
                            "build_number": 0,
                            "depends": [],
                        },
                    },
                    {
                        "version": "8.7.25",
                        "upload_time": "2023-06-01T00:00:00.000Z",
                        "attrs": {
                            "subdir": "linux-64",
                            "build": "h456_0",
                            "build_number": 0,
                            "depends": [],
                        },
                    },
                ],
            )
        ]

    csv = tmp_path / "system.csv"
    csv.write_text("name,channel,ignored,version,depended,notes\nlmod,,False,,,\n")
    monkeypatch.setattr(web_api, "get_package_info", fake_get_package_info)
    return csv


def test_generate_honors_latest_platform_columns(monkeypatch, tmp_path: Path) -> None:
    csv = _fake_lmod_setup(monkeypatch, tmp_path)

    web_api.generate(
        csv,
        out_dir=tmp_path,
        archs=["linux-64", "osx-64"],
        versions=["3.14"],
        name_format="system",
        python=False,
    )

    assert "lmod" in _dependencies(tmp_path / "system_linux-64.yml")
    assert "lmod" not in _dependencies(tmp_path / "system_osx-64.yml")


def test_generate_lock_writes_platform_targets(monkeypatch, tmp_path: Path) -> None:
    csv = _fake_lmod_setup(monkeypatch, tmp_path)
    called: dict[str, Any] = {}
    monkeypatch.setattr(
        web_api,
        "_lock_and_convert",
        lambda manifest, env_names, out_dir: called.update(manifest=manifest, env_names=env_names, out_dir=out_dir),
    )

    web_api.generate(
        csv,
        out_dir=tmp_path,
        archs=["linux-64", "osx-64"],
        versions=["3.14"],
        name_format="system",
        python=False,
        lock=True,
    )

    manifest = tmp_path / "system" / "pixi.toml"
    text = manifest.read_text()
    # lmod is linux-64-only, so it must be under a platform target, not common deps
    assert '[feature."system".target."linux-64".dependencies]\n"lmod" = "*"' in text
    assert '[feature."system".target."osx-64".dependencies]' not in text
    assert 'platforms = ["linux-64", "osx-64"]' in text
    assert '"system" = { features = ["system"], no-default-feature = true }' in text
    assert called["manifest"] == manifest
    assert called["env_names"] == ["system"]
    assert called["out_dir"] == tmp_path
    # no per-arch yml files in lock mode
    assert not (tmp_path / "system_linux-64.yml").exists()

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


def test_generate_honors_latest_platform_columns(monkeypatch, tmp_path: Path) -> None:
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

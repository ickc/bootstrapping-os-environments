"""Unit tests for the dependency audit — synthetic data only, no network."""

import json
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import pytest

from bsos.audit import conda, darwin, upstream
from bsos.audit.conda import Locked, audit_group, python_release
from bsos.audit.report import Ack, Finding, load_acks, render, triage

TODAY = date(2026, 11, 15)


def _file(name: str, version: str, uploaded: str, subdir: str = "linux-64", build: str = "h0_0") -> dict[str, Any]:
    return {
        "basename": f"{subdir}/{name}-{version}-{build}.conda",
        "version": version,
        "upload_time": f"{uploaded} 00:00:00+00:00",
        "labels": ["main"],
        "attrs": {"subdir": subdir, "build": build},
    }


def _lock(*pins: tuple[str, str, str]) -> conda.LockIndex:
    """``(name, version, subdir)`` -> a lock index pinning those builds."""
    index: conda.LockIndex = {}
    for name, version, subdir in pins:
        url = f"https://conda.anaconda.org/conda-forge/{subdir}/{name}-{version}-h0_0.conda"
        index.setdefault(name, {})[subdir] = Locked(version, url)
    return index


def _by_key(findings: list[Finding]) -> dict[str, Finding]:
    return {finding.key: finding for finding in findings}


# ── conda ─────────────────────────────────────────────────────────────────────

FRESH = _file("fresh", "2.0", "2026-11-05")


def test_python_release_follows_the_october_cadence() -> None:
    assert python_release(14) == date(2025, 10, 1)
    assert python_release(15) == date(2026, 10, 1)


def test_healthy_environment_has_no_findings() -> None:
    assert (
        audit_group(
            "system", {"fresh": [FRESH]}, {"system": _lock(("fresh", "2.0", "linux-64"))}, pythons={}, today=TODAY
        )
        == []
    )


def test_old_build_is_informational() -> None:
    """The w3m case: the pin is a build from years ago."""
    packages = {"fresh": [FRESH], "w3m": [_file("w3m", "0.5.3", "2017-08-31")]}
    locks = {"system": _lock(("fresh", "2.0", "linux-64"), ("w3m", "0.5.3", "linux-64"))}
    finding = _by_key(audit_group("system", packages, locks, pythons={}, today=TODAY))["old-build:system/w3m"]
    assert not finding.action
    assert "0.5.3 built 2017-08-31 (system)" in finding.detail


def test_held_back_ignores_what_the_solver_could_not_see() -> None:
    """Newer than the newest pinned build = still inside the cooldown, not held back."""
    poppler = [
        _file("poppler", "26.07.0", "2026-07-06"),
        _file("poppler", "26.10.0", "2026-10-09"),
        _file("poppler", "26.11.0", "2026-11-09"),  # after FRESH: the solver never saw it
        {**_file("poppler", "26.10.9", "2026-11-05"), "upload_time": "2026-11-05 20:00:00+00:00"},  # same day, later
        _file("poppler", "27.0.0rc1", "2026-10-01"),  # prerelease
        {**_file("poppler", "26.10.5", "2026-10-20"), "labels": ["broken"]},
    ]
    locks = {"system": _lock(("fresh", "2.0", "linux-64"), ("poppler", "26.07.0", "linux-64"))}
    finding = _by_key(audit_group("system", {"fresh": [FRESH], "poppler": poppler}, locks, pythons={}, today=TODAY))[
        "held-back:system/poppler"
    ]
    assert not finding.action
    assert finding.detail == "26.07.0 pinned though 26.10.0 was available (system)"


def test_held_back_names_the_platforms_when_only_some_are_affected() -> None:
    gs = [
        _file("gs", "10.04.0", "2024-09-18", "osx-arm64"),
        _file("gs", "10.08.0", "2026-09-08", "osx-arm64"),
        _file("gs", "10.08.0", "2026-09-08", "linux-64"),
    ]
    locks = {
        "system": _lock(("fresh", "2.0", "linux-64"), ("gs", "10.08.0", "linux-64"), ("gs", "10.04.0", "osx-arm64"))
    }
    finding = _by_key(audit_group("system", {"fresh": [FRESH], "gs": gs}, locks, pythons={}, today=TODAY))[
        "held-back:system/gs"
    ]
    assert "(system on osx-arm64)" in finding.detail


def test_active_package_in_no_environment_needs_a_decision() -> None:
    """The intel-openmp case: the generator dropped it without a word."""
    locks = {"py314": _lock(("fresh", "2.0", "linux-64")), "py315": _lock(("fresh", "2.0", "linux-64"))}
    packages = {"fresh": [FRESH], "intel-openmp": [_file("intel-openmp", "2026.2.0", "2026-10-22", "win-64")]}
    finding = _by_key(audit_group("conda", packages, locks, pythons={"py314": 14, "py315": 15}, today=TODAY))[
        "no-env:conda/intel-openmp"
    ]
    assert finding.action
    assert "py314, py315" in finding.detail


def test_python_gap_only_after_the_grace_period() -> None:
    """Missing from py314 (a year old) is a finding; missing from py315 (a month old) is lag."""
    locks = {
        "py313": _lock(("fresh", "2.0", "linux-64"), ("stale", "1.0", "linux-64"), ("lagging", "1.0", "linux-64")),
        "py314": _lock(("fresh", "2.0", "linux-64"), ("lagging", "1.0", "linux-64"), ("modern", "1.0", "linux-64")),
        "py315": _lock(("fresh", "2.0", "linux-64"), ("modern", "1.0", "linux-64")),
    }
    packages = {
        "fresh": [FRESH],
        "stale": [_file("stale", "1.0", "2026-01-01")],
        "lagging": [_file("lagging", "1.0", "2026-01-01")],
        "modern": [_file("modern", "1.0", "2026-01-01")],  # never built for 3.13: dropping old Pythons is fine
    }
    pythons = {"py313": 13, "py314": 14, "py315": 15}
    findings = _by_key(audit_group("conda", packages, locks, pythons=pythons, today=TODAY))
    assert findings["python-gap:conda/stale"].action
    assert "no build for Python 3.14" in findings["python-gap:conda/stale"].detail
    assert "python-gap:conda/lagging" not in findings
    assert "python-gap:conda/modern" not in findings
    # a year on, 3.15 has had its grace period too
    later = _by_key(audit_group("conda", packages, locks, pythons=pythons, today=date(2027, 11, 15)))
    assert "python-gap:conda/lagging" in later


def test_stale_lock_when_nothing_recent_is_pinned() -> None:
    """The bot stopped landing: the newest build anywhere in the lock is months old."""
    packages = {"a": [_file("a", "1.0", "2026-08-24")]}
    locks = {"system": _lock(("a", "1.0", "linux-64"))}
    finding = _by_key(audit_group("system", packages, locks, pythons={}, today=TODAY))["stale-lock:conda/system"]
    assert finding.action and "2026-08-24" in finding.detail


def test_load_lock_indexes_by_name_and_platform(tmp_path: Path) -> None:
    lock = tmp_path / "system-lock.yml"
    lock.write_text(
        "package:\n"
        "- {name: less, platform: linux-64, version: '710', url: 'https://x/linux-64/less-710-h0_0.conda'}\n"
        "- {name: less, platform: osx-arm64, version: '704', url: 'https://x/osx-arm64/less-704-h0_0.conda'}\n"
    )
    index = conda.load_lock(lock)
    assert index["less"]["linux-64"] == Locked("710", "https://x/linux-64/less-710-h0_0.conda")
    assert set(index["less"]) == {"linux-64", "osx-arm64"}


# ── upstream ──────────────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "urls, expected",
    [
        (("https://github.com/mozilla/bleach",), "mozilla/bleach"),
        (("https://github.com/pandas-dev/pandas.git",), "pandas-dev/pandas"),
        (("https://github.com/ickc/pannb/issues/",), "ickc/pannb"),
        ((None, "", "https://arrow.apache.org", "http://github.com/dfm/acor"), "dfm/acor"),
        (("https://github.com/conda-forge/w3m-feedstock", "http://w3m.sourceforge.net"), None),
        (("https://gitlab.com/owner/project",), None),
    ],
)
def test_github_repo(urls: tuple[Any, ...], expected: Any) -> None:
    assert upstream.github_repo(*urls) == expected


def test_recipe_upstreams_come_from_the_recipes() -> None:
    users = upstream.recipe_upstreams()
    assert users["junegunn/fzf"] == {"fzf (installer recipe)"}
    assert "openai/codex" in users  # two artifacts sharing one version spec: one entry
    assert not any("claude" in repo for repo in users)  # not a GitHub-release recipe


def test_archived_needs_a_decision_and_unresolved_is_informational() -> None:
    users = {
        "mozilla/bleach": {"bleach (conda.csv)"},
        "gone/project": {"x (conda.csv)"},
        "ok/project": {"y (conda.csv)"},
    }
    state = {
        "mozilla/bleach": {"nameWithOwner": "mozilla/bleach", "isArchived": True, "pushedAt": "2026-06-05T00:00:00Z"},
        "gone/project": None,
        "ok/project": {"nameWithOwner": "ok/project", "isArchived": False, "pushedAt": "2026-11-01T00:00:00Z"},
    }
    findings = _by_key(upstream.findings_for(users, state))
    assert set(findings) == {"archived:mozilla/bleach", "repo-not-found:gone/project"}
    assert findings["archived:mozilla/bleach"].action
    assert "used by bleach (conda.csv)" in findings["archived:mozilla/bleach"].detail
    assert not findings["repo-not-found:gone/project"].action


def test_query_repos_batches_and_survives_a_missing_repository(monkeypatch: pytest.MonkeyPatch) -> None:
    queries = []

    def fake_graphql(query: str) -> dict[str, Any]:
        queries.append(query)
        return {"r0": {"nameWithOwner": "a/b", "isArchived": False, "pushedAt": "2026-01-01"}, "r1": None}

    monkeypatch.setattr(upstream, "_graphql", fake_graphql)
    state = upstream.query_repos(["c/d", "a/b", "a/b"])
    assert len(queries) == 1 and 'repository(owner:"a",name:"b")' in queries[0]
    assert state == {"a/b": {"nameWithOwner": "a/b", "isArchived": False, "pushedAt": "2026-01-01"}, "c/d": None}


# ── darwin ────────────────────────────────────────────────────────────────────


def test_nix_lists_skip_commented_entries(tmp_path: Path) -> None:
    casks = tmp_path / "casks.nix"
    casks.write_text('[\n  # Web browser\n  "firefox"\n  # "kiwix"\n  "zed"\n]\n')
    assert darwin.quoted_names(casks) == ["firefox", "zed"]
    mas = tmp_path / "masApps.nix"
    mas.write_text('{\n  "Xcode" = 497799835;\n  # "Gone" = 1;\n  "Spark Desktop" = 6445813049;\n}\n')
    assert darwin.mas_apps(mas) == {"Xcode": 497799835, "Spark Desktop": 6445813049}


def test_brew_finding() -> None:
    assert darwin.brew_finding("cask", "firefox", {"deprecated": False, "disabled": False}) is None
    missing = darwin.brew_finding("cask", "gone", None)
    assert missing is not None and missing.key == "brew:cask/gone"
    deprecated = darwin.brew_finding(
        "formula",
        "old",
        {
            "deprecated": True,
            "deprecation_date": "2026-01-01",
            "deprecation_reason": "unmaintained",
            "deprecation_replacement_formula": "new",
        },
    )
    assert deprecated is not None
    assert deprecated.detail == "deprecated by Homebrew as of 2026-01-01: unmaintained; replacement: new"
    scheduled = darwin.brew_finding("cask", "soon", {"disabled": False, "disable_date": "2027-01-01"})
    assert scheduled is not None and "disabled by Homebrew as of 2027-01-01" in scheduled.detail


def test_flake_finding(tmp_path: Path) -> None:
    def write(pinned: date) -> Path:
        stamp = int(datetime(pinned.year, pinned.month, pinned.day, tzinfo=timezone.utc).timestamp())
        lock = tmp_path / "flake.lock"
        lock.write_text(
            json.dumps({"nodes": {"root": {"inputs": {"nixpkgs": "np"}}, "np": {"locked": {"lastModified": stamp}}}})
        )
        return lock

    assert darwin.flake_finding(write(date(2026, 10, 20)), TODAY) is None
    stale = darwin.flake_finding(write(date(2026, 8, 12)), TODAY)
    assert stale is not None and stale.key == "stale-lock:nix/flake.lock" and "95 days ago" in stale.detail


# ── report ────────────────────────────────────────────────────────────────────


def test_acknowledgements_hide_until_they_expire() -> None:
    findings = [
        Finding("archived", "a/b", "archived"),
        Finding("archived", "c/d", "archived"),
        Finding("old-build", "system/sd", "old", action=False),
    ]
    acks = {
        "archived:a/b": Ack("finished software", date(2027, 6, 1)),
        "archived:c/d": Ack("looked fine then", date(2026, 6, 1)),
        "archived:gone/away": Ack("fixed since", date(2027, 6, 1)),
    }
    report = triage(findings, acks, TODAY)
    assert [f.key for f, _ in report.acknowledged] == ["archived:a/b"]
    assert [f.key for f in report.action] == ["archived:c/d"]
    assert "acknowledgement expired 2026-06-01" in report.action[0].detail
    assert [f.key for f in report.info] == ["old-build:system/sd", "unused-ack:archived:gone/away"]
    # a partial run cannot tell an unused acknowledgement from an unchecked one
    assert "unused-ack:archived:gone/away" not in [f.key for f in triage(findings, acks, TODAY, complete=False).info]


def test_load_acks_requires_reason_and_expiry(tmp_path: Path) -> None:
    path = tmp_path / "audit-ack.toml"
    assert load_acks(path) == {}
    path.write_text('["archived:a/b"]\nreason = "finished"\nuntil = 2027-06-01\n')
    assert load_acks(path) == {"archived:a/b": Ack("finished", date(2027, 6, 1))}
    path.write_text('["archived:a/b"]\nreason = "finished"\n')
    with pytest.raises(ValueError, match="until"):
        load_acks(path)


def test_render_is_a_markdown_report() -> None:
    report = triage(
        [Finding("archived", "a/b", "archived | really"), Finding("old-build", "system/sd", "old", action=False)],
        {},
        TODAY,
    )
    text = render(report, TODAY)
    assert text.startswith("# Dependency audit — 2026-11-15\n")
    assert "**1 need a decision**, 1 informational, 0 acknowledged." in text
    assert "| `archived:a/b` | archived \\| really |" in text
    assert "## Acknowledged" not in text

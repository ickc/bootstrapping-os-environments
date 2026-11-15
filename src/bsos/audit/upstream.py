"""Is the upstream project still alive? — the one signal that needs no threshold.

A repository its owner archived is abandoned by declaration. This checks
every active conda package (via the repository URL in its metadata) and every
installer recipe that tracks GitHub releases.

This is the one place envoy talks to the GitHub API. The "never call
``api.github.com``" rule is about *installers*, which run unauthenticated on
end-user machines and hit the 60 req/hour limit; this runs in CI with the
workflow token, as a handful of batched GraphQL queries through ``gh``.
"""

from __future__ import annotations

import importlib
import json
import re
import shutil
import subprocess
from datetime import date
from pathlib import Path
from typing import Any, Iterable

from bsos.audit.conda import load_tables
from bsos.audit.report import Finding
from bsos.installers._compile import discover_modules
from bsos.installers._recipe import GitHubRedirect

_GITHUB = re.compile(r"github\.com[/:]([\w.-]+)/([\w.-]+?)(?:\.git)?(?:[/#?].*)?$")
_BATCH = 50


def github_repo(*urls: str | None) -> str | None:
    """``owner/name`` from the first GitHub URL among *urls* (conda-forge feedstocks are not upstream)."""
    for url in urls:
        match = _GITHUB.search((url or "").strip())
        if match and not match.group(2).endswith("-feedstock"):
            return f"{match.group(1)}/{match.group(2)}"
    return None


def conda_upstreams(conda_dir: Path) -> dict[str, set[str]]:
    """``{owner/name: {who uses it}}`` for the active packages of every CSV."""
    users: dict[str, set[str]] = {}
    for stem, table in load_tables(conda_dir).items():
        for package in table.packages:
            if package.ignored:
                continue
            data = package.data
            repo = github_repo(data.get("dev_url"), data.get("source_git_url"), data.get("home"))
            if repo:
                users.setdefault(repo.lower(), set()).add(f"{package.name} ({stem}.csv)")
    return users


def recipe_upstreams() -> dict[str, set[str]]:
    """``{owner/name: {recipe}}`` for installer recipes that resolve versions from GitHub releases."""
    users: dict[str, set[str]] = {}
    for name in discover_modules():
        recipe = getattr(importlib.import_module(f"bsos.installers.{name}"), "RECIPE", None)
        for artifact in recipe.artifacts if recipe is not None else ():
            if isinstance(artifact.version, GitHubRedirect):
                repo = f"{artifact.version.owner}/{artifact.version.repo}"
                users.setdefault(repo.lower(), set()).add(f"{name} (installer recipe)")
    return users


def _graphql(query: str) -> dict[str, Any]:
    gh = shutil.which("gh")
    if gh is None:
        raise RuntimeError("the upstream check needs the GitHub CLI (`gh`), authenticated (GH_TOKEN in CI)")
    result = subprocess.run([gh, "api", "graphql", "-f", f"query={query}"], capture_output=True, text=True)
    # A repository that no longer resolves makes gh exit non-zero while still
    # returning data for the others, so go by the payload, not the exit code.
    try:
        data = json.loads(result.stdout).get("data")
    except json.JSONDecodeError:
        data = None
    if not isinstance(data, dict):
        raise RuntimeError(f"GitHub GraphQL query failed: {(result.stderr or result.stdout).strip()[:300]}")
    return data


def query_repos(repos: Iterable[str]) -> dict[str, dict[str, Any] | None]:
    """Repository state for each ``owner/name`` (``None`` where it does not resolve)."""
    ordered = sorted(set(repos))
    state: dict[str, dict[str, Any] | None] = {}
    for start in range(0, len(ordered), _BATCH):
        batch = ordered[start : start + _BATCH]
        fields = "".join(
            f'r{i}:repository(owner:"{owner}",name:"{name}"){{nameWithOwner isArchived pushedAt}}'
            for i, (owner, name) in enumerate(repo.split("/", 1) for repo in batch)
        )
        data = _graphql(f"query{{{fields}}}")
        for i, repo in enumerate(batch):
            state[repo] = data.get(f"r{i}")
    return state


def findings_for(users: dict[str, set[str]], state: dict[str, dict[str, Any] | None]) -> list[Finding]:
    findings = []
    for repo, who in users.items():
        used_by = f"used by {', '.join(sorted(who))}"
        info = state.get(repo)
        if info is None:
            findings.append(
                Finding("repo-not-found", repo, f"the GitHub URL in the metadata no longer resolves; {used_by}", False)
            )
        elif info["isArchived"]:
            findings.append(
                Finding(
                    "archived",
                    info["nameWithOwner"],
                    f"archived on GitHub (last push {info['pushedAt'][:10]}); {used_by}",
                )
            )
    return findings


def audit(conda_dir: Path, today: date) -> list[Finding]:
    users = conda_upstreams(conda_dir)
    for repo, who in recipe_upstreams().items():
        users.setdefault(repo, set()).update(who)
    return findings_for(users, query_repos(users))

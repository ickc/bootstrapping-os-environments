"""Declarative installer engine.

Every installer module reduces to a :class:`Recipe` — a data description of
*where* to download an asset, *how* to unpack and place it, how to *verify* the
install, and how to *uninstall* it.  This module interprets that data, so the
five stages every installer shares (locate → unpack/place → cleanup → test →
uninstall) are implemented exactly once here.

A tool module is then just data plus one line::

    from bsos.installers._recipe import github_binary, run_cli

    RECIPE = github_binary(name="foobar", repo="acme/foobar", asset="foobar-{target}.tar.gz",
                           targets={"Linux-x86_64": "x86_64-unknown-linux-musl"}, member="foobar")

    if __name__ == "__main__":
        run_cli(RECIPE)

stdlib only; targets Python 3.10+.  Compiles cleanly into a self-contained
``curl | python3`` script via :mod:`bsos.installers._compile` (the engine is
inlined and tree-shaken down to what each recipe actually reaches).
"""

import argparse
import shutil
import stat
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Union

from bsos.installers._download import (
    download_file,
    download_to_tempdir,
    resolve_latest_github_tag,
)
from bsos.installers._env import EnvConfig, platform_key
from bsos.installers._subprocess import run


# ─────────────────────────────────────────────────────────────────────────────
# Stage 1 — version: how to fill ``{version}`` in a download URL.
# ─────────────────────────────────────────────────────────────────────────────
class VersionSpec:
    """Strategy for resolving the ``{version}`` token of a download URL."""

    def resolve(self) -> str:
        raise NotImplementedError


@dataclass
class Latest(VersionSpec):
    """No version lookup — the URL uses the ``/releases/latest/download/`` redirect."""

    def resolve(self) -> str:
        return "latest"


@dataclass
class Pinned(VersionSpec):
    """A fixed version string baked into the recipe."""

    value: str

    def resolve(self) -> str:
        return self.value


@dataclass
class GitHubRedirect(VersionSpec):
    """Resolve the latest release tag via the ``/releases/latest`` redirect.

    Never calls the GitHub API (rate-limited at 60 req/hour unauthenticated).
    Set *strip_v* to drop a leading ``v`` from the tag (some asset names embed
    the bare version while the tag path keeps the ``v``).
    """

    owner: str
    repo: str
    strip_v: bool = False

    def resolve(self) -> str:
        tag = resolve_latest_github_tag(self.owner, self.repo)
        return tag.lstrip("v") if self.strip_v else tag


# ─────────────────────────────────────────────────────────────────────────────
# Stage 2 — archive kind and destination.
# ─────────────────────────────────────────────────────────────────────────────
@dataclass(frozen=True)
class Archive:
    """An archive format: its filename extension and its extractor kind.

    Frozen (immutable, hashable) so the ``RAW`` constant is usable as the
    ``Artifact.archive`` field default — these are shared value constants.
    """

    ext: str
    kind: Optional[str]  # "tar" | "zip" | None (raw, not an archive)


TAR = Archive("tar.gz", "tar")
ZIP = Archive("zip", "zip")
RAW = Archive("", None)


@dataclass
class Dest:
    """A destination: an :class:`EnvConfig` directory attribute plus a relative path."""

    area: str  # an EnvConfig attribute name, e.g. "bin_dir", "pixi_home"
    rel: str = ""

    def path(self, env: EnvConfig) -> Path:
        base: Path = getattr(env, self.area)
        return base / self.rel if self.rel else base

    @classmethod
    def bin(cls, name: str) -> "Dest":
        """Shorthand for ``$__OPT_ROOT/bin/<name>``."""
        return cls("bin_dir", name)


@dataclass
class RunScript:
    """Install by *running* the downloaded file (e.g. an official ``.sh`` installer).

    *fresh_args* / *update_args* are argv templates (each element may reference
    ``{script}`` and ``{dest}``); *update_marker* is a path under *dest* whose
    presence selects *update_args* over *fresh_args*.
    """

    fresh_args: List[str]
    update_args: List[str]
    update_marker: str


@dataclass
class Artifact:
    """One download that results in one placed file (or one run script).

    ``url_template`` may reference ``{target}`` (the per-platform token),
    ``{version}`` and ``{ext}`` (the resolved archive extension).  ``member``
    is the path of the wanted file *inside* the extracted archive (templated
    the same way); ``None`` means the download itself is the file.
    """

    url_template: str
    dest: Dest
    targets: Optional[Dict[str, str]] = None  # platform_key -> token; None = platform-independent
    version: VersionSpec = field(default_factory=Latest)
    archive: Union[Archive, Dict[str, Archive]] = RAW  # scalar, or per-platform mapping
    member: Optional[str] = None
    executable: bool = True
    action: Optional["RunScript"] = None  # forward ref keeps RunScript out of place-only scripts


# ─────────────────────────────────────────────────────────────────────────────
# Stages 4 & 5 — verify and uninstall.
# ─────────────────────────────────────────────────────────────────────────────
@dataclass
class Verify:
    """How ``test`` validates an install.

    *args* is the argv passed to the installed binary (``None`` ⇒ existence
    check only).  When *contains* is set, success means the substring appears
    in stdout/stderr (the return code is ignored — for tools with idiosyncratic
    exit codes).  *path* overrides which file is probed (default: the first
    artifact's destination).
    """

    args: Optional[List[str]] = field(default_factory=lambda: ["--version"])
    contains: Optional[str] = None
    path: Optional[Dest] = None


@dataclass
class Remove:
    """How ``uninstall`` removes an install.

    Default (``tree=None``) unlinks every artifact's destination.  Set *tree*
    to ``rmtree`` a directory the install created instead (e.g. a conda prefix).
    """

    tree: Optional[Dest] = None


@dataclass
class Recipe:
    name: str
    artifacts: List[Artifact]
    verify: Verify = field(default_factory=Verify)
    remove: Remove = field(default_factory=Remove)


# ─────────────────────────────────────────────────────────────────────────────
# Engine — the five stages, implemented once.
# ─────────────────────────────────────────────────────────────────────────────
def _target_for(art: Artifact, key: str) -> Optional[str]:
    """Resolve the per-platform token, exiting 1 on an unsupported platform."""
    if art.targets is None:
        return None
    token = art.targets.get(key)
    if token is None:
        print(f"Unsupported platform: {key}", file=sys.stderr)
        sys.exit(1)
    return token


def _archive_for(art: Artifact, key: str) -> Archive:
    """Resolve the archive format, which may vary per platform."""
    archive = art.archive
    if isinstance(archive, dict):
        selected = archive.get(key)
        if selected is None:
            print(f"Unsupported platform: {key}", file=sys.stderr)
            sys.exit(1)
        return selected
    return archive


def _run_script(action: RunScript, url: str, dest: Path, env: EnvConfig) -> None:
    tmp = Path(tempfile.mkdtemp(prefix="bsos-"))
    try:
        script = tmp / "installer.sh"
        download_file(url, script)
        script.chmod(script.stat().st_mode | stat.S_IEXEC)
        marker = dest / action.update_marker
        argv_template = action.update_args if marker.exists() else action.fresh_args
        argv = [arg.format(script=str(script), dest=str(dest)) for arg in argv_template]
        print(f"{'Updating' if marker.exists() else 'Installing'} → {dest} ...")
        run(argv, env=env.subprocess_env())
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _install_artifact(art: Artifact, env: EnvConfig) -> Path:
    key = platform_key()
    target = _target_for(art, key)
    archive = _archive_for(art, key)
    version = art.version.resolve()
    token = target if target is not None else ""
    url = art.url_template.format(target=token, version=version, ext=archive.ext)
    dest = art.dest.path(env)

    if art.action is not None:
        _run_script(art.action, url, dest, env)
        return dest

    if archive.kind is None:
        download_file(url, dest)
    else:
        tmp = download_to_tempdir(url, extract=archive.kind)
        try:
            member = (art.member or "").format(target=token, version=version, ext=archive.ext)
            src = tmp / member
            if not src.exists():
                print(f"Expected payload {member!r} not found in archive", file=sys.stderr)
                sys.exit(1)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dest))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    if art.executable:
        dest.chmod(0o755)
    return dest


def install(recipe: Recipe, env: Optional[EnvConfig] = None) -> None:
    env = env or EnvConfig()
    for art in recipe.artifacts:
        dest = _install_artifact(art, env)
        print(f"Installed {recipe.name} → {dest}")


def uninstall(recipe: Recipe, env: Optional[EnvConfig] = None) -> None:
    env = env or EnvConfig()
    if recipe.remove.tree is not None:
        target = recipe.remove.tree.path(env)
        if target.exists():
            shutil.rmtree(target)
            print(f"Removed {target}")
        else:
            print(f"{target} not found", file=sys.stderr)
        return
    for art in recipe.artifacts:
        target = art.dest.path(env)
        if target.exists():
            target.unlink()
            print(f"Removed {target}")
        else:
            print(f"{target} not found", file=sys.stderr)


def _supported_platforms(recipe: Recipe) -> Optional[Set[str]]:
    """Union of platform keys across platform-specific artifacts.

    ``None`` means the recipe is platform-independent (never skipped by ``test``).
    """
    keys: Set[str] = set()
    specific = False
    for art in recipe.artifacts:
        if art.targets is not None:
            specific = True
            keys.update(art.targets)
    return keys if specific else None


def test_install(recipe: Recipe, env: Optional[EnvConfig] = None) -> int:
    """Validate an install on the current platform.

    Skips cleanly (exit 0) on an unsupported platform; fails (exit 1) when the
    expected file is missing on a supported platform.
    """
    env = env or EnvConfig()
    key = platform_key()
    supported = _supported_platforms(recipe)
    if supported is not None and key not in supported:
        print(f"Platform {key} unsupported by {recipe.name} installer; skipping", file=sys.stderr)
        return 0

    verify = recipe.verify
    probe_dest = verify.path if verify.path is not None else recipe.artifacts[0].dest
    probe = probe_dest.path(env)
    if not probe.exists():
        print(f"{probe} not found; run install first", file=sys.stderr)
        return 1

    if verify.args is None:
        print(f"{probe} found")
        return 0

    if verify.contains is not None:
        result = run(
            [str(probe), *verify.args],
            env=env.subprocess_env(),
            check=False,
            capture_output=True,
            text=True,
        )
        output = f"{result.stdout or ''}{result.stderr or ''}".strip()
        if verify.contains.lower() in output.lower():
            print(output)
            return 0
        print(
            f"{recipe.name} {' '.join(verify.args)} did not identify itself (rc={result.returncode}): {output!r}",
            file=sys.stderr,
        )
        return 1

    result = run([str(probe), *verify.args], env=env.subprocess_env(), check=False)
    return int(result.returncode)


def run_cli(recipe: Recipe) -> None:
    """Standard ``install`` / ``uninstall`` / ``test`` command-line dispatch."""
    parser = argparse.ArgumentParser(description=f"{recipe.name} installer")
    parser.add_argument(
        "action",
        choices=["install", "uninstall", "test"],
        help=f"install/uninstall {recipe.name}, or test validates an install "
        "(skips cleanly if the platform is unsupported)",
    )
    args = parser.parse_args()
    env = EnvConfig()
    if args.action == "install":
        install(recipe, env)
    elif args.action == "uninstall":
        uninstall(recipe, env)
    else:
        sys.exit(test_install(recipe, env))


# ─────────────────────────────────────────────────────────────────────────────
# Convenience constructor for the common case: one binary from a GitHub release.
# ─────────────────────────────────────────────────────────────────────────────
def _infer_archive(asset: str) -> Archive:
    if asset.endswith((".tar.gz", ".tgz", ".tar")):
        return TAR
    if asset.endswith(".zip"):
        return ZIP
    return RAW


def github_binary(
    name: str,
    repo: str,
    targets: Dict[str, str],
    asset: str,
    member: Optional[str] = None,
    version: Optional[VersionSpec] = None,
    dest: Optional[Dest] = None,
    executable: bool = True,
    verify: Optional[Verify] = None,
) -> Recipe:
    """Build a single-binary GitHub-release recipe.

    *repo* is ``owner/name``.  *asset* is the release asset filename (may
    contain ``{target}``); the archive format is inferred from its extension.
    *member* is the path of the binary inside the archive (omit for a raw,
    un-archived asset).  *version* defaults to :class:`GitHubRedirect` (resolve
    the latest tag without the API); pass :class:`Latest` to use the
    ``/releases/latest/download/`` redirect, or :class:`Pinned` for a fixed tag.
    """
    if version is None:
        owner, _, repo_name = repo.partition("/")
        version = GitHubRedirect(owner, repo_name)
    archive = _infer_archive(asset)
    if isinstance(version, Latest):
        url_template = f"https://github.com/{repo}/releases/latest/download/{asset}"
    else:
        url_template = f"https://github.com/{repo}/releases/download/{{version}}/{asset}"
    artifact = Artifact(
        url_template=url_template,
        dest=dest if dest is not None else Dest.bin(name),
        targets=targets,
        version=version,
        archive=archive,
        member=member,
        executable=executable,
    )
    return Recipe(name=name, artifacts=[artifact], verify=verify if verify is not None else Verify())

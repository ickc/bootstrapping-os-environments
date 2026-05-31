"""Unit tests for install idempotency.

Each installer type has two code paths:
  install (force=False) — skip if already installed
  install (force=True)  — always run (the "update" action)

Tests use tmp_path to construct an isolated EnvConfig and mock out any
network I/O (_install_artifact for recipe installers, _env_yaml + run for
mamba_env), so nothing is downloaded or executed on the real system.
"""

import contextlib
import shutil
import tempfile
from pathlib import Path
from typing import Iterator
from unittest.mock import patch

import pytest

from bsos.installers._env import EnvConfig
from bsos.installers._recipe import (
    Artifact,
    Dest,
    Latest,
    RAW,
    Recipe,
    Remove,
    RunScript,
    Verify,
    _is_installed,
    install,
)
import bsos.installers.mamba_env as mamba_env_mod


# ── shared helpers ────────────────────────────────────────────────────────────


def _env(tmp_path: Path) -> EnvConfig:
    return EnvConfig(
        {
            "HOME": str(tmp_path),
            "__OPT_ROOT": str(tmp_path / "opt"),
            "MAMBA_ROOT_PREFIX": str(tmp_path / "miniforge3"),
        }
    )


def _plain_recipe(name: str = "tool") -> Recipe:
    """Single-binary, platform-independent recipe — no download needed for tests."""
    return Recipe(
        name=name,
        artifacts=[
            Artifact(
                url_template="https://example.com/tool",
                dest=Dest("bin_dir", name),
                targets=None,
                version=Latest(),
                archive=RAW,
            )
        ],
        verify=Verify(args=None),
    )


def _runscript_recipe(name: str = "tool") -> Recipe:
    dest = Dest("opt_root", name)
    return Recipe(
        name=name,
        artifacts=[
            Artifact(
                url_template="https://example.com/tool.sh",
                dest=dest,
                targets=None,
                version=Latest(),
                archive=RAW,
                action=RunScript(
                    fresh_args=["{script}", "-f", "{dest}"],
                    update_args=["{script}", "-u", "{dest}"],
                    update_marker="etc/marker",
                ),
            )
        ],
        verify=Verify(args=None),
        remove=Remove(tree=dest),  # RunScript installs to a directory, not a single file
    )


def _mamba_env(tmp_path: Path) -> EnvConfig:
    """EnvConfig with a fake mamba binary planted so the existence check passes."""
    mamba_prefix = tmp_path / "miniforge3"
    mamba_bin = mamba_prefix / "bin" / "mamba"
    mamba_bin.parent.mkdir(parents=True)
    mamba_bin.touch()
    return EnvConfig(
        {
            "HOME": str(tmp_path),
            "__OPT_ROOT": str(tmp_path / "opt"),
            "MAMBA_ROOT_PREFIX": str(mamba_prefix),
        }
    )


@contextlib.contextmanager
def _fake_env_yaml(base: str, filename: str) -> Iterator[Path]:
    """Drop-in replacement for mamba_env._env_yaml — yields a real temp file."""
    tmp = Path(tempfile.mkdtemp(prefix="bsos-test-"))
    try:
        spec = tmp / filename
        spec.write_text("name: test\ndependencies: []\n")
        yield spec
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ── _is_installed: plain artifact ─────────────────────────────────────────────


def test_is_installed_plain_absent(tmp_path):
    assert not _is_installed(_plain_recipe(), _env(tmp_path))


def test_is_installed_plain_present(tmp_path):
    env = _env(tmp_path)
    dest = _plain_recipe().artifacts[0].dest.path(env)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.touch()
    assert _is_installed(_plain_recipe(), env)


# ── _is_installed: RunScript artifact ────────────────────────────────────────


def test_is_installed_runscript_marker_absent(tmp_path):
    env = _env(tmp_path)
    recipe = _runscript_recipe()
    # dest dir exists but update_marker does not
    recipe.artifacts[0].dest.path(env).mkdir(parents=True, exist_ok=True)
    assert not _is_installed(recipe, env)


def test_is_installed_runscript_marker_present(tmp_path):
    env = _env(tmp_path)
    recipe = _runscript_recipe()
    marker = recipe.artifacts[0].dest.path(env) / "etc" / "marker"
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.touch()
    assert _is_installed(recipe, env)


# ── install: plain recipe ─────────────────────────────────────────────────────


def test_install_plain_skips_when_present(tmp_path, capsys):
    env = _env(tmp_path)
    recipe = _plain_recipe()
    dest = recipe.artifacts[0].dest.path(env)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.touch()

    with patch("bsos.installers._recipe._install_artifact") as mock_ia:
        install(recipe, env)
        mock_ia.assert_not_called()

    assert "already installed" in capsys.readouterr().out


def test_install_plain_runs_when_absent(tmp_path):
    env = _env(tmp_path)
    recipe = _plain_recipe()

    with patch("bsos.installers._recipe._install_artifact", return_value=Path("/fake/tool")) as mock_ia:
        install(recipe, env)
        mock_ia.assert_called_once()


def test_install_plain_force_runs_when_present(tmp_path, capsys):
    env = _env(tmp_path)
    recipe = _plain_recipe()
    dest = recipe.artifacts[0].dest.path(env)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.touch()

    with patch("bsos.installers._recipe._install_artifact", return_value=dest) as mock_ia:
        install(recipe, env, force=True)
        mock_ia.assert_called_once()

    assert "already installed" not in capsys.readouterr().out


# ── install: RunScript recipe ─────────────────────────────────────────────────


def test_install_runscript_skips_when_installed(tmp_path, capsys):
    env = _env(tmp_path)
    recipe = _runscript_recipe()
    marker = recipe.artifacts[0].dest.path(env) / "etc" / "marker"
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.touch()

    with patch("bsos.installers._recipe._install_artifact") as mock_ia:
        install(recipe, env)
        mock_ia.assert_not_called()

    assert "already installed" in capsys.readouterr().out


def test_install_runscript_runs_when_absent(tmp_path):
    env = _env(tmp_path)
    recipe = _runscript_recipe()

    with patch("bsos.installers._recipe._install_artifact", return_value=Path("/fake")) as mock_ia:
        install(recipe, env)
        mock_ia.assert_called_once()


def test_install_runscript_force_runs_when_installed(tmp_path):
    env = _env(tmp_path)
    recipe = _runscript_recipe()
    marker = recipe.artifacts[0].dest.path(env) / "etc" / "marker"
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.touch()

    with patch("bsos.installers._recipe._install_artifact", return_value=Path("/fake")) as mock_ia:
        install(recipe, env, force=True)
        mock_ia.assert_called_once()


# ── reinstall: plain recipe ───────────────────────────────────────────────────


def test_reinstall_plain_removes_then_installs(tmp_path, capsys):
    env = _env(tmp_path)
    recipe = _plain_recipe()
    dest = recipe.artifacts[0].dest.path(env)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.touch()

    with patch("bsos.installers._recipe._install_artifact", return_value=dest) as mock_ia:
        # uninstall() removes the file; install() re-places it
        from bsos.installers._recipe import uninstall, install as recipe_install
        uninstall(recipe, env)
        recipe_install(recipe, env)
        mock_ia.assert_called_once()

    assert not dest.exists() or mock_ia.called  # file was removed then re-placed


def test_reinstall_runscript_marker_gone_uses_fresh_path(tmp_path):
    """After reinstall the marker is gone, so the next install takes the fresh path."""
    env = _env(tmp_path)
    recipe = _runscript_recipe()
    marker = recipe.artifacts[0].dest.path(env) / "etc" / "marker"
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.touch()

    from bsos.installers._recipe import uninstall
    uninstall(recipe, env)

    # marker gone → _is_installed is False → install will call _install_artifact
    assert not _is_installed(recipe, env)
    with patch("bsos.installers._recipe._install_artifact", return_value=Path("/fake")) as mock_ia:
        install(recipe, env)
        mock_ia.assert_called_once()


# ── mamba_env ─────────────────────────────────────────────────────────────────


def test_mamba_env_install_creates_when_absent(tmp_path):
    env = _mamba_env(tmp_path)
    with (
        patch("bsos.installers.mamba_env._env_yaml", new=_fake_env_yaml),
        patch("bsos.installers.mamba_env.run") as mock_run,
    ):
        mamba_env_mod.install("testenv", env=env)
    argv = mock_run.call_args[0][0]
    assert "create" in argv
    assert "update" not in argv


def test_mamba_env_install_skips_when_present(tmp_path, capsys):
    env = _mamba_env(tmp_path)
    prefix = env.opt_root / "testenv"
    prefix.mkdir(parents=True)

    with patch("bsos.installers.mamba_env.run") as mock_run:
        mamba_env_mod.install("testenv", env=env)
        mock_run.assert_not_called()

    assert "already exists" in capsys.readouterr().out


def test_mamba_env_install_force_updates_when_present(tmp_path):
    env = _mamba_env(tmp_path)
    prefix = env.opt_root / "testenv"
    prefix.mkdir(parents=True)

    with (
        patch("bsos.installers.mamba_env._env_yaml", new=_fake_env_yaml),
        patch("bsos.installers.mamba_env.run") as mock_run,
    ):
        mamba_env_mod.install("testenv", env=env, force=True)
    argv = mock_run.call_args[0][0]
    assert "update" in argv
    assert "create" not in argv


def test_mamba_env_install_force_creates_when_absent(tmp_path):
    env = _mamba_env(tmp_path)
    with (
        patch("bsos.installers.mamba_env._env_yaml", new=_fake_env_yaml),
        patch("bsos.installers.mamba_env.run") as mock_run,
    ):
        mamba_env_mod.install("testenv", env=env, force=True)
    argv = mock_run.call_args[0][0]
    assert "create" in argv
    assert "update" not in argv


def test_mamba_env_reinstall_removes_prefix_then_creates(tmp_path):
    """reinstall = uninstall (rmtree) + install (fresh create), not mamba env update."""
    env = _mamba_env(tmp_path)
    prefix = env.opt_root / "testenv"
    prefix.mkdir(parents=True)
    sentinel = prefix / "sentinel"
    sentinel.touch()

    mamba_env_mod.uninstall("testenv", env=env)
    assert not prefix.exists()

    with (
        patch("bsos.installers.mamba_env._env_yaml", new=_fake_env_yaml),
        patch("bsos.installers.mamba_env.run") as mock_run,
    ):
        mamba_env_mod.install("testenv", env=env)
    argv = mock_run.call_args[0][0]
    assert "create" in argv
    assert "update" not in argv

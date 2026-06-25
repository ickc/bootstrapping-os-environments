"""Tests for bsos.installers._env.

The headline tests pin the checked-in ``env.sh`` and ``env.fish`` to what
``_env.py`` generates: ``_env.py`` is the source of truth, and shell files are
derived artifacts.  If they drift, regenerate with the matching pixi task.
"""

from pathlib import Path

from bsos.installers._env import EnvConfig, generate_env_fish, generate_env_sh, platform_key

REPO_ROOT = Path(__file__).resolve().parents[2]
ENV_SH = REPO_ROOT / "env.sh"
ENV_FISH = REPO_ROOT / "env.fish"


def test_env_sh_matches_generated():
    assert ENV_SH.read_text() == generate_env_sh(), "env.sh is stale; regenerate with `pixi run generate-env-sh`"


def test_env_fish_matches_generated():
    assert ENV_FISH.read_text() == generate_env_fish(), (
        "env.fish is stale; regenerate with `pixi run generate-env-fish`"
    )


def test_defaults_from_home():
    env = EnvConfig({"HOME": "/home/alice"})
    d = env.as_dict()
    assert d["__LOCAL_ROOT"] == "/home/alice/.local"
    assert d["__OPT_ROOT"] == f"/home/alice/.local/opt/{platform_key()}"
    assert d["MAMBA_ROOT_PREFIX"] == f"/home/alice/.local/opt/{platform_key()}/micromamba"
    assert d["__LMOD_INIT"] == f"/home/alice/.local/opt/{platform_key()}/system/lmod/lmod/init"
    assert d["XDG_DATA_HOME"] == "/home/alice/.local/share"


def test_appdir_redirects_local_root():
    env = EnvConfig({"HOME": "/home/bob", "__APPDIR": "/cosma/apps/bob"})
    d = env.as_dict()
    assert d["__LOCAL_ROOT"] == "/cosma/apps/bob/local"
    assert d["__OPT_ROOT"] == f"/cosma/apps/bob/local/opt/{platform_key()}"


def test_preexisting_values_respected():
    env = EnvConfig(
        {
            "HOME": "/home/carol",
            "__OPT_ROOT": "/custom/opt",
            "MAMBA_ROOT_PREFIX": "/custom/mamba",
            "__LMOD_INIT": "/custom/lmod/init",
        }
    )
    d = env.as_dict()
    assert d["__OPT_ROOT"] == "/custom/opt"
    assert d["MAMBA_ROOT_PREFIX"] == "/custom/mamba"
    assert d["__LMOD_INIT"] == "/custom/lmod/init"


def test_empty_value_treated_as_unset():
    # Mirrors shell ${VAR:-default}: an empty string falls back to default.
    env = EnvConfig({"HOME": "/home/dave", "__OPT_ROOT": "", "__LMOD_INIT": ""})
    assert env.as_dict()["__OPT_ROOT"] == f"/home/dave/.local/opt/{platform_key()}"
    assert env.as_dict()["__LMOD_INIT"] == f"/home/dave/.local/opt/{platform_key()}/system/lmod/lmod/init"


def test_subprocess_env_includes_managed_vars():
    env = EnvConfig({"HOME": "/home/erin"})
    sp = env.subprocess_env()
    # all managed vars present
    for key, value in env.as_dict().items():
        assert sp[key] == value
    # values are plain strings (suitable as subprocess env)
    assert all(isinstance(v, str) for v in sp.values())


def test_subprocess_env_inherits_network_and_github_auth_vars(monkeypatch):
    inherited = {
        "HTTPS_PROXY": "http://proxy.example:8080",
        "http_proxy": "http://lower-proxy.example:8080",
        "NO_PROXY": "localhost,127.0.0.1",
        "GITHUB_TOKEN": "ghs_example",
        "GH_TOKEN": "ghp_example",
    }
    for key, value in inherited.items():
        monkeypatch.setenv(key, value)

    sp = EnvConfig({"HOME": "/home/frank"}).subprocess_env()

    for key, value in inherited.items():
        assert sp[key] == value

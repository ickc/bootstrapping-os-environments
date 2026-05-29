"""Tests for the installer compile system."""

import ast
from pathlib import Path

import pytest

from bsos.installers._compile import compile_module, resolve_dependencies

REPO_ROOT = Path(__file__).resolve().parents[2]

_COMPILED_MODULES = ["code", "pixi", "mamba", "mamba_env", "sman", "zim"]

# mamba_env uses only _env/_subprocess (no _download), so __version__ is not
# imported and therefore not baked into the compiled output.
_MODULES_WITH_VERSION = [m for m in _COMPILED_MODULES if m != "mamba_env"]


def test_code_dependencies_are_topologically_ordered():
    order = resolve_dependencies("code")
    # a module's intra-package deps must appear before it
    assert order.index("_env") < order.index("code")
    assert order.index("_download") < order.index("code")
    assert order[-1] == "code"


@pytest.mark.parametrize("module", _COMPILED_MODULES)
def test_compiled_is_valid_and_self_contained(module):
    text = compile_module(module)
    tree = ast.parse(text)  # must be syntactically valid
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            assert node.level == 0, f"{module}: relative import leaked into compiled output"
            assert not (node.module or "").startswith("bsos"), (
                f"{module}: bsos import leaked: {node.module}"
            )
        elif isinstance(node, ast.Import):
            assert not any(a.name.startswith("bsos") for a in node.names)


@pytest.mark.parametrize("module", _MODULES_WITH_VERSION)
def test_compiled_bakes_version(module):
    from bsos import __version__

    text = compile_module(module)
    assert f"__version__ = {__version__!r}" in text


@pytest.mark.parametrize("module", _COMPILED_MODULES)
def test_checked_in_script_is_up_to_date(module):
    output = module.replace("_", "-") + ".py"  # mamba_env → mamba-env.py? no, keep underscore
    # compiled output uses the module name directly: mamba_env.py not mamba-env.py
    artifact_path = REPO_ROOT / "install" / f"{module}.py"
    artifact = artifact_path.read_text()
    assert artifact == compile_module(module), (
        f"install/{module}.py is stale; regenerate with "
        f"`pixi run compile-{module.replace('_', '-')}`"
    )

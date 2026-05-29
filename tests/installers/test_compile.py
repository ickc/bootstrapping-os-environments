"""Tests for the installer compile system."""

import ast
from pathlib import Path

from bsos.installers._compile import compile_module, resolve_dependencies

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_code_dependencies_are_topologically_ordered():
    order = resolve_dependencies("code")
    # a module's intra-package deps must appear before it
    assert order.index("_env") < order.index("code")
    assert order.index("_download") < order.index("code")
    assert order[-1] == "code"


def test_compiled_code_is_valid_and_self_contained():
    text = compile_module("code")
    tree = ast.parse(text)  # must be syntactically valid
    # no bsos imports (intra-package or top-level) should survive
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            assert node.level == 0, "relative import leaked into compiled output"
            assert not (node.module or "").startswith("bsos"), (
                f"bsos import leaked: {node.module}"
            )
        elif isinstance(node, ast.Import):
            assert not any(a.name.startswith("bsos") for a in node.names)


def test_compiled_code_bakes_version():
    from bsos import __version__

    text = compile_module("code")
    assert f"__version__ = {__version__!r}" in text


def test_checked_in_code_py_is_up_to_date():
    artifact = (REPO_ROOT / "install" / "code.py").read_text()
    assert artifact == compile_module("code"), (
        "install/code.py is stale; regenerate with `pixi run compile-code`"
    )

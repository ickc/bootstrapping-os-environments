"""Compile installer modules into self-contained single-file scripts.

Mirrors the bash compile.sh approach: resolves intra-package imports,
topologically sorts dependencies, merges/canonicalizes stdlib imports,
and emits a single .py file suitable for ``curl | python3``.

Usage::

    python -m bsos.installers._compile code -o install/code.py
"""

import argparse
import ast
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

_PACKAGE = "bsos.installers"
_PACKAGE_DIR = Path(__file__).resolve().parent


def _module_path(name: str) -> Path:
    return _PACKAGE_DIR / f"{name}.py"


def _read_source(name: str) -> str:
    path = _module_path(name)
    if not path.is_file():
        raise FileNotFoundError(f"Module not found: {path}")
    return path.read_text()


def _is_intra_package(node: ast.ImportFrom) -> bool:
    if node.level and node.level > 0:
        return True
    if node.module and node.module.startswith(f"{_PACKAGE}."):
        return True
    return False


def _extract_intra_deps(node: ast.ImportFrom) -> List[str]:
    if node.level and node.level > 0:
        if node.module:
            return [node.module]
        return [alias.name for alias in node.names]
    if node.module and node.module.startswith(f"{_PACKAGE}."):
        return [node.module[len(f"{_PACKAGE}."):]]
    return []


def _find_deps(source: str) -> Set[str]:
    deps = set()  # type: Set[str]
    for node in ast.parse(source).body:
        if isinstance(node, ast.ImportFrom) and _is_intra_package(node):
            deps.update(_extract_intra_deps(node))
    return deps


def resolve_dependencies(target: str) -> List[str]:
    """Return all intra-package dependencies in topological order."""
    visited = set()  # type: Set[str]
    order = []  # type: List[str]

    def visit(name: str) -> None:
        if name in visited:
            return
        visited.add(name)
        for dep in sorted(_find_deps(_read_source(name))):
            visit(dep)
        order.append(name)

    visit(target)
    return order


def _segment(lines: List[str], node: ast.stmt) -> str:
    """Return the full source text of *node* (handles multi-line statements)."""
    end = node.end_lineno or node.lineno
    return "\n".join(lines[node.lineno - 1 : end])


def _classify(source: str) -> Tuple[List[str], List[str], List[str], List[str], List[str]]:
    """Split *source* into (future, stdlib, baked, code, main_block).

    *future* and *stdlib* are full import statements; intra-package
    imports are dropped; ``from bsos import …`` statements go to *baked*
    (resolved to literals at compile time); the ``if __name__`` block is
    separated so it can be emitted once, at the very end.
    """
    tree = ast.parse(source)
    lines = source.splitlines()

    consumed = set()  # type: Set[int]
    future = []  # type: List[str]
    stdlib = []  # type: List[str]
    baked = []  # type: List[str]
    main_start = None  # type: Optional[int]

    # Drop each module's leading docstring — the compiled file carries the
    # target module's docstring at the top instead.
    if (
        tree.body
        and isinstance(tree.body[0], ast.Expr)
        and isinstance(tree.body[0].value, ast.Constant)
        and isinstance(tree.body[0].value.value, str)
    ):
        doc = tree.body[0]
        consumed.update(range(doc.lineno, (doc.end_lineno or doc.lineno) + 1))

    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            consumed.update(range(node.lineno, (node.end_lineno or node.lineno) + 1))
            if isinstance(node, ast.ImportFrom) and node.module == "__future__":
                future.append(_segment(lines, node))
            elif isinstance(node, ast.ImportFrom) and _is_intra_package(node):
                pass  # dropped — inlined below
            elif isinstance(node, ast.ImportFrom) and node.module == "bsos":
                baked.append(_segment(lines, node))  # resolved to literals
            else:
                stdlib.append(_segment(lines, node))
        elif (
            isinstance(node, ast.If)
            and isinstance(node.test, ast.Compare)
            and isinstance(node.test.left, ast.Name)
            and node.test.left.id == "__name__"
        ):
            main_start = node.lineno

    if main_start is not None:
        main_block = lines[main_start - 1 :]
        consumed.update(range(main_start, len(lines) + 1))
    else:
        main_block = []

    code = [lines[i] for i in range(len(lines)) if (i + 1) not in consumed]
    return future, stdlib, baked, code, main_block


def _render_imports(segments: List[str]) -> List[str]:
    """Merge import statements: one ``import`` line per name, one
    ``from M import …`` line per module, names sorted and de-duplicated."""
    plain = set()  # type: Set[str]
    froms = {}  # type: Dict[str, Dict[str, Optional[str]]]
    for seg in segments:
        node = ast.parse(seg).body[0]
        if isinstance(node, ast.Import):
            for alias in node.names:
                plain.add(f"import {alias.name} as {alias.asname}" if alias.asname else f"import {alias.name}")
        elif isinstance(node, ast.ImportFrom):
            names = froms.setdefault(node.module or "", {})
            for alias in node.names:
                names[alias.name] = alias.asname

    out = sorted(plain)
    for module in sorted(froms):
        names = froms[module]
        rendered = [f"{n} as {names[n]}" if names[n] else n for n in sorted(names)]
        out.append(f"from {module} import {', '.join(rendered)}")
    return out


def _bake_imports(segments: List[str]) -> List[str]:
    """Resolve ``from bsos import NAME`` statements to literal assignments.

    Imports the real ``bsos`` package at compile time and bakes each
    referenced attribute as ``alias = <repr>`` so the standalone script
    needs no ``bsos`` package.  Only simple constants are supported.
    """
    import bsos  # the real package — available during compilation

    resolved = {}  # type: Dict[str, str]
    for seg in segments:
        node = ast.parse(seg).body[0]
        assert isinstance(node, ast.ImportFrom)
        for alias in node.names:
            value = getattr(bsos, alias.name)
            if not isinstance(value, (str, int, float, bool, type(None))):
                raise TypeError(
                    f"cannot bake non-constant `bsos.{alias.name}` ({type(value).__name__})"
                )
            resolved[alias.asname or alias.name] = repr(value)
    return [f"{name} = {literal}" for name, literal in sorted(resolved.items())]


def compile_module(target: str) -> str:
    """Compile *target* into a self-contained script."""
    all_future = []  # type: List[str]
    all_stdlib = []  # type: List[str]
    all_baked = []  # type: List[str]
    all_code = []  # type: List[str]
    target_main = []  # type: List[str]

    for mod in resolve_dependencies(target):
        future, stdlib, baked, code, main_block = _classify(_read_source(mod))
        all_future.extend(future)
        all_stdlib.extend(stdlib)
        all_baked.extend(baked)
        all_code.append(f"\n# --- {mod} ---\n")
        all_code.extend(code)
        if mod == target and main_block:
            target_main = main_block

    target_doc = ast.get_docstring(ast.parse(_read_source(target)))
    output = [
        "#!/usr/bin/env python3",
        "# Auto-generated by bsos compile system from "
        f"{_PACKAGE}.{target} — do not edit.",
    ]
    if target_doc:
        output.append('"""{}"""'.format(target_doc))
    # __future__ imports must precede all other statements
    future_block = _render_imports(all_future) if all_future else []
    if future_block:
        output.append("")
        output.extend(future_block)
    stdlib_block = _render_imports(all_stdlib)
    if stdlib_block:
        output.append("")
        output.extend(stdlib_block)
    baked_block = _bake_imports(all_baked) if all_baked else []
    if baked_block:
        output.append("")
        output.append("# Baked from the bsos package at compile time.")
        output.extend(baked_block)
    output.extend(all_code)
    if target_main:
        output.append("")
        output.extend(target_main)

    text = "\n".join(output) + "\n"
    while "\n\n\n\n" in text:  # collapse 3+ blank lines to 2
        text = text.replace("\n\n\n\n", "\n\n\n")
    return text


def main() -> None:
    parser = argparse.ArgumentParser(description="Compile a bsos installer module.")
    parser.add_argument("target", help="Module name (e.g. 'code')")
    parser.add_argument("-o", "--output", help="Output file path (default: stdout)")
    args = parser.parse_args()

    text = compile_module(args.target)

    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text)
        out.chmod(0o755)
        print(f"Compiled {args.target} → {out}", file=sys.stderr)
    else:
        print(text, end="")


if __name__ == "__main__":
    main()

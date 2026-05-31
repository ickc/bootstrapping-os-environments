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
_INSTALL_DIR = _PACKAGE_DIR.parents[2] / "install"


def discover_modules() -> List[str]:
    """Return all installer module names (non-private, non-dunder) sorted by name."""
    return sorted(p.stem for p in _PACKAGE_DIR.glob("*.py") if not p.stem.startswith("_"))


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
        return [node.module[len(f"{_PACKAGE}.") :]]
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


def _get_top_level_defs(source: str) -> Dict[str, ast.stmt]:
    """Map name → AST node for each top-level definition (funcs, classes, assigns)."""
    defs: Dict[str, ast.stmt] = {}
    for node in ast.parse(source).body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            defs[node.name] = node
        elif isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name):
                    defs[t.id] = node
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            defs[node.target.id] = node
    return defs


def _walk_skip_annotations(node: ast.AST):
    """Walk an AST node's descendants, skipping type annotation subtrees.

    Type annotations (argument annotations, return annotations, variable
    annotations) are pure hints — they create no runtime dependency on the
    names they mention, so the tree-shaker must not follow them.

    This holds only because the compiled output emits ``from __future__ import
    annotations`` (see :func:`compile_module`), which stringizes every
    annotation; without it, dropping an annotation-only name (e.g.
    ``_download.PathLike``) would crash at def-time.
    """
    from collections import deque

    todo: deque[ast.AST] = deque([node])
    while todo:
        cur = todo.popleft()
        yield cur
        for field, value in ast.iter_fields(cur):
            if field == "annotation":
                continue
            if field == "returns" and isinstance(cur, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if isinstance(value, list):
                todo.extend(v for v in value if isinstance(v, ast.AST))
            elif isinstance(value, ast.AST):
                todo.append(value)


def _transitive_needed(seed: Set[str], defs: Dict[str, ast.stmt]) -> Set[str]:
    """Return all names in *defs* reachable from *seed* via Name references."""
    all_names = set(defs)
    needed = set(seed) & all_names
    queue = list(needed)
    while queue:
        name = queue.pop()
        for child in _walk_skip_annotations(defs[name]):
            if isinstance(child, ast.Name) and child.id in all_names and child.id not in needed:
                needed.add(child.id)
                queue.append(child.id)
    return needed


def _collect_dep_imports(source: str) -> Dict[str, Set[str]]:
    """Return ``{dep_module: {imported_names}}`` for all intra-package imports."""
    result: Dict[str, Set[str]] = {}
    for node in ast.parse(source).body:
        if not isinstance(node, ast.ImportFrom) or not _is_intra_package(node):
            continue
        names = {alias.name for alias in node.names}
        for dep in _extract_intra_deps(node):
            result.setdefault(dep, set()).update(names)
    return result


def _segment(lines: List[str], node: ast.stmt) -> str:
    """Return the full source text of *node* (handles multi-line statements)."""
    end = node.end_lineno or node.lineno
    return "\n".join(lines[node.lineno - 1 : end])


def _classify(
    source: str, needed: Optional[Set[str]] = None
) -> Tuple[List[str], List[str], List[str], List[str], List[str]]:
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

    if needed is not None:
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                if node.name not in needed:
                    # node.lineno is the def/class keyword; any decorators sit
                    # above it and must be consumed too, or a tree-shaken
                    # @decorator (e.g. @dataclass) leaks as an orphan line.
                    start = node.lineno
                    for dec in node.decorator_list:
                        start = min(start, dec.lineno)
                    consumed.update(range(start, (node.end_lineno or node.lineno) + 1))
            elif isinstance(node, ast.Assign):
                target_names = [t.id for t in node.targets if isinstance(t, ast.Name)]
                if target_names and not any(n in needed for n in target_names):
                    consumed.update(range(node.lineno, (node.end_lineno or node.lineno) + 1))
            elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                if node.target.id not in needed:
                    consumed.update(range(node.lineno, (node.end_lineno or node.lineno) + 1))

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
                raise TypeError(f"cannot bake non-constant `bsos.{alias.name}` ({type(value).__name__})")
            resolved[alias.asname or alias.name] = repr(value)
    return [f"{name} = {literal}" for name, literal in sorted(resolved.items())]


def compile_module(target: str) -> str:
    """Compile *target* into a self-contained script."""
    order = resolve_dependencies(target)

    # For each module, record which names it imports from each intra-package dep.
    dep_imports: Dict[str, Dict[str, Set[str]]] = {mod: _collect_dep_imports(_read_source(mod)) for mod in order}

    # Backward pass: compute the set of top-level names needed from each dep module.
    # The target module is always included in full (needed = None).
    # Dep modules include only names reachable from what their importers explicitly use.
    needed_names: Dict[str, Optional[Set[str]]] = {}
    needed_from: Dict[str, Set[str]] = {}  # accumulated seeds for each dep

    for mod in reversed(order):
        if mod == target:
            needed_names[mod] = None  # include everything
        else:
            seed = needed_from.get(mod, set())
            defs = _get_top_level_defs(_read_source(mod))
            needed_names[mod] = _transitive_needed(seed, defs)
        # Propagate: whatever this module imports from its own deps is needed there.
        for dep, names in dep_imports[mod].items():
            needed_from.setdefault(dep, set()).update(names)

    # Always stringize annotations in compiled output. The tree-shaker drops
    # annotation-only names (e.g. _download.PathLike) but leaves the annotations
    # that mention them in the emitted signatures; PEP 563 makes those a no-op at
    # runtime instead of a def-time NameError. Merges/dedupes with any module's
    # own __future__ imports via _render_imports.
    all_future = ["from __future__ import annotations"]  # type: List[str]
    all_stdlib = []  # type: List[str]
    all_baked = []  # type: List[str]
    all_code = []  # type: List[str]
    target_main = []  # type: List[str]

    for mod in order:
        future, stdlib, baked, code, main_block = _classify(_read_source(mod), needed_names[mod])
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
        f"# Auto-generated by bsos compile system from {_PACKAGE}.{target} — do not edit.",
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
    parser = argparse.ArgumentParser(description="Compile bsos installer module(s).")
    parser.add_argument("target", nargs="?", help="Module name (e.g. 'code'); omit to compile all")
    parser.add_argument("-o", "--output", help="Output file (single-module mode only; default: stdout)")
    args = parser.parse_args()

    if args.target:
        text = compile_module(args.target)
        if args.output:
            out = Path(args.output)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(text)
            out.chmod(0o755)
            print(f"Compiled {args.target} → {out}", file=sys.stderr)
        else:
            print(text, end="")
    else:
        _INSTALL_DIR.mkdir(parents=True, exist_ok=True)
        for name in discover_modules():
            text = compile_module(name)
            out = _INSTALL_DIR / f"{name}.py"
            out.write_text(text)
            out.chmod(0o755)
            print(f"Compiled {name} → {out}", file=sys.stderr)


if __name__ == "__main__":
    main()

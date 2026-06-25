"""Stdlib-only installer toolkit (VS Code CLI, mamba, pixi, …).

Each installer module exposes ``install`` / ``uninstall`` (and a ``test``)
entry point and can be compiled into a self-contained ``curl | python3``
script via :mod:`bsos.installers._compile`.
"""

"""Dispatch install/uninstall/test actions across installer modules.

Usage::

    python -m bsos.installers install [name ...]
    python -m bsos.installers uninstall [name ...]
    python -m bsos.installers test [name ...]

With no names, all discovered installer modules are targeted (sorted by name).
A module is discovered if its filename does not start with ``_``.

Per-module dispatch protocol:

* If the module exposes a ``RECIPE`` attribute, the standard
  :mod:`bsos.installers._recipe` engine functions are called directly.
* Otherwise the module's own ``install(env=…)`` / ``uninstall(env=…)`` /
  ``test_install(env=…)`` callables are used (e.g. ``mamba_env``).
"""

import argparse
import importlib
import sys

from bsos.installers._compile import discover_modules
from bsos.installers._env import EnvConfig
from bsos.installers._recipe import Recipe
from bsos.installers._recipe import install as _recipe_install
from bsos.installers._recipe import test_install as _recipe_test
from bsos.installers._recipe import uninstall as _recipe_uninstall


def _dispatch(action: str, names: list[str], version_override: str | None = None) -> int:
    env = EnvConfig()
    rc = 0
    for name in names:
        mod = importlib.import_module(f"bsos.installers.{name}")
        if hasattr(mod, "RECIPE"):
            recipe: Recipe = mod.RECIPE
            if action == "install":
                _recipe_install(recipe, env, version_override)
            elif action == "uninstall":
                _recipe_uninstall(recipe, env)
            else:
                rc |= _recipe_test(recipe, env)
        else:
            if action == "install":
                mod.install(env=env)
            elif action == "uninstall":
                mod.uninstall(env=env)
            else:
                result = mod.test_install(env=env)
                if result is not None:
                    rc |= result
    return rc


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("action", choices=["install", "uninstall", "test"])
    parser.add_argument("names", nargs="*", metavar="name", help="Installer module names (default: all, sorted by name)")
    parser.add_argument(
        "--version",
        dest="version_override",
        metavar="TAG",
        default=None,
        help="git release tag to install (e.g. v1.2.3); requires exactly one name",
    )
    args = parser.parse_args()

    if args.version_override is not None and len(args.names) != 1:
        parser.error("--version requires exactly one installer name")

    names = args.names if args.names else discover_modules()

    if args.version_override is not None:
        name = names[0]
        mod = importlib.import_module(f"bsos.installers.{name}")
        if not hasattr(mod, "RECIPE"):
            print(f"{name}: --version is not supported (no RECIPE)", file=sys.stderr)
            sys.exit(1)
        recipe: Recipe = mod.RECIPE
        has_slot = any("{version}" in a.url_template for a in recipe.artifacts)
        if not has_slot:
            print(f"{name}: --version is not supported (no {{version}} slot in URL)", file=sys.stderr)
            sys.exit(1)

    sys.exit(_dispatch(args.action, names, args.version_override))


if __name__ == "__main__":
    main()

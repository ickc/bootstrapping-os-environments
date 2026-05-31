"""Helpers to annotate a nix `brews.nix` list with Homebrew formula descriptions.

This module exposes a single function:

    def add_description(path: Path) -> None

It reads a file containing a bracketed list of double-quoted Homebrew formula
names (e.g. the nix `brews.nix` shown by the user), queries `brew info
<name> --json=v2` for each entry, extracts the description from the JSON
(`formulae[0]["desc"]`) and rewrites the file so that each entry in the list
is represented by two lines:

  - a comment line with two leading spaces and `# DESCRIPTION`
  - a line with two leading spaces and the double-quoted package name

Only the standard library is used; `brew` is invoked via `subprocess`. If `brew`
is not available or fails for an entry, an empty comment is written for that
package's description.

Example input (simplified):
[
  "ansible"
  "mpv"
]

Example output:
[
  # Automate deployment, configuration, and upgrading
  "ansible"
  # A free, open-source, document viewer
  "mpv"
]
"""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, cast

import defopt


def _parse_brew_names(lines: List[str]) -> List[str]:
    """Return a list of package names (without quotes) parsed from the provided lines.

    This function is tolerant of being given:
      - the full file lines (including the `[` and `]` bracket lines), or
      - only the inner block lines (the lines between the brackets).

    It simply extracts any line that is a single double-quoted token like:
      "ansible"

    and returns the token without quotes.
    """
    name_re = re.compile(r'^\s*"([^"]+)"\s*$')
    names: List[str] = []

    for ln in lines:
        m = name_re.match(ln)
        if m:
            names.append(m.group(1))
    return names


def _call_brew_info(name: str, cask: bool = False) -> Optional[Dict[str, Any]]:
    """Run `brew info <name> --json=v2` and return parsed JSON or None on failure."""
    command = ["brew", "info", name, "--json=v2"]
    if cask:
        command.insert(2, "--cask")
    try:
        proc = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        # brew not available on PATH
        return None

    if proc.returncode != 0:
        return None

    try:
        return cast(Dict[str, Any], json.loads(proc.stdout))
    except json.JSONDecodeError:
        return None


def _extract_description(brew_json: Optional[Dict[str, Any]], cask: bool = False) -> Optional[str]:
    """Extract `formulae[0]['desc']` from brew JSON if present."""
    key = "casks" if cask else "formulae"
    if not brew_json:
        return None
    try:
        package = brew_json.get(key)
        if not isinstance(package, list) or not package:
            return None
        desc = package[0].get("desc")
        if isinstance(desc, str):
            return desc.strip()
    except Exception:
        return None
    return None


def _format_block(name: str, description: Optional[str]) -> List[str]:
    """Return the two-line block for a package.

    Each returned string includes its trailing newline.
    """
    desc_text = description or ""
    # Ensure description does not contain newline characters that would break layout.
    desc_text = desc_text.splitlines()[0] if desc_text else ""
    return [f"  # {desc_text}\n", f'  "{name}"\n'] if desc_text else [f'  "{name}"\n']


def add_description(path: Path, *, cask: bool = False, sort: bool = False) -> None:
    """Read a nix brews list at `path`, annotate each formula with brew descs, and write it back.

    Args:
        path: Path to a nix file
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    # Read with keepends so we preserve original newline semantics for prefix/suffix.
    raw = path.read_text(encoding="utf-8")
    lines = raw.splitlines(keepends=True)

    # Locate first line that's exactly '[' and last line that's exactly ']' (after strip).
    open_idx: Optional[int] = None
    close_idx: Optional[int] = None

    for i, ln in enumerate(lines):
        if open_idx is None and ln.strip() == "[":
            open_idx = i
            # continue scanning to find closing bracket
    if open_idx is None:
        raise ValueError("Opening bracket '[' not found on its own line")

    for i in range(len(lines) - 1, -1, -1):
        if lines[i].strip() == "]":
            close_idx = i
            break
    if close_idx is None or close_idx <= open_idx:
        raise ValueError("Closing bracket ']' not found on its own line after '['")

    prefix = lines[: open_idx + 1]  # include the '[' line
    suffix = lines[close_idx:]  # include the ']' line and beyond

    # Parse package names from the original content between the brackets.
    inner_original = lines[open_idx + 1 : close_idx]
    names = _parse_brew_names(inner_original)
    if sort:
        names.sort()

    # Build the new inner block
    new_inner: List[str] = []
    for name in names:
        info = _call_brew_info(name, cask=cask)
        desc = _extract_description(info, cask=cask)
        new_inner.extend(_format_block(name, desc))

    # Ensure there's a newline before the closing bracket if the prefix did not
    # provide one at the end of its last line. We join and write as-is.
    new_contents = "".join(prefix + new_inner + suffix)
    path.write_text(new_contents, encoding="utf-8")


if __name__ == "__main__":
    defopt.run([add_description])

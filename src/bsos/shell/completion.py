"""Shell completion generator.

Generates shell completions for installed tools, writing them to the
XDG-compliant locations:

- ``$XDG_DATA_HOME/bash-completion/completions/_<tool>``
- ``$XDG_DATA_HOME/zsh/functions/_<tool>``

Tools that are not installed are silently skipped.  This module is run as
a pixi task (``pixi run generate-completions``) — it is *not* compiled into
a standalone script because it requires the target tools to already be present.
"""

import argparse
import shutil
import subprocess
import sys
from typing import List, Optional, Tuple

from bsos.installers._env import EnvConfig

# Each entry: (tool_name, bash_command, zsh_command)
# None means "no completion for this shell".
_TOOLS: List[Tuple[str, Optional[List[str]], Optional[List[str]]]] = [
    ("bat", ["bat", "--completion", "bash"], ["bat", "--completion", "zsh"]),
    ("gh", ["gh", "completion", "-s", "bash"], ["gh", "completion", "-s", "zsh"]),
    ("pandoc", ["pandoc", "--bash-completion"], None),
    ("pixi", ["pixi", "completion", "--shell", "bash"], ["pixi", "completion", "--shell", "zsh"]),
    ("starship", ["starship", "completions", "bash"], ["starship", "completions", "zsh"]),
    (
        "zellij",
        ["zellij", "setup", "--generate-completion", "bash"],
        ["zellij", "setup", "--generate-completion", "zsh"],
    ),
]


def generate(env: Optional[EnvConfig] = None) -> None:
    env = env or EnvConfig()
    bash_dir = env.xdg_data_home / "bash-completion" / "completions"
    zsh_dir = env.xdg_data_home / "zsh" / "functions"
    bash_dir.mkdir(parents=True, exist_ok=True)
    zsh_dir.mkdir(parents=True, exist_ok=True)

    for tool, bash_cmd, zsh_cmd in _TOOLS:
        if shutil.which(tool) is None:
            print(f"  skipping {tool} (not found on PATH)")
            continue
        for shell, cmd, out_dir in [("bash", bash_cmd, bash_dir), ("zsh", zsh_cmd, zsh_dir)]:
            if cmd is None:
                continue
            out = out_dir / f"_{tool}"
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                out.write_text(result.stdout)
                print(f"  {tool}: {shell} → {out}")
            except subprocess.CalledProcessError as exc:
                print(f"  {tool}: {shell} completion failed: {exc}", file=sys.stderr)

    print(f"\nCompletions written to:\n  {bash_dir}\n  {zsh_dir}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["generate"])
    args = parser.parse_args()
    if args.action == "generate":
        generate()


if __name__ == "__main__":
    main()

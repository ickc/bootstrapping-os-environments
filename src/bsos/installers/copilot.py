"""GitHub Copilot CLI (``copilot``) installer.

The quickstart docs only advertise ``npm install -g @github/copilot`` (plus
Homebrew/WinGet casks), but ``github/copilot-cli`` releases also publish
self-contained single-binary tarballs — one ``copilot`` executable per
platform, a Node single-executable-application with no external runtime
dependency.  That's what we install here, matching the ``codex`` / ``agy``
download-and-place flow.

The release tag is resolved by following the ``/releases/latest`` redirect
(no GitHub API call).  Tags are standard ``v``-prefixed (e.g. ``v1.0.83``),
so ``github_binary``'s defaults apply.

Linux musl tarballs (``copilot-linuxmusl-*``) exist but, as elsewhere in
envoy, only the glibc build is targeted.

Usage::

    python -m bsos.installers.copilot install
    python -m bsos.installers.copilot uninstall
    python -m bsos.installers.copilot test
"""

from bsos.installers._recipe import github_binary, run_cli

RECIPE = github_binary(
    name="copilot",
    repo="github/copilot-cli",
    asset="copilot-{target}.tar.gz",
    member="copilot",
    targets={
        "Linux-x86_64": "linux-x64",
        "Linux-aarch64": "linux-arm64",
        "Darwin-x86_64": "darwin-x64",
        "Darwin-arm64": "darwin-arm64",
    },
)

if __name__ == "__main__":
    run_cli(RECIPE)

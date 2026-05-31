"""GitHub CLI (gh) installer.

Downloads the latest gh binary from GitHub releases without calling the GitHub
API (rate-limited at 60 req/hour unauthenticated); the version is resolved by
following the /releases/latest redirect.

Usage::

    python -m bsos.installers.gh install
    python -m bsos.installers.gh uninstall
    python -m bsos.installers.gh test
"""

from bsos.installers._recipe import TAR, ZIP, Artifact, Dest, GitHubRedirect, Recipe, run_cli

# {tag} puts the full git tag (e.g. v2.70.0) in the URL path.
# {version} (strip_v=True) gives the bare version (2.70.0) for asset name and member.
RECIPE = Recipe(
    name="gh",
    artifacts=[
        Artifact(
            url_template="https://github.com/cli/cli/releases/download/{tag}/gh_{version}_{target}.{ext}",
            version=GitHubRedirect("cli", "cli", strip_v=True),
            targets={
                "Linux-x86_64": "linux_amd64",
                "Linux-aarch64": "linux_arm64",
                "Darwin-x86_64": "macOS_amd64",
                "Darwin-arm64": "macOS_arm64",
            },
            archive={
                "Linux-x86_64": TAR,
                "Linux-aarch64": TAR,
                "Darwin-x86_64": ZIP,
                "Darwin-arm64": ZIP,
            },
            member="gh_{version}_{target}/bin/gh",
            dest=Dest.bin("gh"),
        )
    ],
)

if __name__ == "__main__":
    run_cli(RECIPE)

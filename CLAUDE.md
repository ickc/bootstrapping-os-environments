# CLAUDE.md

Guidance for Claude Code when working in this repository.

## Installer conventions (`src/bsos/installers/`)

### Add installers as recipes
Each tool installer is a thin module that declares a `RECIPE` and calls
`run_cli` — the shared engine in `_recipe.py` handles download, unpack, place,
verify, and uninstall, so `install`/`uninstall`/`test` (plus `--version`) come
for free. To add a tool, define its `RECIPE` (usually a single
`github_binary(...)` call) plus the matching `compile-*` / `install-*` /
`test-*` / `uninstall-*` pixi tasks, then recompile. Reach for the full
`Recipe`/`Artifact` form only for quirks: a per-OS archive type, a binary
nested in a subdirectory, multiple artifacts, or a run-the-downloaded-script
install (`RunScript`, as `mamba` uses). `mamba_env` and `completion` are
intentionally *not* recipes — they need a running mamba / already-installed
tools rather than a download-and-place flow.

### Writing a new recipe — three decisions

**1. Does it come from GitHub releases?**
- Yes, single binary: use `github_binary(name, repo, asset, targets, ...)`.
  `--version` works automatically.
- Yes, with quirks (multiple artifacts, `RunScript`, etc.): use
  `Recipe`/`Artifact` directly with `version=GitHubRedirect(owner, repo, ...)`.
  `--version` works as long as `{version}` appears in the URL template.
- No (e.g. a CDN URL like VS Code): omit `version=`; `--version` will error
  cleanly at runtime with no extra code.

**2. What tag format does the repo use?**

Always use `{tag}` in the URL *path* — it resolves to the full git tag exactly
as released and works for any format:
- Standard `v`-prefix (e.g. `v1.2.3`): `{tag}` → `v1.2.3`.  `github_binary` does this by default.
- No prefix (e.g. Miniforge `26.3.2-2`): `{tag}` → `26.3.2-2`.  Also works with no extra flags.
- Unusual prefix (e.g. codex `rust-v0.135.0`): `{tag}` → `rust-v0.135.0`.  Same.

**3. Does the version appear in the asset filename or archive member?**
- If yes, use `{version}` there — it strips a leading `v` when `strip_v=True`
  (default).  Example: `sman-{target}-v{version}.tgz` / member
  `sman-{target}-v{version}`.  The literal `v` before `{version}` in the
  filename is part of the template string, not a special token.
- Use `strip_v=False` only when the tag has no `v` to strip AND `{version}`
  appears in the filename (rare; for most such repos `{version}` won't be in
  the filename at all, so `strip_v` doesn't matter).

**`--version` convention**: the user passes the git tag as-is (e.g.
`v1.2.3` or `rust-v0.135.0`).  `{tag}` resolves to the raw override;
`{version}` strips a leading `v` when `strip_v=True`.

### No GitHub API calls
Never call `api.github.com` to resolve "latest" release versions. The API is
rate-limited at 60 req/hour for unauthenticated clients; shared CI runners hit
this limit routinely and get a 403. Instead, `GitHubRedirect` follows the
`/releases/latest` redirect to read the final URL and extract the tag name —
one cheap HTTP request, no API key, no rate limit.

### Fail hard on missing prerequisites
`test` actions may exit 0 to skip cleanly on *unsupported platforms* (the
script simply has no work to do there). A missing *dependency* on a supported
platform is a different situation — it means something that should have been
installed wasn't. Print a clear error message and exit 1.

### Compile after every source edit
Each installer module has a compiled counterpart in `install/`. After editing
any source module, recompile it (`pixi run compile-<name>`) before committing.
The unit tests enforce freshness: a stale `install/*.py` fails CI.

### Stdlib only in `bsos.installers`
The installer package and all its helpers use Python stdlib only — no third-party
imports. This constraint must hold in both the source modules and their compiled
output. The compile system enforces it via the unit tests.

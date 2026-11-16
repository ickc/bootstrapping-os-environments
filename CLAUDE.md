# CLAUDE.md

Guidance for Claude Code when working in this repository.

## Conda env pipeline (`conda/`)

`pixi run conda-generate` refreshes each `conda/<stem>.csv` from the
anaconda.org web API, writes a pixi manifest at `conda/<stem>/pixi.toml`
(one feature/environment per name — `conda.csv` yields py311–py315;
platform-selective dependencies via `[feature.*.target.<arch>]`; package
versions are never pinned in the manifest — the lockfile is what pins; the
sole exception is `python`, pinned per env to produce python-version
variants), solves it with `pixi update --no-install` (no env is created; it
must be `update` rather than `lock` — with every spec unpinned, `pixi lock`
finds the old lockfile still satisfies the manifest and never re-solves), and
converts each environment to a unified multi-platform conda-lock file
`conda/<name>-lock.yml` via `pixi-to-conda-lock`. Non-default channels are declared per package
(`potrace = {version = "*", channel = "bioconda"}`); pixi additionally
requires those channels in the workspace channel list, appended after
conda-forge. Package entries in each conda-lock file are topologically
sorted per platform — micromamba installs them in file order (no solve, no
transaction sorting), and alphabetical order runs post-link scripts before
their libraries are linked (e.g. gdk-pixbuf's cache update failing on
libglib). All generated files are committed, pinning the environments in git.

`mamba_env.py` consumes `<name>-lock.yml` by default (micromamba/mamba read
conda-lock files directly, recognized by the `-lock.yml` suffix — misnamed,
they silently create an *empty* env); `--no-lock` selects the per-platform
`<name>_<arch>.yml` instead (e.g. the legacy `py39`). On `update`,
`env update --prune` is tried first; when it fails on a lockfile spec
(current libmamba cannot re-solve against conda-lock files), the env is left
alone if its stamped lockfile sha256 (`conda-meta/.bsos-lock-sha256`) already
matches, else removed and recreated — equivalent, since the lock pins every
package. `test` checks more than that the env exists: on Linux it runs `ldd`
over every ELF executable in the env's `bin/` and fails if a shared library
does not resolve. A lock can solve and install cleanly and still pin a binary
that cannot start — when a feedstock stops being rebuilt the solver walks back
to an old build (w3m's from 2017, wanting `libssl.so.1.0.0`) — and only the
dynamic loader shows it.

The `conda-generate` workflow refreshes the locks weekly and unattended:
generate, commit to `automation/conda-generate`, run the `test-installers`
and `test-bootstrap` jobs against that exact commit (as reusable workflows),
then fast-forward `main` when both are green. The bootstrap is the lock's real
consumer — it creates the `system` env from it on a bare machine and then
relies on the tools it provides — so a lock that installs but breaks the
bootstrap must not land. A pull request is opened only when the tests fail or
`main` moved meanwhile. Do not go back to opening a PR with the default token:
such a PR never gets CI and needs someone to merge it, which is how the locks
once went two months stale.

## Bootstrap (`bootstrap.sh`)

`bootstrap.sh` is the single entry point for provisioning a fresh machine
(`curl -fsSL https://raw.githubusercontent.com/ickc/bootstrapping-os-environments/main/bootstrap.sh | bash`,
`… | bash -s -- --public`). It is a self-contained bash script whose only
external dependency is `curl`. It needs no Python of any version, because the
targets include machines without a usable one: everything is bootstrapped from
micromamba, **micromamba → conda `system` env (pixi, git, gh, zsh, chezmoi, …)
→ the rest**, and the Python installers then run through `pixi run` in the
envoy clone, which brings its own Python. Do not add a step that needs a tool
before the stage that installs it.

- **Stage 0** downloads `env.sh` to a temp file and sources it for
  `__OSTYPE`/`__ARCH`/`__OPT_ROOT`/the XDG dirs, so every later path agrees
  with what envoy's installers use. It also drops non-directories from
  `XDG_CONFIG_DIRS`, which chezmoi otherwise trips over.
- **Stage 1** refuses an unsupported platform (micromamba would create an
  *empty* env rather than fail) and a `__OPT_ROOT` that is not an absolute
  path below `/` (the stage `rm -rf`s `$__OPT_ROOT/system`). It installs the
  micromamba static binary into `$__OPT_ROOT/bin` with the official
  `micro.mamba.pm/install.sh` (`BIN_FOLDER` pre-set, `INIT_YES=no`,
  `CONDA_FORGE_YES=no`, stdin from `/dev/null`: no prompts, no shell-rc or
  `~/.mambarc` edits), then creates the `system` env at `$__OPT_ROOT/system`
  from `conda/system-lock.yml`. The env is left alone when the lockfile's
  sha256 matches `conda-meta/.bsos-lock-sha256`, and removed and recreated
  otherwise, because `env update` cannot consume conda-lock files. The stamp
  is the same one `mamba_env.py` writes and reads, so a later
  `mamba_env update` on an unchanged lock is a no-op too. Where the lockfile
  comes from lives only in `fetch_system_lock`; change it there.
- **Stage 2** clones envoy into `$XDG_DATA_HOME/envoy` and installs the tools
  that are not conda packages, `pixi run python -m bsos.installers update code
  sman`, in that clone.
- **Stage 3** runs `chezmoi init --apply` of `ickc/dotfiles` and clones
  sman-snippets and navi-cheatsheets. The personal path also clones ssh-dir
  into `~/.ssh` and runs `make permission`; a failure there only warns.
- **Stage 4** (personal path only) generates `~/.ssh/id_ed25519` and runs
  `gh auth login`. `--no-identity`, implied by `CI=true`, uses an empty
  passphrase and skips the login, so the personal path can run unattended.
- **Final**: `pixi run generate-completions` in the envoy clone.

The personal path (default) clones over SSH and assumes SSH agent forwarding;
`--public` uses HTTPS and skips ssh-dir and Stage 4. Host keys accepted before
ssh-dir exists go to a throwaway known_hosts file, because git refuses to clone
ssh-dir into a non-empty `~/.ssh`.

Every clone is a managed runtime copy, not a dev checkout: re-running
hard-syncs it to its remote's default branch, discarding local changes to
tracked files and keeping untracked ones (the private keys in `~/.ssh`). That
is what makes a second run idempotent, and it is checked in CI.

### Testing hook: `ENVOY_REPO` and `ENVOY_REF`

Unset, envoy comes from `main` of `ickc/bootstrapping-os-environments`.
`ENVOY_REPO` (owner/name) and `ENVOY_REF` (branch, tag or full sha) select
another source: `env.sh` and the lockfile are fetched from
`raw.githubusercontent.com/$ENVOY_REPO/$ENVOY_REF`, and the clone is fetched
at that ref and checked out detached instead of hard-synced to `main`. All
three must come from one commit — the smoke test compares the env's stamp with
the clone's lockfile. `ENVOY_REF=main` takes the default path.

`test-bootstrap.yml` sets the hook so CI tests the commit under test rather
than `main`: the input `ref` when called from `conda-generate`, the PR head
for a pull request (not the merge commit `github.sha` names, which GitHub
recreates as the base moves), and `github.sha` for a push or a manual run. It
checks out the same commit, runs the public path, the smoke test
(`tests/bootstrap/smoke.sh`, also `pixi run test-bootstrap[-public]`), both
again for idempotency, and asserts the clone is on that commit. Without that
assertion a broken hook would silently test `main`.

Do not run `bootstrap.sh` or the smoke test on a dev machine to try a change:
they work on the real home directory (recreate the `system` env, hard-reset
clones, apply dotfiles). Lint locally (`bash -n`, `pixi run lint`) and let the
pull request's `test-bootstrap` jobs do the end-to-end run.

## Dependency audit (`src/bsos/audit/`)

`pixi run audit` (weekly in CI, `audit.yml`) looks for abandoned or rotting
dependencies. It deliberately does not use "time since last release" —
`bzip2` and `make` are old and fine. The signals are explicit declarations
(upstream repository archived on GitHub, cask deprecated by Homebrew, app
delisted from the App Store) and failure to keep up (no build for a Python
released over a year ago, a package the generator silently dropped, locks or
`flake.lock` that stopped being refreshed). Those are *action* findings and
make the audit exit 1; "held back by another pin" and "pinned build over
three years old" are informational.

A finding is dealt with by fixing it or by acknowledging it in
`audit-ack.toml`, keyed as printed, with a `reason` and a required `until`
date — acknowledgements expire so they get revisited. A green audit therefore
means nothing new. A check that cannot run reports `check-failed` rather than
passing silently.

Keep new checks to signals that hold without a tuned threshold; a check that
needs acknowledging on most runs is noise. `bsos.audit` may use third-party
dependencies (like `bsos.conda`; unlike `bsos.installers`).

## Nix flake (`nix/`)

The `flake-update` workflow bumps `nix/flake.lock` weekly and lands it on
`main` after evaluating every `darwinConfigurations.<host>.system` down to its
derivation, on a macOS runner. Pull requests touching `nix/` run the same
evaluation. It is evaluation only — nothing is built — which catches what a
bump usually breaks (an attribute removed or renamed, a dropped option, a
package newly marked insecure). The Linux dev machines have no nix, so that
workflow is the only place the flake is checked; a change under `nix/` is
verified by its pull request, not locally.

## Installer conventions (`src/bsos/installers/`)

### Add installers as recipes
Each tool installer is a thin module that declares a `RECIPE` and calls
`run_cli` — the shared engine in `_recipe.py` handles download, unpack, place,
verify, and uninstall, so `install`/`uninstall`/`test` (plus `--version`) come
for free. To add a tool, define its `RECIPE` (usually a single
`github_binary(...)` call), then recompile (`pixi run compile`) — installer
modules are auto-discovered, so no per-tool pixi tasks are needed. Reach for the full
`Recipe`/`Artifact` form only for quirks: a per-OS archive type, a binary
nested in a subdirectory, multiple artifacts, or a run-the-downloaded-script
install (`RunScript`, as `mamba` uses). `mamba_env` and `completion` are
intentionally *not* recipes — they need a running micromamba/mamba /
already-installed tools rather than a download-and-place flow.

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

This rule is about installers, which run unauthenticated on end-user machines.
The audit (`bsos.audit.upstream`) does query GitHub — a few batched GraphQL
calls through `gh`, authenticated with the workflow token in CI — and that is
intended.

### Fail hard on missing prerequisites
`test` actions may exit 0 to skip cleanly on *unsupported platforms* (the
script simply has no work to do there). A missing *dependency* on a supported
platform is a different situation — it means something that should have been
installed wasn't. Print a clear error message and exit 1.

### Compile after every source edit
Each installer module has a compiled counterpart in `install/`. After editing
any source module, recompile (`pixi run compile`, or `pixi run compile -- <name>`
for a single module) before committing.
The unit tests enforce freshness: a stale `install/*.py` fails CI.

### Stdlib only in `bsos.installers`
The installer package and all its helpers use Python stdlib only — no third-party
imports. This constraint must hold in both the source modules and their compiled
output. The compile system enforces it via the unit tests.

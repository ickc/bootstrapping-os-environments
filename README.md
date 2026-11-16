# envoy — bootstrapping OS environments

*(package name `bsos`, nicknamed **envoy**)*

Tooling to bootstrap and provision a personal UNIX-like environment across the
machines I actually use — HPC login nodes without root, Linux servers, macOS
laptops, and the occasional Windows box. It is both the toolbox and the
one-line `curl | bash` bootstrap that composes it with my dotfiles and data
repos.

The guiding constraint is **no `sudo`**. The primary path installs everything
into your home directory via a static micromamba binary and conda packages, so
it works on a shared cluster where you'll never be root. Other backends
(nix, dnf, winget) handle the systems where you *are* admin.

## Bootstrap

[`bootstrap.sh`](bootstrap.sh) provisions a fresh machine. It needs nothing but
`curl` — no root, and no Python of any version:

```bash
# Personal: SSH clones (assumes SSH agent forwarding), ssh-dir as ~/.ssh, a new SSH key
curl -fsSL https://raw.githubusercontent.com/ickc/bootstrapping-os-environments/main/bootstrap.sh | bash

# Public: HTTPS clones, no ssh-dir, no SSH key
curl -fsSL https://raw.githubusercontent.com/ickc/bootstrapping-os-environments/main/bootstrap.sh | bash -s -- --public
```

It runs in stages, each relying on what the previous one installed:

1. **micromamba and the `system` env** — the static micromamba binary into
   `$__OPT_ROOT/bin`, then the conda `system` env (pixi, git, gh, zsh, chezmoi,
   …) from this repo's pinned [`conda/system-lock.yml`](conda/system-lock.yml).
2. **envoy** — a clone of this repo at `$XDG_DATA_HOME/envoy`; the tools that
   are not conda packages (the VS Code CLI, sman) are installed by its
   installers, run in its pixi env.
3. **dotfiles and data repos** — `chezmoi init --apply` of
   [dotfiles](https://github.com/ickc/dotfiles), the sman snippets and navi
   cheatsheets; on the personal path also ssh-dir as `~/.ssh`.
4. **identity** (personal path only) — an SSH key for this machine and
   `gh auth login`. `--no-identity` (implied by `CI=true`) uses an empty
   passphrase and skips the login, for unattended runs.

It finishes by generating shell completions. Running it again is safe: the
`system` env is left alone while the lock is unchanged, and the clones are
re-synced to their remotes.

To check the result, run the smoke test that matches the path, from any clone of
this repo (for example the one the bootstrap made):

```bash
pixi run test-bootstrap          # personal path
pixi run test-bootstrap-public   # public path
```

## What's inside

Each top-level directory targets one way of installing software. They're at
different levels of maturity — `conda/` and `nix/` are the developed,
sophisticated ones; the rest range from solid to scratch-pad.

| Directory | Target | What it does |
|-----------|--------|--------------|
| **`conda/`** | Any UNIX, **no root** (HPC, shared servers) | The main event. Version-pinned conda environments (`system`, per-Python `py311`–`py315`, `jupyterlab`) as multi-platform conda-lock files, generated from CSV package lists and committed to git. Installs sudo-lessly into `$HOME` via micromamba. |
| **`nix/`** | macOS (primarily) | A `nix-darwin` flake — declarative system + Homebrew + Mac App Store management. The most reproducible path where Nix is available. |
| **`rhel/`** | RHEL / Fedora Linux servers | `dnf` package lists, `what-provides` helpers, a ZFS install script — for machines where you have root and a real package manager. |
| **`windows/`** | Windows | A `winget` package manifest (`winget import`). |
| **`macOS/`** | macOS | Miscellaneous tweaks — default app associations, key bindings, Cocoa Emacs emulation. |
| **`common/`** | Cross-platform | Odds and ends (e.g. writing an ISO to USB). |
| **`src/bsos/` + `install/`** | Any UNIX | The Python installer toolkit (below) — the engine behind the no-root path. |

## Installers (`src/bsos/installers`, `install/`)

`bsos.installers` is a **stdlib-only** toolkit (Python 3.10+) for installing
individual CLI tools into `$HOME` without root: `micromamba`, `pixi`, `mamba`,
`gh`, `fzf`, `chezmoi`, `navi`, `sman`, the VS Code CLI, `rustup`, `claude`,
`codex`, and more. Each tool is a thin *recipe* (usually one line) over a shared
download-unpack-place-verify engine, so `install` / `uninstall` / `test` (plus
`--version`) come for free.

Every module compiles to a self-contained single-file script under `install/`,
runnable with nothing but a system Python:

```bash
curl -fsSL https://raw.githubusercontent.com/ickc/bootstrapping-os-environments/main/install/code.py | python3 - install
```

With [pixi](https://pixi.sh) available, use the tasks instead:

```bash
pixi run install -- code gh   # install named tools (omit names for all)
pixi run compile              # recompile install/*.py after editing a source module
pixi run smoke -- pixi        # smoke-test an install
```

`env.sh` / `env.fish` (generated from `bsos.installers._env`) derive the
`$__OPT_ROOT`, `MAMBA_ROOT_PREFIX`, and XDG paths everything installs under —
source them from your shell startup.

## Supported platforms

The no-root installer path (and its CI) targets:

- Darwin arm64
- Darwin x86_64
- Linux x86_64
- Linux aarch64

## Continuous integration

The `test-installers` workflow runs the compiled installers end-to-end
(`install` then `test`) on the GitHub-hosted runners that map to each supported
`$(uname -sm)`:

| Runner | Platform |
|--------|----------|
| `ubuntu-latest` | Linux x86_64 |
| `ubuntu-24.04-arm` | Linux aarch64 |
| `macos-latest` | Darwin arm64 |
| `macos-26-intel` | Darwin x86_64 |

`test` skips cleanly (exit 0) on a platform an installer doesn't support, so the
same matrix scales as more installers are added.

The `test-bootstrap` workflow runs `bootstrap.sh --public` end to end on the same
runners, then the smoke test, then both again to show a second run changes
nothing. It bootstraps from the commit under test (through the `ENVOY_REPO` and
`ENVOY_REF` hook documented in the script) rather than from `main`.

Scheduled workflows keep the pinned environments honest:

- **`conda-generate`** (weekly) regenerates the conda locks, runs the
  `test-installers` and `test-bootstrap` jobs against the result, and
  fast-forwards `main` when they pass — no pull request to merge unless
  something fails.
- **`audit`** (weekly) runs `pixi run audit`, which looks for abandoned or
  rotting dependencies: upstreams archived on GitHub, casks Homebrew
  deprecated, apps delisted from the App Store, packages with no build for a
  current Python, locks that stopped being refreshed. It fails when something
  needs a decision; fix it or acknowledge it, with an expiry, in
  [`audit-ack.toml`](audit-ack.toml).
- **`flake-update`** (weekly) bumps `nix/flake.lock`, evaluates every
  `darwinConfiguration`, and lands the bump on `main`. Pull requests that touch
  `nix/` get the same evaluation.

## License

See [LICENSE](LICENSE).

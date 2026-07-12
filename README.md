# envoy — bootstrapping OS environments

*(package name `bsos`, nicknamed **envoy**)*

Tooling to bootstrap and provision a personal UNIX-like environment across the
machines I actually use — HPC login nodes without root, Linux servers, macOS
laptops, and the occasional Windows box. It is the reusable, standalone toolbox;
[**provision**](https://github.com/ickc/provision) is the orchestrator that
composes it with dotfiles and other repos into a one-line `curl | bash`
bootstrap.

The guiding constraint is **no `sudo`**. The primary path installs everything
into your home directory via a static micromamba binary and conda packages, so
it works on a shared cluster where you'll never be root. Other backends
(nix, dnf, winget) handle the systems where you *are* admin.

## What's inside

Each top-level directory targets one way of installing software. They're at
different levels of maturity — `conda/` and `nix/` are the developed,
sophisticated ones; the rest range from solid to scratch-pad.

| Directory | Target | What it does |
|-----------|--------|--------------|
| **`conda/`** | Any UNIX, **no root** (HPC, shared servers) | The main event. Version-pinned conda environments (`system`, per-Python `py310`–`py314`, `jupyterlab`) as multi-platform conda-lock files, generated from CSV package lists and committed to git. Installs sudo-lessly into `$HOME` via micromamba. |
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
curl -fsSL https://raw.githubusercontent.com/ickc/envoy/main/install/code.py | python3 - install
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

## License

See [LICENSE](LICENSE).

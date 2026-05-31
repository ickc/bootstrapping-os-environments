# Supported platform

`$(uname -sm)`
: Darwin arm64
: Darwin x86_64
: Linux x86_64
: Linux aarch64
: Linux ppc64le
: FreeBSD amd64

ppc64le and FreeBSD are not bootstrap targets (no pixi binary) and are
not covered by every installer — e.g. the VS Code CLI installer has no
upstream build for them.

## Installers

`bsos.installers` is a stdlib-only toolkit (Python 3.10+). Each module
exposes `install` / `uninstall` / `test` actions and compiles into a
self-contained single-file script under `install/` for `curl | python3`
use:

```bash
curl -fsSL https://raw.githubusercontent.com/ickc/envoy/main/install/code.py | python3 - install
```

With pixi available, use the tasks instead (`pixi run install -- code`,
`pixi run compile`, `pixi run test`, …).

## Continuous integration

The `test-installers` workflow runs the compiled installers end-to-end
(`install` then `test`) on the GitHub-hosted runners that map to a
supported `$(uname -sm)`:

| Runner | Platform |
|--------|----------|
| `ubuntu-latest` | Linux x86_64 |
| `ubuntu-24.04-arm` | Linux aarch64 |
| `macos-latest` | Darwin arm64 |
| `macos-26-intel` | Darwin x86_64 |

`test` skips cleanly (exit 0) on a platform an installer doesn't
support, so the same matrix works as more installers are added.

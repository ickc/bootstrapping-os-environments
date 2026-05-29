# CLAUDE.md

Guidance for Claude Code when working in this repository.

## Installer conventions (`src/bsos/installers/`)

### No GitHub API calls
Never call `api.github.com` to resolve "latest" release versions. The API is
rate-limited at 60 req/hour for unauthenticated clients; shared CI runners hit
this limit routinely and get a 403. Use the redirect URL instead:

```
https://github.com/<org>/<repo>/releases/latest/download/<filename>
```

GitHub resolves this to the current release with an HTTP redirect — no API
call, no rate limit.

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

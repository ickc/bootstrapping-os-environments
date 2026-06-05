All files in this directory are compiled from `src/bsos/installers/` via the Python
compile system (`pixi run compile`).  Each `<tool>.py` is a self-contained script
that can be run with a stock `python3` — no pixi or other dependencies required.

# Usage

```bash
# Install a single tool (e.g. chezmoi):
python3 install/chezmoi.py install

# Or via curl on a fresh machine:
curl -fsSL https://raw.githubusercontent.com/ickc/envoy/main/install/chezmoi.py | python3 - install
```

# Full system bootstrap

Full bootstrap (all tools + dotfiles + SSH) is orchestrated by the
[provision repo](https://github.com/ickc/provision):

```bash
curl -fsSL https://raw.githubusercontent.com/ickc/provision/main/bootstrap.sh | bash
```

All files in this directory are compiled from `src/bsos/installers/` via the Python
compile system (`pixi run compile`).  Each `<tool>.py` is a self-contained script
that can be run with a stock `python3` — no pixi or other dependencies required.

# Usage

To innstall a single tool (e.g. chezmoi):

Method 1: (assumed the repo is cloned)

```bash
python3 install/chezmoi.py install
```

Method 2: via curl on a fresh machine:

```sh
curl -fsSL https://raw.githubusercontent.com/ickc/envoy/main/install/chezmoi.py | python3 - install
```

Method 3: via curl, but on a fresh machine with Python <3.7:

```sh
# bootstrap pixi first
export PIXI_HOME="${HOME}/.local/opt/$(uname -sm | tr ' ' -)/pixi"
export PIXI_BIN_DIR="${PIXI_HOME}/bin"
export PIXI_NO_PATH_UPDATE=1
curl -fsSL https://pixi.sh/install.sh | sh
# then run it like this:
curl -fsSL https://raw.githubusercontent.com/ickc/envoy/main/install/chezmoi.py | "${PIXI_BIN_DIR}/pixi" exec --spec python python3 - install
```

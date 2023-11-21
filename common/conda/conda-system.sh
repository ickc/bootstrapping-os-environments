#!/usr/bin/env bash

set -e

# * use UPDATE=1 to update the environment instead

# * Define PREFIX if you want to install in a conda prefix instead
# PREFIX=
BINDIR="${BINDIR:-$HOME/.local/bin}"

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

OS="$(uname -s)"
ARCH="$(uname -m)"
case "$OS" in
    Darwin)  # macOS
        case "$ARCH" in
            x86_64)   # macOS x64
                TXT=conda-system.txt
                ;;
            arm64)    # macOS aarch
                TXT=conda-system-Darwin-arm64.txt
                ;;
            *)          # Unknown macOS architecture
                echo "Unknown macOS architecture: $ARCH"
                exit 1
                ;;
        esac
        ;;
    "Linux")   # Linux
        case "$ARCH" in
            "x86_64")   # Linux x64
                TXT=conda-system.txt
                ;;
            "ppc64le")  # Linux ppc64le
                TXT=conda-system-Linux-ppc64le.txt
                ;;
            *)          # Unknown Linux architecture
                echo "Unknown Linux architecture: $ARCH"
                exit 1
                ;;
        esac
        ;;
    *)
        echo "Unsupported OS: $OS"
        exit 1
        ;;
esac

./../../src/bsos/conda_env.py -o temp.yml -n system -C "$TXT" -v 3.11 -c conda-forge
if [[ -z ${PREFIX+x} ]]; then
    ENV_NAME=system311-conda-forge
    if [[ -z "$UPDATE" ]]; then
        mamba env create -f temp.yml -n "$ENV_NAME"
    else
        mamba env update -f temp.yml -n "$ENV_NAME" --prune
    fi
    . activate "$ENV_NAME"
    PREFIX="$CONDA_PREFIX"
else
    if [[ -z "$UPDATE" ]]; then
        mamba env create -f temp.yml -p "$PREFIX"
    else
        mamba env update -f temp.yml -p "$PREFIX" --prune
    fi
fi
rm -f temp.yml

mkdir -p "$BINDIR"
while read line; do
    [[ -e "$PREFIX/bin/$line" ]] && ln -sf "$PREFIX/bin/$line" "$BINDIR"
done < conda-system-link.txt

#!/usr/bin/env bash

# e.g. find /global/common/software/polar/.conda/envs -maxdepth 1 -name '*20190730*' -exec ./conda-uninstall.sh {} \;

set -e

environment="$1"

if [[ ! -d $environment ]]; then
    echo "$environment do not exist." >&2
    echo "You could try finding it from $HOME/.conda/environments.txt" >&2
    exit 1
fi

if [[ -n $NERSC_HOST ]]; then
    alias mamba=/usr/common/software/python/3.8-anaconda-2020.11/bin/mamba
fi

echo "removing environment $environment..."
mamba remove -p "$environment" --all -y

echo "removing its record in $HOME/.conda/environments.txt..."
mv "$HOME/.conda/environments.txt" "$HOME/.conda/environments.txt.backup"
grep -v "$environment" "$HOME/.conda/environments.txt.backup" > "$HOME/.conda/environments.txt"

if [[ $(uname) == Darwin ]]; then
    kernel_prefix="$HOME/Library/Jupyter/kernels"
else
    kernel_prefix="$HOME/.local/share/jupyter/kernels"
fi

echo "removing jupyter kernel in $kernel_prefix/${environment##*/}..."
rm -rf "$kernel_prefix/${environment##*/}"

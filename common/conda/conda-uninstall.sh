#!/usr/bin/env bash

# e.g. find /global/common/software/polar/.conda/envs -maxdepth 1 -name '*20190730*' -exec ./conda-uninstall.sh {} \;

set -e

environment="$1"

if [[ ! -d "$environment" ]]; then
    echo "$environment do not exist." >&2
    echo "You could try finding it from $HOME/.conda/environments.txt" >&2
    exit 1
fi

[[ -n $NERSC_HOST ]] && module load python/3.7-anaconda-2019.07

echo "removing environment $environment..."
mamba remove -p "$environment" --all -y

echo "removing its record in $HOME/.conda/environments.txt..."
mv "$HOME/.conda/environments.txt" "$HOME/.conda/environments.txt.backup"
grep -v "$environment" "$HOME/.conda/environments.txt.backup" > "$HOME/.conda/environments.txt"

echo "removing jupyter kernel in $HOME/.local/share/jupyter/kernels/${environment##*/}..."
rm -rf "$HOME/.local/share/jupyter/kernels/${environment##*/}"

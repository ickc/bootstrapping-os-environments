#!/usr/bin/env bash

set -e

environment="$1"

if [[ ! -d "$environment" ]]; then
    echo "$environment do not exist." >&2
    echo "You could try finding it from $HOME/.conda/environments.txt" >&2
    exit 1
fi

[[ -n $NERSC_HOST ]] && module load python/3.6-anaconda-5.2

echo "removing environment $environment..."
conda remove -p "$environment" --all -y

echo "removing its record in $HOME/.conda/environments.txt..."
mv "$HOME/.conda/environments.txt" "$HOME/.conda/environments.txt.backup"
grep -v "$environment" "$HOME/.conda/environments.txt.backup" > "$HOME/.conda/environments.txt"

echo "removing jupyter kernel in $HOME/.local/share/jupyter/kernels/${environment##*/}..."
rm -rf "$HOME/.local/share/jupyter/kernels/${environment##*/}"

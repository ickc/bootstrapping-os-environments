#!/usr/bin/env bash

set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

./conda_env.py -o temp.yml -n system -C conda-system.txt -v 3.9 -c conda-forge
mamba env create -f temp.yml -p /global/common/software/polar/.conda/envs/system39-conda-forge
rm -f temp.yml

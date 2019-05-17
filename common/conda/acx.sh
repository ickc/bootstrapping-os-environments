#!/usr/bin/env bash

set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

conda env create -f "$DIR/acx.yml"

. activate acx

# ipython kernel
python -m ipykernel install --user --name acx

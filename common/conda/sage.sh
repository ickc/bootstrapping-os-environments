#!/usr/bin/env bash

set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

mamba env create -f "$DIR/sage.yml"

. activate sage2

# sagemath kernel
jupyter kernelspec install --user $(dirname $(which sage))/../share/jupyter/kernels/sagemath --name sagemath2

# ipython kernel
python -m ipykernel install --user --name sage2

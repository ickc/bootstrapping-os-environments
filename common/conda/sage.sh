#!/usr/bin/env bash

set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

conda env create -f "$DIR/sage.yml" -f

. activate sage

# sagemath kernel
jupyter kernelspec install --user $(dirname $(which sage))/../share/jupyter/kernels/sagemath

# ipython kernel
python -m ipykernel install --user --name sage

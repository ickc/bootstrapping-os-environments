#!/usr/bin/env bash

set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

conda env create -f "$DIR/sage3.yml"

. activate sage3

# sagemath kernel
jupyter kernelspec install --user $(dirname $(which sage))/../share/jupyter/kernels/sagemath --name sagemath3

# ipython kernel
python -m ipykernel install --user --name sage3

#!/usr/bin/env bash

set -e

NAME="${NAME:-sage}"

conda create -n "$NAME" intelpython3_core 'python>=3' sage -y

. activate "$NAME"

# sagemath kernel
jupyter kernelspec install --user $(dirname $(which sage))/../share/jupyter/kernels/sagemath

# ipython kernel
python -m ipykernel install --user --name "$NAME"

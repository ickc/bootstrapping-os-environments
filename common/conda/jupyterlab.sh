#!/usr/bin/env bash

set -e

path2txt="$(dirname "${BASH_SOURCE[0]}")/jupyterlab.txt"

# create environment jupyterlab for using in jupyterhub
conda create -n jupyterlab -c conda-forge python=3 jupyterlab jupyterhub -y
. activate jupyterlab

temp=($(grep -v '#' "$path2txt"))

# https://plotly.com/python/getting-started/#jupyterlab-support-python-35
export NODE_OPTIONS=--max-old-space-size=4096
jupyter labextension install "${temp[@]}"

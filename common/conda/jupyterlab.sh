#!/usr/bin/env bash

set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# create environment jupyterlab for using in jupyterhub
mamba env create -f "$DIR/jupyterlab.yml"
. activate jupyterlab

temp=($(grep -v '#' "$DIR/jupyterlab.txt"))

# https://plotly.com/python/getting-started/#jupyterlab-support-python-35
export NODE_OPTIONS=--max-old-space-size=4096
jupyter labextension install "${temp[@]}"

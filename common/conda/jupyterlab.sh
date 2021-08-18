#!/usr/bin/env bash

set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# create environment jupyterlab for using in jupyterhub
mamba env create -f "$DIR/jupyterlab.yml" || mamba env update -f "$DIR/jupyterlab.yml"

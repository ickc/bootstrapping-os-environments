#!/usr/bin/env bash

set -e

path2txt="$(dirname "${BASH_SOURCE[0]}")/jupyterlab.txt"

# create environment jupyterlab for using in jupyterhub
conda create -n jupyterlab -c defaults python=3 jupyterlab jupyterhub jupyterthemes 'pyzmq>=17' nodejs -y
. activate jupyterlab

temp=($(grep -v '#' "$path2txt"))
jupyter labextension install "${temp[@]}"

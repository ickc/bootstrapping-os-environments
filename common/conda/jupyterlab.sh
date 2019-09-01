#!/usr/bin/env bash

set -e

path2txt="$(dirname "${BASH_SOURCE[0]}")/jupyterlab.txt"

# create environment jupyterlab for using in jupyterhub
conda create -n jupyterlab -c defaults python=3 jupyterlab jupyterhub 'pyzmq>=17' nodejs -y
. activate jupyterlab

npm install -g npm
npm install -g node

temp=($(grep -v '#' "$path2txt"))
jupyter labextension install "${temp[@]}"

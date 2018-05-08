#!/usr/bin/env bash

# create environment jupyterlab for using in jupyterhub

conda create -n jupyterlab python=3.6 jupyterlab jupyterhub jupyterthemes -y &&
. activate jupyterlab &&
jupyter labextension install @jupyterlab/hub-extension

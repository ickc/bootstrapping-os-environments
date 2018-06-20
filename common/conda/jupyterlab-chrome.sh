#!/usr/bin/env bash

. activate jupyterlab

jupyter lab --generate-config

cat << 'EOF' >> ~/.jupyter/jupyter_notebook_config.py
c.LabApp.browser = '"/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary" --app=%s'
EOF

#!/usr/bin/env bash

. activate jupyterlab

jupyter lab --generate-config

cat << 'EOF' >> ~/.jupyter/jupyter_notebook_config.py
c.LabApp.browser = '"/Applications/Chromium.app/Contents/MacOS/Chromium" --app=%s'
EOF

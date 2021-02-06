#!/usr/bin/env bash

. activate jupyterlab

mkdir -p ~/.jupyter
: > ~/.jupyter/jupyter_lab_config.py

if [[ $(uname) == Darwin ]]; then
cat << 'EOF' >> ~/.jupyter/jupyter_lab_config.py
c.LabApp.browser = '"/Applications/Chromium.app/Contents/MacOS/Chromium" -incognito --app=%s'
EOF
else
cat << 'EOF' >> ~/.jupyter/jupyter_lab_config.py
c.LabApp.browser = 'chromium-browser -incognito --app=%s'
EOF
fi

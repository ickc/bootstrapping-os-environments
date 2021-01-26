#!/usr/bin/env bash

. activate jupyterlab

mkdir -p ~/.jupyter
: > ~/.jupyter/jupyter_notebook_config.py

if [[ $(uname) == Darwin ]]; then
cat << 'EOF' >> ~/.jupyter/jupyter_notebook_config.py
c.LabApp.browser = '"/Applications/Chromium.app/Contents/MacOS/Chromium" --app=%s'
c.NotebookApp.use_redirect_file = False
EOF
else
cat << 'EOF' >> ~/.jupyter/jupyter_notebook_config.py
c.LabApp.browser = 'chromium-browser --app=%s'
c.NotebookApp.use_redirect_file = False
EOF
fi

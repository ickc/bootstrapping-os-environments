#!/usr/bin/env bash

. activate jupyterlab

mkdir -p "$HOME/.jupyter"

if [[ $(uname) == Darwin ]]; then
    cat << 'EOF' > "$HOME/.jupyter/jupyter_lab_config.py"
c.ServerApp.browser = "/Applications/Chromium.app/Contents/MacOS/Chromium --app=%s"
c.ServerApp.iopub_data_rate_limit = 10000000000
EOF
else
    cat << 'EOF' > "$HOME/.jupyter/jupyter_lab_config.py"
c.ServerApp.browser = "chromium-browser --app=%s"
c.ServerApp.iopub_data_rate_limit = 10000000000
EOF
fi

# https://jupyterlab.readthedocs.io/en/stable/user/jupyterhub.html#jupyterhub
cat << EOF > "$HOME/.jupyter/jupyterhub_config.py"
c.Spawner.default_url = "/lab"
c.JupyterHub.ssl_key = "$HOME/.jupyter/ssl.key"
c.JupyterHub.ssl_cert = "$HOME/.jupyter/ssl.crt"
EOF

openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout "$HOME/.jupyter/ssl.key" -out "$HOME/.jupyter/ssl.crt"

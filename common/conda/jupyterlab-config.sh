#!/usr/bin/env bash

. activate jupyterlab

JUPYTER_CONFIG_DIR="${JUPYTER_CONFIG_DIR}:-${HOME}/.jupyter}"
mkdir -p "${JUPYTER_CONFIG_DIR}"

if [[ $(uname) == Darwin ]]; then
    cat << 'EOF' > "${JUPYTER_CONFIG_DIR}/jupyter_lab_config.py"
c.ServerApp.browser = "/Applications/Chromium.app/Contents/MacOS/Chromium --app=%s"
c.ServerApp.iopub_data_rate_limit = 10000000000
EOF
else
    cat << 'EOF' > "${JUPYTER_CONFIG_DIR}/jupyter_lab_config.py"
c.ServerApp.browser = "chromium-browser --app=%s"
c.ServerApp.iopub_data_rate_limit = 10000000000
EOF
fi

# https://jupyterlab.readthedocs.io/en/stable/user/jupyterhub.html#jupyterhub
cat << EOF > "${JUPYTER_CONFIG_DIR}/jupyterhub_config.py"
c.Spawner.default_url = "/lab"
c.JupyterHub.ssl_key = "${JUPYTER_CONFIG_DIR}/ssl.key"
c.JupyterHub.ssl_cert = "${JUPYTER_CONFIG_DIR}/ssl.crt"
EOF

openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout "${JUPYTER_CONFIG_DIR}/ssl.key" -out "${HOME}/.jupyter/ssl.crt"

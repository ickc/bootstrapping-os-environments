#!/usr/bin/env bash

mkdir -p ~/.jupyter

cat << 'EOF' > ~/.jupyter/jupyter_lab_config.py
c.ServerApp.iopub_data_rate_limit = 10000000000
EOF

# https://jupyterlab.readthedocs.io/en/stable/user/jupyterhub.html#jupyterhub
cat << EOF | sudo tee -a /etc/jupyterhub/jupyterhub_config.py
c.Spawner.default_url = "/lab"
c.JupyterHub.ssl_key = "/etc/jupyterhub/ssl.key"
c.JupyterHub.ssl_cert = "/etc/jupyterhub/ssl.crt"
EOF

sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/jupyterhub/ssl.key -out /etc/jupyterhub/ssl.crt

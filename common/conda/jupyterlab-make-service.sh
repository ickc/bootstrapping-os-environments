#!/usr/bin/env bash

# usage: ./make-service.sh
# env var PYTHONPATH will be used
# assumes the directory this script is residing does not need escape
# create a /usr/lib/systemd/system/jupyterhub.service s.t.
# the jupyterhub service can be started via
# sudo systemctl enable --now jupyterhub

SERVICEFILE="${SERVICEFILE:-/usr/lib/systemd/system/jupyterhub.service}"
RUNUSER="${RUNUSER:-$USER}"
WORKINGDIR="${WORKINGDIR:-$HOME}"

cat << EOF |
[Unit]
Description=Jupyterhub
After=syslog.target network.target

[Service]
User=$RUNUSER
Environment=PYTHONPATH=$PYTHONPATH
ExecStart=/bin/sh -c 'source /opt/anaconda/bin/activate jupyterlab && jupyterhub labhub'
WorkingDirectory=$WORKINGDIR

[Install]
WantedBy=multi-user.target
EOF
sudo tee "$SERVICEFILE"

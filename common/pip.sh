#!/bin/bash

pip3 install -r pip.txt

printf "%s\n" "c.NotebookApp.browser = '/Applications/Firefox.app/Contents/MacOS/firefox-bin %s'" > $HOME/.jupyter/jupyter_notebook_config.py

# install jupyter widget extension
jupyter nbextension enable --py --sys-prefix widgetsnbextension

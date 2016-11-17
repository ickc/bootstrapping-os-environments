#!/bin/bash

pip install -U pandocfilters
pip install -U panflute
pip install -U ipython
pip install -U numpy
pip install -U scipy
pip install -U matplotlib
pip install -U nose
pip install -U pandas
pip install -U sympy
pip install -U cython
pip install -U jupyter && printf "%s\n" "c.NotebookApp.browser = '/Applications/Firefox.app/Contents/MacOS/firefox-bin %s'" > $HOME/.jupyter/jupyter_notebook_config.py
pip install -U seaborn
pip install -U moviepy
pip install -U tabulate
pip install -U terminaltables
pip install -U astropy
pip install -U openpyxl
pip install -U pillow
pip install -U pyyaml
pip install -U autopep8

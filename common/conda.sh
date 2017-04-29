#!/bin/bash

grep -v '#' conda.txt | xargs -n 1 -P 1 conda install

# install jupyter widget extension
jupyter nbextension enable --py --sys-prefix widgetsnbextension

conda create -n idp3 python=3 ipykernel

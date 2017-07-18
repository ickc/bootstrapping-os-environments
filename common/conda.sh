#!/bin/bash

conda create -n idp3 -c intel intelpython3_core python=3 -y

. activate idp3

grep -v '#' conda.txt | xargs -n 1 -P 1 conda install -y
# install the mpi4py with mpich
conda install -c mpi4py mpi4py mpich -y

# iPython kernel
python -m ipykernel install --user --name idp3 --display-name "IDP3"

# install jupyter widget extension
jupyter nbextension enable --py --sys-prefix widgetsnbextension

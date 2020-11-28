#!/usr/bin/env bash

set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# install conda environments

# ab2-defaults
# ./conda_env.py -o temp.yml -n "ab" -C conda.txt -P pip.txt
# conda env create -f temp.yml
# ab2-intel
# ./conda_env.py -o temp.yml -n "ab" -C conda.txt -P pip.txt -c intel
# conda env create -f temp.yml

# all2-defaults
# ./conda_env.py -o temp.yml -n "all" -C conda.txt conda-all.txt conda-CPython.txt -P pip.txt pip-all.txt
# conda env create -f temp.yml
# all2-intel
# ./conda_env.py -o temp.yml -n "all" -C conda.txt conda-all.txt conda-CPython.txt -P pip.txt pip-all.txt -c intel
# conda env create -f temp.yml

# ab38-defaults
# ./conda_env.py -o temp.yml -n "ab" -C conda.txt -P pip.txt -v 3.8
# conda env create -f temp.yml
# ab37-intel
# ./conda_env.py -o temp.yml -n "ab" -C conda.txt -P pip.txt -c intel -v 3.7
# conda env create -f temp.yml

# all38-defaults
./conda_env.py -o temp.yml -n "all" -C conda.txt conda-all.txt conda-CPython.txt conda-Python3.8.txt -P pip.txt pip-all.txt -v 3.8
conda env create -f temp.yml
# all37-intel
./conda_env.py -o temp.yml -n "all" -C conda.txt conda-all.txt conda-CPython.txt conda-Python3.8.txt -P pip.txt pip-all.txt -c intel -v 3.7
conda env create -f temp.yml

# all39-defaults
./conda_env.py -o temp.yml -n "all" -C conda.txt conda-all.txt conda-CPython.txt -P pip.txt pip-all.txt -v 3.9
conda env create -f temp.yml

# pypy36-conda-forge
# ./conda_env.py -o temp.yml -n "pypy" -C conda.txt conda-all.txt -P pip.txt pip-all.txt -v 3.6 --pypy -c conda-forge
conda env create -f pypy36-conda-forge.yml

rm -f temp.yml

# iterate over each conda environment

    conda info --env | grep -v -E '#|root' - | grep -E '(defaults|intel|conda-forge)' - | cut -d' ' -f1 | xargs -i bash -c '
        for name do
            . activate "$name"
            python -m ipykernel install --user --name "$name" --display-name "$name"
            conda deactivate
        done' bash {}

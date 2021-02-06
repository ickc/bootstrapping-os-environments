#!/usr/bin/env bash

set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# install conda environments

# ab2-defaults
# ./conda_env.py -o temp.yml -m mpich -n "ab" -C conda.txt
# mamba env create -f temp.yml
# ab2-intel
# ./conda_env.py -o temp.yml -m mpich -n "ab" -C conda.txt -c intel
# mamba env create -f temp.yml

# all2-defaults
# ./conda_env.py -o temp.yml -m mpich -n "all" -C conda.txt conda-all.txt conda-CPython.txt
# mamba env create -f temp.yml
# all2-intel
# ./conda_env.py -o temp.yml -m mpich -n "all" -C conda.txt conda-all.txt conda-CPython.txt -c intel
# mamba env create -f temp.yml

# ab38-defaults
# ./conda_env.py -o temp.yml -m mpich -n "ab" -C conda.txt -v 3.8
# mamba env create -f temp.yml
# ab37-intel
# ./conda_env.py -o temp.yml -m mpich -n "ab" -C conda.txt -c intel -v 3.7
# mamba env create -f temp.yml

# all38-defaults
./conda_env.py -o temp.yml -m mpich -n "all" -C conda.txt conda-all.txt conda-CPython.txt -v 3.8
mamba env create -f temp.yml
# all37-intel
./conda_env.py -o temp.yml -m mpich -n "all" -C conda.txt conda-all.txt conda-CPython.txt -c intel -v 3.7
mamba env create -f temp.yml

# all39-defaults
./conda_env.py -o temp.yml -m mpich -n "all" -C conda.txt conda-all.txt conda-CPython.txt -v 3.9
mamba env create -f temp.yml

# pip39-defaults
./conda_env.py -o temp.yml -n "pip" -P pip.txt -v 3.9
mamba env create -f temp.yml

# these bare envs are for tox

# bare35-defaults
./conda_env.py -o temp.yml -n "bare" -v 3.5
mamba env create -f temp.yml

# bare36-defaults
./conda_env.py -o temp.yml -n "bare" -v 3.6
mamba env create -f temp.yml

# bare-pypy27-conda-forge
./conda_env.py -o temp.yml -n "bare-pypy" -v 2.7 --pypy -c conda-forge
mamba env create -f temp.yml

# bare-pypy36-conda-forge
./conda_env.py -o temp.yml -n "bare-pypy" -v 3.6 --pypy -c conda-forge
mamba env create -f temp.yml

# bare-pypy37-conda-forge
./conda_env.py -o temp.yml -n "bare-pypy" -v 3.7 --pypy -c conda-forge
mamba env create -f temp.yml

# pypy36-conda-forge
# ./conda_env.py -o temp.yml -m mpich -n "pypy" -C conda.txt conda-all.txt -v 3.6 --pypy -c conda-forge
# mamba env create -f pypy36-conda-forge.yml

rm -f temp.yml

# iterate over each conda environment

conda info --env | grep -v -E '#|base' - | grep -E '(defaults|intel|conda-forge)' - | cut -d' ' -f1 | xargs -i bash -c '
    for name do
        . activate "$name"
        python -m ipykernel install --user --name "$name" --display-name "$name"
        conda deactivate
    done' bash {}

conda info --env | grep -v -E '#|base' - | grep -E '^(all|pip)' - | cut -d' ' -f1 | xargs -i bash -c '
    for name do
        . activate "$name"
        case "$name" in
        *-defaults)
            cp condarc/defaults.yml "$CONDA_PREFIX/.condarc"
            ;;
        *-conda-forge)
            cp condarc/conda-forge.yml "$CONDA_PREFIX/.condarc"
            ;;
        *-intel)
            cp condarc/intel.yml "$CONDA_PREFIX/.condarc"
            ;;
        pip*)
            cp condarc/pip.yml "$CONDA_PREFIX/.condarc"
            ;;
        esac
        conda deactivate
    done' bash {}

#!/usr/bin/env bash

# usage: UPDATE=1 ./conda-install.sh

set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# install conda environments

# all37-conda-forge
./../../src/bsos/conda_env.py -o temp.yml -m mpich -n "all" -C conda.csv -c conda-forge -v 3.7
if [[ -n ${UPDATE+x} ]]; then
    mamba env update -f temp.yml
else
    mamba env create -f temp.yml
fi
# all38-conda-forge
./../../src/bsos/conda_env.py -o temp.yml -m mpich -n "all" -C conda.csv -c conda-forge -v 3.8
if [[ -n ${UPDATE+x} ]]; then
    mamba env update -f temp.yml
else
    mamba env create -f temp.yml
fi
# all39-conda-forge
./../../src/bsos/conda_env.py -o temp.yml -m mpich -n "all" -C conda.csv -c conda-forge -v 3.9
if [[ -n ${UPDATE+x} ]]; then
    mamba env update -f temp.yml
else
    mamba env create -f temp.yml
fi
# all310-conda-forge
./../../src/bsos/conda_env.py -o temp.yml -m mpich -n "all" -C conda.csv -c conda-forge -v 3.10
if [[ -n ${UPDATE+x} ]]; then
    mamba env update -f temp.yml
else
    mamba env create -f temp.yml
fi
# all311-conda-forge
./../../src/bsos/conda_env.py -o temp.yml -m mpich -n "all" -C conda.csv -c conda-forge -v 3.11
if [[ -n ${UPDATE+x} ]]; then
    mamba env update -f temp.yml
else
    mamba env create -f temp.yml
fi
# pypy-37-conda-forge
./../../src/bsos/conda_env.py -o temp.yml -m mpich -n "pypy" -C conda.csv -c conda-forge -v 3.7 --pypy
if [[ -n ${UPDATE+x} ]]; then
    mamba env update -f temp.yml
else
    mamba env create -f temp.yml
fi

# pip311-defaults
./../../src/bsos/conda_env.py -o temp.yml -n "pip" -P pip.txt -v 3.11
if [[ -n ${UPDATE+x} ]]; then
    mamba env update -f temp.yml
else
    mamba env create -f temp.yml
fi

# these bare envs are for tox

# bare36-defaults
# ./../../src/bsos/conda_env.py -o temp.yml -n "bare" -v 3.6
# mamba env create -f temp.yml

# bare-pypy27-conda-forge
# ./../../src/bsos/conda_env.py -o temp.yml -n "bare-pypy" -v 2.7 --pypy -c conda-forge
# mamba env create -f temp.yml

# bare-pypy36-conda-forge
# ./../../src/bsos/conda_env.py -o temp.yml -n "bare-pypy" -v 3.6 --pypy -c conda-forge
# mamba env create -f temp.yml

# bare-pypy37-conda-forge
# ./../../src/bsos/conda_env.py -o temp.yml -n "bare-pypy" -v 3.7 --pypy -c conda-forge
# mamba env create -f temp.yml

# pypy36-conda-forge
# ./../../src/bsos/conda_env.py -o temp.yml -m mpich -n "pypy" -C conda.txt conda-all.txt -v 3.6 --pypy -c conda-forge
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

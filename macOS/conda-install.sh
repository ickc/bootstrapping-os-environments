#!/usr/bin/env bash

set -e

path2ReproducibleOsEnvironments="$HOME/git/source/reproducible-os-environments"

conda_script_path="$path2ReproducibleOsEnvironments/common/conda/conda.py"
conda_path="$path2ReproducibleOsEnvironments/common/conda/conda.txt"
conda_all_path="$path2ReproducibleOsEnvironments/common/conda/conda-all.txt"
pip_path="$path2ReproducibleOsEnvironments/common/conda/pip.txt"
pip_all_path="$path2ReproducibleOsEnvironments/common/conda/pip-all.txt"

date=$(date +%Y%m%d)

# install conda environments

# ab2-defaults
"$conda_script_path" -o "$path2ReproducibleOsEnvironments/temp.yml" -n "ab" -C "$conda_path" -P "$pip_path"
conda env create -f "$path2ReproducibleOsEnvironments/temp.yml"
# ab2-intel
"$conda_script_path" -o "$path2ReproducibleOsEnvironments/temp.yml" -n "ab" -C "$conda_path" -P "$pip_path" -c intel
conda env create -f "$path2ReproducibleOsEnvironments/temp.yml"

# all2-defaults
"$conda_script_path" -o "$path2ReproducibleOsEnvironments/temp.yml" -n "all" -C "$conda_all_path" -P "$pip_all_path"
conda env create -f "$path2ReproducibleOsEnvironments/temp.yml"
# all2-intel
"$conda_script_path" -o "$path2ReproducibleOsEnvironments/temp.yml" -n "all" -C "$conda_all_path" -P "$pip_all_path" -c intel
conda env create -f "$path2ReproducibleOsEnvironments/temp.yml"

# ab3-defaults
"$conda_script_path" -o "$path2ReproducibleOsEnvironments/temp.yml" -n "ab" -C "$conda_path" -P "$pip_path" -v 3
conda env create -f "$path2ReproducibleOsEnvironments/temp.yml"
# ab3-intel
"$conda_script_path" -o "$path2ReproducibleOsEnvironments/temp.yml" -n "ab" -C "$conda_path" -P "$pip_path" -c intel -v 3
conda env create -f "$path2ReproducibleOsEnvironments/temp.yml"

# all3-defaults
"$conda_script_path" -o "$path2ReproducibleOsEnvironments/temp.yml" -n "all" -C "$conda_all_path" -P "$pip_all_path" -v 3
conda env create -f "$path2ReproducibleOsEnvironments/temp.yml"
# all3-intel
"$conda_script_path" -o "$path2ReproducibleOsEnvironments/temp.yml" -n "all" -C "$conda_all_path" -P "$pip_all_path" -c intel -v 3
conda env create -f "$path2ReproducibleOsEnvironments/temp.yml"

rm -f "$path2ReproducibleOsEnvironments/temp.yml"

#!/usr/bin/env bash

set -e

# helpers ##############################################################

print_double_line () {
    eval printf %.0s= '{1..'"${COLUMNS:-$(tput cols)}"\}
}

print_line () {
    eval printf %.0s- '{1..'"${COLUMNS:-$(tput cols)}"\}
}

########################################################################

install () {
if command -v git &> /dev/null; then
    NOGIT=0
else
    NOGIT=1
fi

mkdir -p ~/git/source
cd ~/git/source
if [[ $NOGIT -eq 0 ]]; then
    mkdir -p ~/.ssh
    ssh-keyscan github.com >> ~/.ssh/known_hosts
    print_double_line
    echo "Cloning bootstrapping-os-environments..."
    git clone git@github.com:ickc/bootstrapping-os-environments.git || git clone https://github.com/ickc/bootstrapping-os-environments.git
else
    print_double_line
    echo "git not found, downloading bootstrapping-os-environments..."
    curl -O -L https://github.com/ickc/bootstrapping-os-environments/archive/refs/heads/master.zip
    unzip master.zip
    rm -f master.zip
    mv bootstrapping-os-environments-master bootstrapping-os-environments
fi

print_double_line
echo "Installing mamba..."
CONDA_PREFIX=~/.mambaforge ~/git/source/bootstrapping-os-environments/install/mamba.sh
. ~/.mambaforge/bin/activate

print_line
echo "Installing system packages from conda..."
~/git/source/bootstrapping-os-environments/common/conda/conda-system.sh
export PATH="$HOME/.local/bin:$PATH"

if [[ $NOGIT -eq 1 ]]; then
    rm -rf ~/git/source/bootstrapping-os-environments
    cd ~/git/source
    git clone git@github.com:ickc/bootstrapping-os-environments.git || git clone https://github.com/ickc/bootstrapping-os-environments.git
fi
}

install

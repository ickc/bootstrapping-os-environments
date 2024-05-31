#!/usr/bin/env bash

set -e

PREFIX="${PREFIX:-$HOME}"
# point CONDA_PREFIX to an existing conda/mamba prefix to skip installing mamba
CONDA_PREFIX="${CONDA_PREFIX:-$PREFIX/.mambaforge}"

# helpers ##############################################################

print_double_line() {
    eval printf %.0s= '{1..'"${COLUMNS:-$(tput cols)}"\}
}

print_line() {
    eval printf %.0s- '{1..'"${COLUMNS:-$(tput cols)}"\}
}

########################################################################

install() {
    if command -v git &> /dev/null; then
        NOGIT=0
    else
        NOGIT=1
    fi

    # git 2.3.0 or later is required
    export GIT_SSH_COMMAND="ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no"

    mkdir -p "$PREFIX/git/source"
    cd "$PREFIX/git/source"
    print_double_line
    if [[ $NOGIT == 0 ]]; then
        echo "Cloning bootstrapping-os-environments..."
        git clone git@github.com:ickc/bootstrapping-os-environments.git || git clone https://github.com/ickc/bootstrapping-os-environments.git
    else
        echo "git not found, downloading bootstrapping-os-environments..."
        curl -O -L https://github.com/ickc/bootstrapping-os-environments/archive/refs/heads/master.zip
        unzip master.zip
        rm -f master.zip
        mv bootstrapping-os-environments-master bootstrapping-os-environments
    fi

    print_double_line
    if [[ -x ${CONDA_PREFIX}/bin/mamba ]]; then
        echo "Using existing mamba prefix at $CONDA_PREFIX"
    else
        echo "Installing mamba..."
        export CONDA_PREFIX
        "$PREFIX/git/source/bootstrapping-os-environments/install/mamba.sh"
    fi
    # shellcheck disable=SC1091
    . "$CONDA_PREFIX/bin/activate"

    print_line
    echo "Installing system packages from conda..."
    "$PREFIX/git/source/bootstrapping-os-environments/common/conda/conda-system.sh"
    export PATH="$PREFIX/.local/bin:$PATH"

    if [[ $NOGIT -eq 1 ]]; then
        rm -rf "$PREFIX/git/source/bootstrapping-os-environments"
        cd "$PREFIX/git/source"
        git clone git@github.com:ickc/bootstrapping-os-environments.git || git clone https://github.com/ickc/bootstrapping-os-environments.git
    fi
}

install

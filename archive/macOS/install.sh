#!/usr/bin/env zsh

set -e

# helpers ##############################################################

print_double_line() {
    eval printf %.0s= '{1..'"${COLUMNS:-$(tput cols)}"\}
}

print_line() {
    eval printf %.0s- '{1..'"${COLUMNS:-$(tput cols)}"\}
}

########################################################################

print_double_line
echo "install homebrew..."
if [[ "$(uname -m)" == arm64 ]]; then
    HOMEBREW_PREFIX=/opt/homebrew
    NONINTERACTIVE=1 /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
else
    HOMEBREW_PREFIX="${HOME}/.homebrew"
    # install brew
    sudo mkdir -p "${HOMEBREW_PREFIX}" && sudo chown "${USER}" "${HOMEBREW_PREFIX}" && sudo chgrp staff "${HOMEBREW_PREFIX}"
    curl -L https://github.com/Homebrew/brew/tarball/master | tar xz --strip 1 -C "${HOMEBREW_PREFIX}"
fi

print_double_line
echo 'install basher...'
../install/basher.sh

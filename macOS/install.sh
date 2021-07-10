#!/usr/bin/env zsh

set -e

MACPORTS_VERSION=2.7.1
MACPORTS_OS_VERSION=11-BigSur
# TODO: on next macOS major upgrade we should move to /opt/homebrew and create a dedicated homebrew user account to manage this
HOMEBREW_PREFIX="$HOME/.homebrew"
CONDA_PREFIX="${CONDA_PREFIX:-"$HOME/.mambaforge"}"

# sudo loop
sudo xcodebuild -license accept
while true; do sudo -n true; sleep 60; kill -0 "$$" || exit; done 2>/dev/null &

# install xcode command line tools
xcode-select --install

# helpers ##############################################################

print_double_line () {
    eval printf %.0s= '{1..'"${COLUMNS:-$(tput cols)}"\}
}

print_line () {
    eval printf %.0s- '{1..'"${COLUMNS:-$(tput cols)}"\}
}

########################################################################

print_double_line
echo "install macports..."
# port: update from https://www.macports.org/install.php
# prebuild binaries
curl -L "https://github.com/macports/macports-base/releases/download/v${MACPORTS_VERSION}/MacPorts-${MACPORTS_VERSION}-${MACPORTS_OS_VERSION}.pkg" --output "MacPorts-${MACPORTS_VERSION}-${MACPORTS_OS_VERSION}.pkg"
sudo installer -pkg "MacPorts-${MACPORTS_VERSION}-${MACPORTS_OS_VERSION}.pkg" -target /
rm -f "MacPorts-${MACPORTS_VERSION}-${MACPORTS_OS_VERSION}.pkg"
# build from source
# curl https://distfiles.macports.org/MacPorts/MacPorts-${MACPORTS_VERSION}.tar.bz2 --output MacPorts-${MACPORTS_VERSION}.tar.bz2
# tar xjvf MacPorts-${MACPORTS_VERSION}.tar.bz2
# cd MacPorts-${MACPORTS_VERSION}
# build from master
# git clone https://github.com/macports/macports-base.git
# cd macports-base
# ./configure && make && sudo make install
# cd ..
# rm -rf MacPorts-${MACPORTS_VERSION}*
# rm -rf macports-base
sudo /opt/local/bin/port -v selfupdate

print_double_line
echo "install homebrew..."
# install brew
sudo mkdir -p "$HOMEBREW_PREFIX" && sudo chown "$USER" "$HOMEBREW_PREFIX" && sudo chgrp staff "$HOMEBREW_PREFIX"
curl -L https://github.com/Homebrew/brew/tarball/master | tar xz --strip 1 -C "$HOMEBREW_PREFIX"

export PATH="$HOMEBREW_PREFIX/bin:$PATH"
print_double_line
echo "install mas..."
brew install mas

print_double_line
echo 'install oracle-jdk...'
brew install --cask oracle-jdk

print_double_line
echo 'install mamba-forge...'
export CONDA_PREFIX
../install/mamba.sh

print_double_line
echo 'install basher...'
../common/basher.sh

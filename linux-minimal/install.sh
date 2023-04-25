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

print_double_line
echo "Enter your email: "
read email
echo "Generatin ssh key for $email"
ssh-keygen -t ed25519 -C "$email"

print_line
echo "Add the following to your github account in https://github.com/settings/keys"
cat ~/.ssh/id_ed25519.pub
echo "Press enter to continue"
read

print_double_line
echo "Installing dotfiles..."
mkdir -p ~/git/source; cd ~/git/source
git clone git@github.com:ickc/dotfiles.git
cd dotfiles
make uninstall && make install && make

print_double_line
echo "Installing ssh-dir..."
mkdir -p ~/git/private; cd ~/git/private
git clone git@github.com:ickc/ssh-dir.git
cd ssh-dir
mv ~/.ssh/id_ed25519 .ssh/
mv ~/.ssh/id_ed25519.pub .ssh/
rm -rf ~/.ssh
make install

print_double_line
echo "Installing bootstrapping-os-environments..."
mkdir -p ~/git/source
cd ~/git/source
git clone git@github.com:ickc/bootstrapping-os-environments.git

print_double_line
echo "Installing basher..."
cd ~/git/source/bootstrapping-os-environments/install
./basher.sh
print_line
echo "Installing basher packages..."
cd ~/git/source/bootstrapping-os-environments/common
./basher.sh

print_double_line
echo "Installing mambaforge..."
cd ~/git/source/bootstrapping-os-environments/install/
./mamba.sh
. ~/.mambaforge/bin/activate
print_line
echo "Installing system packages using mamba..."
cd ~/git/source/bootstrapping-os-environments/common/conda/
./conda-system.sh

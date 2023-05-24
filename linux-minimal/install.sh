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
print_double_line
if [[ -f ~/.ssh/id_ed25519.pub || -f ~/.ssh/id_rsa.pub ]]; then
    echo "SSH key already exists, assuming ssh-agent is setup to pull from GitHub and skip generating ssh key."
else
    read -p "Enter your email: " email
    echo "Generating ssh key for $email"
    ssh-keygen -t ed25519 -C "$email" || ssh-keygen -t rsa -b 4096 -C "$email"
    eval "$(ssh-agent -s)"
    ssh-add ~/.ssh/id_ed25519 || ssh-add ~/.ssh/id_rsa

    print_line
    echo "Add the following to your github account in https://github.com/settings/keys"
    cat ~/.ssh/id_ed25519.pub || cat ~/.ssh/id_rsa.pub
fi
read -p "Press enter to continue"

print_double_line
echo "Installing dotfiles..."
mkdir -p ~/git/source; cd ~/git/source
git clone git@github.com:ickc/dotfiles.git
cd dotfiles
. "$HOME/git/source/dotfiles/bin/env"
make install && make

print_double_line
echo "Installing ssh-dir..."
mkdir -p ~/git/private; cd ~/git/private
git clone git@github.com:ickc/ssh-dir.git
cd ssh-dir
mv ~/.ssh/id_ed25519 .ssh/ || mv ~/.ssh/id_rsa .ssh/
mv ~/.ssh/id_ed25519.pub .ssh/ || mv ~/.ssh/id_rsa.pub .ssh/
rm -rf ~/.ssh
make install

print_double_line
echo "Installing mambaforge..."
cd ~/git/source/bootstrapping-os-environments/install/
CONDA_PREFIX=~/.mambaforge ./mamba.sh
. ~/.mambaforge/bin/activate
print_line
echo "Installing system packages using mamba..."
cd ~/git/source/bootstrapping-os-environments/common/conda/
./conda-system.sh

print_double_line
echo "Installing basher..."
cd ~/git/source/bootstrapping-os-environments/install
./basher.sh
export PATH="$HOME/.basher/bin:$PATH"
print_line
echo "Installing basher packages..."
cd ~/git/source/bootstrapping-os-environments/common
./basher.sh
}

install

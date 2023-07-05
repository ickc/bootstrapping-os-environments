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

# make sure packages from bootstrap.sh can be seen
export PATH="$HOME/.local/bin:$PATH"
print_double_line
if [[ -f ~/.ssh/id_ed25519.pub || -f ~/.ssh/id_rsa.pub ]]; then
    echo "SSH key already exists, assuming ssh-agent is setup to pull from GitHub and skip generating ssh key."
else
    read -p "Enter your email: " email
    echo "Generating ssh key for $email"
    mkdir -p ~/.ssh
    ssh-keygen -t ed25519 -C "$email" -f ~/.ssh/id_ed25519 || ssh-keygen -t rsa -b 4096 -C "$email" -f ~/.ssh/id_rsa
    eval "$(ssh-agent -s)"
    ssh-add ~/.ssh/id_ed25519 || ssh-add ~/.ssh/id_rsa

    print_line
    echo "Add the following to your github account in https://github.com/settings/keys"
    cat ~/.ssh/id_ed25519.pub || cat ~/.ssh/id_rsa.pub
fi
read -p "Press enter to continue"

print_double_line
echo "Installing bootstrapping-os-envrioments..."
if [[ -d ~/git/source/bootstrapping-os-environments ]]; then
    echo "bootstrapping-os-environments already exists, just in case it points to https, setting url to git@github.com:ickc/bootstrapping-os-environments.git..."
    cd ~/git/source/bootstrapping-os-environments
    git remote set-url origin git@github.com:ickc/bootstrapping-os-environments.git
else
    mkdir -p ~/git/source; cd ~/git/source
    git clone git@github.com:ickc/bootstrapping-os-environments.git
fi

print_double_line
echo "Installing dotfiles..."
mkdir -p ~/git/source; cd ~/git/source
git clone git@github.com:ickc/dotfiles.git
cd dotfiles
. "$HOME/git/source/dotfiles/bin/env"
make install && make

print_double_line
echo "Installing ssh-dir..."
git clone git@github.com:ickc/ssh-dir.git ~/.ssh.temp
cd ~/.ssh.temp
mv ~/.ssh/id_ed25519 ~/.ssh.temp || mv ~/.ssh/id_rsa ~/.ssh.temp
mv ~/.ssh/id_ed25519.pub ~/.ssh.temp || mv ~/.ssh/id_rsa.pub ~/.ssh.temp
rm -rf ~/.ssh
mv ~/.ssh.temp ~/.ssh

print_double_line
echo "Installing basher..."
cd ~/git/source/bootstrapping-os-environments/install
./basher.sh
export PATH="$HOME/.basher/bin:$PATH"
print_line
echo "Installing basher packages..."
cd ~/git/source/bootstrapping-os-environments/common
./basher.sh

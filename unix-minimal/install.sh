#!/usr/bin/env bash

# usuage: BSOS_EMAIL=... ./install.sh

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

if [[ -z "$BSOS_EMAIL" ]]; then
    echo "Error: BSOS_EMAIL environment variable not set. Exiting..."
    exit 1
fi
# determine ssh algorithm to use
if ssh -Q key | grep -q "ssh-ed25519"; then
    SSH_ALGO=ed25519
elif ssh -Q key | grep -q "ssh-rsa"; then
    SSH_ALGO=rsa
else
    echo "No supported ssh algorithm found, exiting..."
    exit 1
fi

print_double_line
if [[ -f "$HOME/.ssh/id_${SSH_ALGO}.pubs" ]]; then
    echo "SSH key already exists, assuming ssh-agent is setup to pull from GitHub and skip generating ssh key."
else
    echo "Generating ssh key for $BSOS_EMAIL"
    mkdir -p "$HOME/.ssh"
    ssh-keygen -t "$SSH_ALGO" -C "$BSOS_EMAIL" -f "$HOME/.ssh/id_${SSH_ALGO}"
    eval "$(ssh-agent -s)"
    ssh-add "$HOME/.ssh/id_${SSH_ALGO}"
fi

# authenticate with GitHub
"$HOME/git/source/bootstrapping-os-environments/install/gh.sh"
gh auth login --git-protocol ssh --web

print_double_line
echo "Installing bootstrapping-os-envrioments..."
if [[ -d "$HOME/git/source/bootstrapping-os-environments" ]]; then
    echo "bootstrapping-os-environments already exists, just in case it points to https, setting url to git@github.com:ickc/bootstrapping-os-environments.git..."
    cd "$HOME/git/source/bootstrapping-os-environments"
    git remote set-url origin git@github.com:ickc/bootstrapping-os-environments.git
else
    mkdir -p "$HOME/git/source;" cd "$HOME/git/source"
    git clone git@github.com:ickc/bootstrapping-os-environments.git
fi

print_double_line
echo "Installing dotfiles..."
mkdir -p "$HOME/git/source;" cd "$HOME/git/source"
git clone git@github.com:ickc/dotfiles.git
cd dotfiles
# shellcheck disable=SC1091
. "$HOME/git/source/dotfiles/bin/env"
make install && make

print_double_line
echo "Installing ssh-dir..."
git clone git@github.com:ickc/ssh-dir.git "$HOME/.ssh.temp"
cd "$HOME/.ssh.temp"
mv "$HOME/.ssh/id_${SSH_ALGO}" "$HOME/.ssh.temp"
mv "$HOME/.ssh/id_${SSH_ALGO}.pub" "$HOME/.ssh.temp"
rm -rf "$HOME/.ssh"
mv "$HOME/.ssh.temp" "$HOME/.ssh"

print_double_line
echo "Installing basher..."
cd "$HOME/git/source/bootstrapping-os-environments/install"
./basher.sh
export PATH="$HOME/.basher/bin:$PATH"
print_line
echo "Installing basher packages..."
cd "$HOME/git/source/bootstrapping-os-environments/common"
./basher.sh

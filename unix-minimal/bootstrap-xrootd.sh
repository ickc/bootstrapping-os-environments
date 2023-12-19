#!/usr/bin/env bash

# download ssh keys ############################################################
XROOTD_ROOT=root://bohr3226.tier2.hep.manchester.ac.uk:1094//dpm/tier2.hep.manchester.ac.uk/home/souk.ac.uk
# to stroage
# gfal-mkdir -p -m 700 "$XROOTD_ROOT/home/$USER/.ssh"
# gfal-copy ~/.ssh/id_ed25519 "$XROOTD_ROOT/home/$USER/.ssh/id_ed25519"
# gfal-copy ~/.ssh/id_ed25519.pub "$XROOTD_ROOT/home/$USER/.ssh/id_ed25519.pub"
# check
# gfal-ls "$XROOTD_ROOT/home/$USER/.ssh"
# from storage
mkdir -p -m 700 ~/.ssh
gfal-copy "$XROOTD_ROOT/home/$USER/.ssh/id_ed25519" ~/.ssh/id_ed25519
chmod 600 ~/.ssh/id_ed25519
gfal-copy "$XROOTD_ROOT/home/$USER/.ssh/id_ed25519.pub" ~/.ssh/id_ed25519.pub
chmod 644 ~/.ssh/id_ed25519.pub
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# git ##########################################################################
git clone git@github.com:ickc/sman.git ~/.sman
git clone https://github.com/basherpm/basher.git ~/.basher

mkdir -p ~/git/source
cd ~/git/source
git clone git@github.com:ickc/dotfiles
git clone git@github.com:ickc/sman-snippets

# install zim ##################################################################

curl -fsSL --create-dirs -o ~/.zim/zimfw.zsh https://github.com/zimfw/zimfw/releases/latest/download/zimfw.zsh

# install sman #################################################################
mkdir -p ~/.local/bin
curl -L https://github.com/ickc/sman/releases/download/v1.0.1/sman-linux-amd64-v1.0.1.tgz | tar -xz -C ~/.local/bin sman-linux-amd64-v1.0.1
mv ~/.local/bin/sman-linux-amd64-v1.0.1 ~/.local/bin/sman

# dotfiles
cd ~/git/source/dotfiles
. bin/env
make

# basher #######################################################################
~/.basher/bin/basher install ickc/dautil-sh

# start zsh ####################################################################
"$CVMFS_ROOT/usr/bin/zsh"

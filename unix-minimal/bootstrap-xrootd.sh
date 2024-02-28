#!/usr/bin/env bash

# git 2.3.0 or later is required
export GIT_SSH_COMMAND="ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no"
# temporary fix of https://github.com/simonsobs-uk/data-centre/issues/47
export HOME="/home/$USER"

# download ssh keys ############################################################
CVMFS_ROOT=/cvmfs/northgrid.gridpp.ac.uk/simonsobservatory
export PATH="$CVMFS_ROOT/usr/bin:$PATH"
XROOTD_ROOT=root://bohr3226.tier2.hep.manchester.ac.uk:1094//dpm/tier2.hep.manchester.ac.uk/home/souk.ac.uk
# to stroage
# gfal-mkdir -p -m 700 "$XROOTD_ROOT/home/$USER/.ssh"
# gfal-copy ~/.ssh/id_ed25519 "$XROOTD_ROOT/home/$USER/.ssh/id_ed25519"
# gfal-copy ~/.ssh/id_ed25519.pub "$XROOTD_ROOT/home/$USER/.ssh/id_ed25519.pub"
# check
# gfal-ls "$XROOTD_ROOT/home/$USER/.ssh"
# from storage
mkdir -p -m 700 ~/.ssh
gfal-copy -r "$XROOTD_ROOT/home/$USER/.ssh" ~/.ssh
find ~/.ssh -type f -exec chmod 600 {} +
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# dotfiles #####################################################################
mkdir -p ~/git/source
cd ~/git/source
git clone git@github.com:ickc/dotfiles
cd ~/git/source/dotfiles
. config/zsh/.zshenv
. config/zsh/.zshrc > /dev/null
make install -j && make -j
. config/zsh/.zshenv
. config/zsh/.zshrc > /dev/null

# start zsh ####################################################################
$CVMFS_ROOT/usr/bin/zsh

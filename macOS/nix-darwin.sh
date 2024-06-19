#!/usr/bin/env bash

# * This is a note, should not be executed as is

# Determinate Systems Nix installer
# https://zero-to-nix.com/start/install
curl --proto '=https' --tlsv1.2 -sSf -L https://install.determinate.systems/nix | sh -s -- install

# source in current section, should not be needed for new sessions
# . /nix/var/nix/profiles/default/etc/profile.d/nix-daemon.sh

# testing
nix --version

# nix-darwin
# https://github.com/LnL7/nix-darwin
mkdir -p ~/.config/nix-darwin
cd ~/.config/nix-darwin
nix flake init -t nix-darwin
# inspect and tailor
# nixpkgs.hostPlatform to aarch64-darwin
# darwinConfigurations."simple"
# e.g.
sed -i -E \
    -e "s/simple/$(scutil --get LocalHostName)/" \
    -e 's/x86_64-darwin/aarch64-darwin/' \
    flake.nix

# check & apply
# nix run nix-darwin -- switch --flake ~/git/source/dotfiles/config/nix-darwin
darwin-rebuild switch --flake ~/git/source/dotfiles/config/nix-darwin

# update
cd ~/git/source/dotfiles/config/nix-darwin
nix flake update

# GC
nix-collect-garbage -d && nix-store --optimise

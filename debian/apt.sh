#!/usr/bin/env bash

set -e

export DEBIAN_FRONTEND=noninteractive

sudo apt-get update -qq
sudo apt -y upgrade

sudo apt install -y software-properties-common
sudo add-apt-repository ppa:team-xbmc/ppa -y
sudo apt-get update -qq

xargs -a <(sed -E 's/^([^# ]*).*$/\1/g' apt.txt) -r -- sudo apt-get install -qq

sudo sensors-detect --auto

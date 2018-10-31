#!/usr/bin/env bash

export DEBIAN_FRONTEND=noninteractive

sudo apt-get update -qq && sudo apt -y full-upgrade

xargs -a <(sed -E 's/^([^# ]*).*$/\1/g' apt.txt) -r -- sudo apt-get install -qq

sudo sensors-detect

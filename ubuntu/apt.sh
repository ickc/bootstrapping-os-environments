#!/usr/bin/env bash

export DEBIAN_FRONTEND=noninteractive

sudo apt-get update -qq && sudo apt -y full-upgrade

grep -v '#' apt.txt | xargs -i bash -c 'sudo apt-get install -qq {}'

sudo sensors-detect

#!/bin/bash

export DEBIAN_FRONTEND=noninteractive

sudo apt-get update -qq && sudo apt -y full-upgrade

grep -v '#' apt.txt | xargs sudo apt-get install -qq

sudo sensors-detect

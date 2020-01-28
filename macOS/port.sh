#!/usr/bin/env bash

# sudo loop
sudo -v
while true; do sudo -n true; sleep 60; kill -0 "$$" || exit; done 2>/dev/null &

grep -v '#' port.txt | xargs sudo port install

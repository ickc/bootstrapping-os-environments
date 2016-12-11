#!/bin/bash

export DEBIAN_FRONTEND=noninteractive

sudo apt-get update -qq && sudo apt -y full-upgrade

sudo apt-get install -qq openssh-server

sudo apt-get install -qq python-pip

sudo apt-get install texlive

sudo apt-get -qq install pandoc

sudo pip install -U pandocfilters

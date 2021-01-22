#!/usr/bin/env bash

set -e

# sudo loop
while true; do sudo -n true; sleep 60; kill -0 "$$" || exit; done 2>/dev/null &

# helpers ##############################################################

print_double_line () {
    eval printf %.0s= '{1..'"${COLUMNS:-$(tput cols)}"\}
}

print_line () {
    eval printf %.0s- '{1..'"${COLUMNS:-$(tput cols)}"\}
}

########################################################################

print_double_line
echo "install bottom..."
../install/bottom.sh

print_double_line
echo "install mamba..."
../install/mamba.sh

print_double_line
echo "install vscode..."
../install/vscode.sh

print_double_line
echo "install windscribe..."
../install/windscribe.sh

print_double_line
echo "install zerotier..."
../install/zerotier.sh

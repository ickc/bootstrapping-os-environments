#!/usr/bin/env bash

set -e

# install prefix
PREFIX="${PREFIX:-"/opt/globusconnectpersonal"}"
URL='https://downloads.globus.org/globus-connect-personal/linux/stable/globusconnectpersonal-latest.tgz'

# helpers ##############################################################

print_double_line () {
    eval printf %.0s= '{1..'"${COLUMNS:-$(tput cols)}"\}
}

print_line () {
    eval printf %.0s- '{1..'"${COLUMNS:-$(tput cols)}"\}
}

mkdir_check_sudo () {
    if [[ -d "$1" ]]; then
        if [[ -w "$1" ]]; then
            # echo "directory exist and writable: $1"
            NEED_SUDO=0
        else
            # echo "directory exist but not writable: $1"
            NEED_SUDO=1
        fi
    else
        mkdir -p "$1" 2> /dev/null || true
        if [[ -d "$1" ]]; then
            # echo "directory not exist and created: $1"
            NEED_SUDO=0
        else
            # echo "directory not exist and not created, retry with sudo: $1"
            sudo mkdir -p "$1"
            NEED_SUDO=1
        fi
    fi
}

########################################################################

mkdir_check_sudo "$PREFIX"
cd "$PREFIX"
if [[ "$NEED_SUDO" == 0 ]]; then
    wget -qO- "$URL" | tar --strip-components=1 -xzf -
else
    wget -qO- "$URL" | sudo tar --strip-components=1 -xzf -
fi

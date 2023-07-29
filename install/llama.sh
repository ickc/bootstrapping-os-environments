#!/usr/bin/env bash

set -e

# location to put git repo
REPO_PREFIX="${REPO_PREFIX:-"$HOME/git/read-only"}"
# install prefix
PREFIX="${PREFIX:-"/opt/llama"}"
# if CLEAN=1 then remove built files
CLEAN="${CLEAN:-1}"

# helpers ##############################################################

print_double_line () {
    eval printf %.0s= '{1..'"${COLUMNS:-$(tput cols)}"\}
}

print_line () {
    eval printf %.0s- '{1..'"${COLUMNS:-$(tput cols)}"\}
}

########################################################################

print_double_line
if [[ -d "$REPO_PREFIX/llama.cpp" ]]; then
    cd "$REPO_PREFIX/llama.cpp"
    echo "Updating existing repo in $REPO_PREFIX/llama.cpp"
    print_line
    git pull
else
    echo "Cloning repo"
    print_line
    mkdir -p "$REPO_PREFIX"
    cd "$REPO_PREFIX"
    git clone git@github.com:ggerganov/llama.cpp.git
    cd llama.cpp
fi

if [[ "$CLEAN" == 1 ]]; then
    print_double_line
    echo "Cleaning build dir"
    print_line
    rm -rf build build-info.h
fi

mkdir -p build
cd build

print_double_line
echo "Running cmake"
print_line
cmake -DLLAMA_METAL=ON --install-prefix "$PREFIX" ..
print_double_line
echo "Building"
print_line
cmake --build . --config Release

print_double_line
echo "Installing"
print_line
make install || sudo make install

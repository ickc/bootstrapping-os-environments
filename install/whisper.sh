#!/usr/bin/env bash

set -e

# location to put git repo
REPO_PREFIX="${REPO_PREFIX:-"$HOME/git/read-only"}"
# install prefix
PREFIX="${PREFIX:-"/opt/whisper"}"
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
if [[ -d "$REPO_PREFIX/whisper.cpp" ]]; then
    cd "$REPO_PREFIX/whisper.cpp"
    echo "Updating existing repo in $REPO_PREFIX/whisper.cpp"
    print_line
    git pull
else
    echo "Cloning repo"
    print_line
    mkdir -p "$REPO_PREFIX"
    cd "$REPO_PREFIX"
    git clone git@github.com:ggerganov/whisper.cpp.git
    cd whisper.cpp
fi

if [[ "$CLEAN" == 1 ]]; then
    print_double_line
    echo "Cleaning build dir"
    print_line
    rm -rf build
fi

mkdir -p build
cd build

print_double_line
echo "Running cmake"
print_line
cmake \
    -DCMAKE_INSTALL_PREFIX="$PREFIX" \
    ..
print_double_line
echo "Building"
print_line
cmake --build . --config Release

print_double_line
echo "Installing"
print_line
make install || sudo make install

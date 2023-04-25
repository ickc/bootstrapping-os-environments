#!/usr/bin/env bash

set -e

# TODO: update from https://zsh.sourceforge.io/Arc/source.html
VERSION=${VERSION:-5.9}
# https://unix.stackexchange.com/a/84980/192799
DOWNLOADDIR="$(mktemp -d 2>/dev/null || mktemp -d -t 'zsh')"
INSTALLDIR=${INSTALLDIR:-"$HOME/.local"}

filename="zsh-$VERSION.tar.xz"
dirname="zsh-$VERSION"
url="https://sourceforge.net/projects/zsh/files/zsh/$VERSION/$filename/download"

cd "$DOWNLOADDIR"

# helpers ##############################################################

print_double_line () {
    eval printf %.0s= '{1..'"${COLUMNS:-$(tput cols)}"\}
}

print_line () {
    eval printf %.0s- '{1..'"${COLUMNS:-$(tput cols)}"\}
}

########################################################################

print_double_line
echo Downloading from $url to temp dir $DOWNLOADDIR
wget -O - "$url" | tar -xJf -

cd "$dirname"

print_double_line
echo Configuring...
./configure --prefix="$INSTALLDIR" \
            --datadir="$INSTALLDIR/share" \
            --enable-maildir-support \
            --with-term-lib='ncursesw' \
            --enable-multibyte \
            --enable-function-subdirs \
            --with-tcsetpgrp \
            --enable-pcre \
            --enable-cap \
            --enable-zsh-secure-free

print_double_line
echo Making...

make

make check

print_double_line
echo Installing...
make install

make install.info

print_line
echo Removing temp dir at $DOWNLOADDIR
rm -rf "$DOWNLOADDIR"

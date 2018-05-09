#!/bin/sh​

VERSION=${VERSION:-5.5.1}
DOWNLOADDIR=${DOWNLOADDIR:-"$HOME/.zsh"}
INSTALLDIR=${INSTALLDIR:-/global/common/software/polar/local}

filename="zsh-$VERSION.tar.xz"
dirname="zsh-$VERSION"
url="https://sourceforge.net/projects/zsh/files/zsh/$VERSION/$filename/download"

mdcd () {
    mkdir -p "$@" && cd "$@"
}

mdcd "$DOWNLOADDIR"

wget -O - "$url" | tar -xJf -

cd "$dirname"

./Util/preconfig

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

make

make check

make install

make install.info

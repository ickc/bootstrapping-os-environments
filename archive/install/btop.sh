#!/usr/bin/env bash

set -e

PREFIX="${PREFIX:-${HOME}/.local}"
DOWNLOADDIR="$(mktemp -d 2> /dev/null || mktemp -d -t 'zsh')"

# helpers ##############################################################

print_double_line() {
    eval printf %.0s= '{1..'"${COLUMNS:-$(tput cols)}"\}
}

print_line() {
    eval printf %.0s- '{1..'"${COLUMNS:-$(tput cols)}"\}
}

########################################################################

ARCH=$(uname -m)
OS=$(uname -s)

case "${OS}" in
    Linux)
        case "${ARCH}" in
            aarch64)
                filename="btop-aarch64-linux-musl.tbz"
                ;;
            armv7l)
                filename="btop-armv7l-linux-musleabihf.tbz"
                ;;
            arm)
                filename="btop-arm-linux-musleabi.tbz"
                ;;
            i486)
                filename="btop-i486-linux-musl.tbz"
                ;;
            i686)
                filename="btop-i686-linux-musl.tbz"
                ;;
            powerpc64le)
                filename="btop-powerpc64-linux-musl.tbz"
                ;;
            mips64)
                filename="btop-mips64-linux-musl.tbz"
                ;;
            x86_64)
                filename="btop-x86_64-linux-musl.tbz"
                ;;
            *)
                echo "Unsupported architecture: ${ARCH}"
                exit 1
                ;;
        esac
        ;;
    *)
        echo "Unsupported OS: ${OS}"
        exit 1
        ;;
esac

downloadUrl="https://github.com/aristocratos/btop/releases/latest/download/${filename}"

print_double_line
echo Downloading to temp dir "${DOWNLOADDIR}"
cd "${DOWNLOADDIR}"
wget -qO- "${downloadUrl}" | tar -xjf -

print_double_line
echo Installing...
cd btop
export PREFIX
make install

print_line
echo Removing temp dir "${DOWNLOADDIR}"
rm -rf "${DOWNLOADDIR}"

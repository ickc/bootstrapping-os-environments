#!/usr/bin/env bash

set -e

PREFIX="${PREFIX:-${HOME}/.local}"
# https://unix.stackexchange.com/a/84980/192799
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
    Darwin)
        case "${ARCH}" in
            arm64)
                filename="bottom_aarch64-apple-darwin.tar.gz"
                ;;
            x86_64)
                filename="bottom_x86_64-apple-darwin.tar.gz"
                ;;
            *)
                echo "Unsupported architecture: ${ARCH}"
                exit 1
                ;;
        esac
        ;;
    Linux)
        case "${ARCH}" in
            aarch64)
                filename="bottom_aarch64-unknown-linux-gnu.tar.gz"
                ;;
            armv7l)
                filename="bottom_armv7-unknown-linux-gnueabihf.tar.gz"
                ;;
            i686)
                filename="bottom_i686-unknown-linux-gnu.tar.gz"
                ;;
            powerpc64le)
                filename="bottom_powerpc64le-unknown-linux-gnu.tar.gz"
                ;;
            riscv64)
                filename="bottom_riscv64gc-unknown-linux-gnu.tar.gz"
                ;;
            x86_64)
                filename="bottom_x86_64-unknown-linux-gnu.tar.gz"
                ;;
            *)
                echo "Unsupported architecture: ${ARCH}"
                exit 1
                ;;
        esac
        ;;
    FreeBSD)
        case "${ARCH}" in
            x86_64)
                filename="bottom_x86_64-unknown-freebsd-$(uname -r | cut -d- -f1).tar.gz"
                ;;
            *)
                echo "Unsupported architecture: ${ARCH}"
                exit 1
                ;;
        esac
        ;;
    MINGW* | CYGWIN* | MSYS*)
        case "${ARCH}" in
            i686)
                filename="bottom_i686-pc-windows-msvc.zip"
                ;;
            x86_64)
                filename="bottom_x86_64-pc-windows-msvc.zip"
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

downloadUrl="https://github.com/ClementTsang/bottom/releases/latest/download/${filename}"

print_double_line
echo Downloading to temp dir "${DOWNLOADDIR}"
cd "${DOWNLOADDIR}"
wget -qO- "${downloadUrl}" | tar -xzf -

print_double_line
echo Installing...
mkdir -p "${PREFIX}/bin"
mv btm "${PREFIX}/bin"

print_line
echo Removing temp dir "${DOWNLOADDIR}"
rm -rf "${DOWNLOADDIR}"

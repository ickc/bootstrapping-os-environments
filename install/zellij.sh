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
    Darwin)
        case "${ARCH}" in
            arm64)
                filename="zellij-aarch64-apple-darwin.tar.gz"
                ;;
            x86_64)
                filename="zellij-x86_64-apple-darwin.tar.gz"
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
                filename="zellij-aarch64-unknown-linux-musl.tar.gz"
                ;;
            x86_64)
                filename="zellij-x86_64-unknown-linux-musl.tar.gz"
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

downloadUrl="https://github.com/zellij-org/zellij/releases/latest/download/${filename}"

print_double_line
echo Downloading to temp dir "${DOWNLOADDIR}"
cd "${DOWNLOADDIR}"
wget -qO- "${downloadUrl}" | tar -xzf -

print_double_line
echo Installing...
mkdir -p "${PREFIX}/bin"
mv zellij "${PREFIX}/bin"

print_line
echo Removing temp dir "${DOWNLOADDIR}"
rm -rf "${DOWNLOADDIR}"

#!/usr/bin/env bash

set -e

PREFIX=${PREFIX:-${HOME}/.local}

base_url=https://github.com/fastfetch-cli/fastfetch/releases/latest/download/

os=$(uname -s)
arch=$(uname -m)

# Determine the correct asset based on the system architecture and OS
case "${os}" in
    Linux)
        case "${arch}" in
            x86_64)
                file="fastfetch-linux-amd64.tar.gz"
                ;;
            aarch64)
                file="fastfetch-linux-aarch64.tar.gz"
                ;;
            armv7l)
                file="fastfetch-linux-armv7l.tar.gz"
                ;;
            *)
                echo "Unsupported architecture: ${arch}"
                exit 1
                ;;
        esac
        ;;
    Darwin)
        file="fastfetch-macos-universal.tar.gz"
        ;;
    FreeBSD)
        case "${arch}" in
            amd64)
                file="fastfetch-freebsd-amd64.tar.gz"
                ;;
            aarch64)
                file="fastfetch-freebsd-aarch64.tar.gz"
                ;;
            *)
                echo "Unsupported architecture: ${arch}"
                exit 1
                ;;
        esac
        ;;
    *)
        echo "Unsupported OS: ${os}"
        exit 1
        ;;
esac

# Full URL for the chosen asset
url="${base_url}/${file}"

mkdir -p "${PREFIX}"
# shellcheck disable=SC2312
wget -qO- "${url}" | tar -xzf - -C "${PREFIX}" --strip-components=2

echo "Fastfetch has been installed to ${PREFIX}"

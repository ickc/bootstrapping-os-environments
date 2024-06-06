#!/usr/bin/env bash

set -e

PREFIX=${PREFIX:-${HOME}/.local}

# Function to download and install devtunnel
install_devtunnel() {
    local url=$1
    local dest="${PREFIX}/bin/devtunnel"

    echo "Downloading from ${url}..."
    mkdir -p "${PREFIX}/bin"

    if [[ ${url} == *-zip ]]; then
        # shellcheck disable=SC2312
        curl -L "${url}" -o devtunnel.zip
        unzip -o devtunnel.zip -d "${PREFIX}/bin"
        rm -f devtunnel.zip
    else
        curl -L "${url}" -o "${dest}"
    fi

    chmod +x "${dest}"
    echo "devtunnel has been installed to ${dest}"
}

# Detect OS and architecture
OS=$(uname -s)
ARCH=$(uname -m)

case "${OS}" in
    Darwin)
        case "${ARCH}" in
            arm64)
                install_devtunnel "https://aka.ms/TunnelsCliDownload/osx-arm64-zip"
                ;;
            x86_64)
                install_devtunnel "https://aka.ms/TunnelsCliDownload/osx-x64-zip"
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
                install_devtunnel "https://aka.ms/TunnelsCliDownload/linux-arm64"
                ;;
            x86_64)
                install_devtunnel "https://aka.ms/TunnelsCliDownload/linux-x64"
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

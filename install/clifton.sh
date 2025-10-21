#!/usr/bin/env bash

set -e

PREFIX="${PREFIX:-${HOME}/.local}"
USE_MUSL="${USE_MUSL:-0}"
# create tempdir in a portable way
DOWNLOADDIR="$(mktemp -d 2> /dev/null || mktemp -d -t 'clifton')"

# helpers ##############################################################

print_double_line() {
    eval printf %.0s= '{1..'"${COLUMNS:-$(tput cols 2>/dev/null || echo 80)}"\}
    printf "\n"
}

print_line() {
    eval printf %.0s- '{1..'"${COLUMNS:-$(tput cols 2>/dev/null || echo 80)}"\}
    printf "\n"
}

########################################################################

# shellcheck disable=SC2312
read -r OS ARCH <<< "$(uname -sm)"

case "${OS}" in
    Darwin)
        case "${ARCH}" in
            arm64)
                filename="clifton-macos-aarch64"
                ;;
            x86_64)
                filename="clifton-macos-x86_64"
                ;;
            *)
                echo "Unsupported architecture on macOS: ${ARCH}"
                exit 1
                ;;
        esac
        ;;
    Linux)
        case "${ARCH}" in
            aarch64)
                if [[ ${USE_MUSL} == 1 ]]; then
                    filename="clifton-linux-musl-aarch64"
                else
                    filename="clifton-linux-aarch64"
                fi
                ;;
            x86_64)
                if [[ ${USE_MUSL} == 1 ]]; then
                    filename="clifton-linux-musl-x86_64"
                else
                    filename="clifton-linux-x86_64"
                fi
                ;;
            *)
                echo "Unsupported architecture on Linux: ${ARCH}"
                exit 1
                ;;
        esac
        ;;
    *)
        echo "Unsupported OS: ${OS}"
        exit 1
        ;;
esac

downloadUrl="https://github.com/isambard-sc/clifton/releases/latest/download/${filename}"

print_double_line
echo "Downloading ${filename} to temp dir: ${DOWNLOADDIR}"
cd "${DOWNLOADDIR}"

# Prefer wget, fallback to curl
if command -v wget >/dev/null 2>&1; then
    wget -q -O "${filename}" "${downloadUrl}"
elif command -v curl >/dev/null 2>&1; then
    curl -sSL -o "${filename}" "${downloadUrl}"
else
    echo "Error: please install wget or curl to download files."
    exit 1
fi

if [ ! -s "${filename}" ]; then
    echo "Download failed or produced empty file: ${filename}"
    exit 1
fi

print_double_line
echo "Installing..."
mkdir -p "${PREFIX}/bin"

# Ensure executable and move to bin as `clifton`
chmod +x "${filename}"
mv -f "${filename}" "${PREFIX}/bin/clifton"

print_line
echo "Installed clifton to ${PREFIX}/bin/clifton"

print_line
echo "Removing temp dir ${DOWNLOADDIR}"
rm -rf "${DOWNLOADDIR}"

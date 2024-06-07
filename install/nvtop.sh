#!/usr/bin/env bash

set -e

PREFIX="${PREFIX:-${HOME}/.local}"
IMAGEDIR="${IMAGEDIR:-${HOME}/.local/share/applications}"

repo=Syllo/nvtop
filename=nvtop-x86_64.AppImage
downloadUrl="https://github.com/${repo}/releases/latest/download/${filename}"

# helpers ##############################################################

print_double_line() {
    eval printf %.0s= '{1..'"${COLUMNS:-$(tput cols)}"\}
}

print_line() {
    eval printf %.0s- '{1..'"${COLUMNS:-$(tput cols)}"\}
}

########################################################################

print_double_line
echo "Downloading nvtop from ${downloadUrl}"
mkdir -p "${IMAGEDIR}/nvtop"
cd "${IMAGEDIR}/nvtop"
wget "${downloadUrl}"

print_double_line
echo "Extracting nvtop to ${IMAGEDIR}/nvtop"
chmod +x "${filename}"
"./${filename}" --appimage-extract
rm -f "${filename}"

print_double_line
echo "Creating a symbolic link to ${IMAGEDIR}/nvtop/squashfs-root/usr/bin/nvtop"
mkdir -p "${PREFIX}/bin"
ln -sf "${IMAGEDIR}/nvtop/squashfs-root/usr/bin/nvtop" "${PREFIX}/bin/nvtop"

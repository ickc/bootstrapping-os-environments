#!/usr/bin/env bash

set -e

PREFIX="${PREFIX:-${HOME}/.local}"

repo=Syllo/nvtop
filename=nvtop-x86_64.AppImage
downloadUrl="https://github.com/${repo}/releases/latest/download/${filename}"

mkdir -p "${PREFIX}/bin"
echo "wget ${downloadUrl} -O ${PREFIX}/bin/nvtop"
wget "${downloadUrl}" -O "${PREFIX}/bin/nvtop"

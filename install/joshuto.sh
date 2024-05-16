#!/usr/bin/env bash

set -e

PREFIX="${PREFIX:-$HOME/.local}"

REPO_URL="https://github.com/kamiyaa/joshuto/releases"
# e.g. /kamiyaa/joshuto/releases/tag/v0.9.6
LATEST_RELEASE_URL="$(curl -s "$REPO_URL" | grep -oP '/kamiyaa/joshuto/releases/tag/v[^"]+' | head -1)"
# e.g. v0.9.6
LATEST_VERSION="$(echo "$LATEST_RELEASE_URL" | grep -oP '[^/]+$')"

LATEST_DOWNLOAD_URL="https://github.com/kamiyaa/joshuto/releases/download/${LATEST_VERSION}/joshuto-${LATEST_VERSION}-x86_64-unknown-linux-musl.tar.gz"

echo "Downloading $LATEST_DOWNLOAD_URL"
wget -qO- "$LATEST_DOWNLOAD_URL" | tar xz -C "$PREFIX/bin" --strip-components=1

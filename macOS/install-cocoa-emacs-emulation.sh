#!/usr/bin/env bash

TARGETDIR="$HOME/Library/KeyBindings/"

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

mkdir -p "$TARGETDIR" &&
cp "$DIR/DefaultKeyBinding.dict" "$TARGETDIR"

#!/usr/bin/env bash

# https://web.archive.org/web/20220608191954/http://www.hcs.harvard.edu/~jrus/site/cocoa-text.html

TARGETDIR="$HOME/Library/KeyBindings/"

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

mkdir -p "$TARGETDIR" &&
    cp "$DIR/DefaultKeyBinding.dict" "$TARGETDIR"

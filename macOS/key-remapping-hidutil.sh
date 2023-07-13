#!/usr/bin/env bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# modify from https://apple.stackexchange.com/a/398797/355318
# also see https://developer.apple.com/library/archive/technotes/tn2450/_index.html
# this maps the Application key used in Windows to the Right Alt key used in macOS
cp -f "$DIR/com.local.KeyRemapping.plist" "$HOME/Library/LaunchAgents/"

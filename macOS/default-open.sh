#!/usr/bin/env bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# https://github.com/mathiasbynens/dotfiles/issues/458
for ext in toml dict; do
    defaults write ~/Library/Preferences/com.apple.LaunchServices/com.apple.launchservices.secure.plist LSHandlers -array-add \
    "{
        LSHandlerContentTag = ${ext};
        LSHandlerContentTagClass = 'public.filename-extension';
        LSHandlerPreferredVersions =             {
            LSHandlerRoleAll = '-';
        };
        LSHandlerRoleAll = 'com.microsoft.vscode';
    }"
    done

# https://apple.stackexchange.com/a/123954
duti < "$DIR/default-open.tsv"

#!/usr/bin/env bash

set -e

PREFIX="${PREFIX:-$HOME/.local}"

# helpers ##############################################################

print_double_line() {
    eval printf %.0s= '{1..'"${COLUMNS:-$(tput cols)}"\}
}

print_line() {
    eval printf %.0s- '{1..'"${COLUMNS:-$(tput cols)}"\}
}

########################################################################

install() {
    # https://unix.stackexchange.com/a/84980/192799
    DOWNLOADDIR="$(mktemp -d 2> /dev/null || mktemp -d -t 'zsh')"

    version="$(curl --silent "https://api.github.com/repos/cli/cli/releases/latest" | grep '"tag_name":' | sed -E 's/.*"v([^"]+)".*/\1/')"
    print_double_line
    echo "Installing gh version $version"

    case "$(uname -s)" in
        Linux*)
            OS=Linux
            case "$(uname -m)" in
                x86_64)
                    downloadUrl="https://github.com/cli/cli/releases/download/v${version}/gh_${version}_linux_amd64.tar.gz"
                    ;;
                i*86)
                    downloadUrl="https://github.com/cli/cli/releases/download/v${version}/gh_${version}_linux_386.tar.gz"
                    ;;
                armv*l)
                    downloadUrl="https://github.com/cli/cli/releases/download/v${version}/gh_${version}_linux_armv6.tar.gz"
                    ;;
                aarch64)
                    downloadUrl="https://github.com/cli/cli/releases/download/v${version}/gh_${version}_linux_arm64.tar.gz"
                    ;;
                *)
                    echo "Unsupported CPU architecture: $(uname -m)"
                    exit 1
                    ;;
            esac
            ;;
        Darwin*)
            OS=Darwin
            case "$(uname -m)" in
                arm64)
                    downloadUrl="https://github.com/cli/cli/releases/download/v${version}/gh_${version}_macOS_arm64.zip"
                    ;;
                x86_64)
                    downloadUrl="https://github.com/cli/cli/releases/download/v${version}/gh_${version}_macOS_amd64.zip"
                    ;;
                *)
                    echo "Unsupported CPU architecture: $(uname -m)"
                    exit 1
                    ;;
            esac
            ;;
        *)
            echo "Unsupported operating system: $(uname -s)"
            exit 1
            ;;
    esac

    filename="${downloadUrl##*/}"
    if [[ $OS == Linux ]]; then
        stem="${filename%.tar.gz}"
    else
        stem="${filename%.zip}"
    fi

    print_double_line
    echo "Downloading $downloadUrl to temp dir $DOWNLOADDIR"
    cd "$DOWNLOADDIR"
    if [[ $OS == Linux ]]; then
        curl -L "$downloadUrl" -o gh.tar.gz
        tar -xf gh.tar.gz
    else
        curl -L "$downloadUrl" -o gh.zip
        unzip gh.zip
    fi
    cd "$stem"

    print_double_line
    echo Installing to "$PREFIX"
    mkdir -p "$PREFIX/bin"
    mv bin/gh "$PREFIX/bin"
    mkdir -p "$PREFIX/share/man/man1"
    mv "share/man/man1"/* "$PREFIX/share/man/man1"

    print_double_line
    echo Removing temp dir "$DOWNLOADDIR"
    rm -rf "$DOWNLOADDIR"
}

install

VERSION=1.0.4
BINDIR="${__OPT_ROOT}/bin"

# shellcheck disable=SC2312
read -r __OSTYPE __ARCH <<< "$(uname -sm)"

sman_install_bin() {
    case "${__OSTYPE}-${__ARCH}" in
        Darwin-arm64) GO_UNAME=darwin-arm64 ;;
        Darwin-x86_64) GO_UNAME=darwin-amd64 ;;
        Linux-x86_64) GO_UNAME=linux-amd64 ;;
        Linux-aarch64) GO_UNAME=linux-arm64 ;;
        Linux-ppc64le) GO_UNAME=linux-ppc64le ;;
        FreeBSD-amd64) GO_UNAME=freebsd-amd64 ;;
        *) exit 1 ;;
    esac
    filename="sman-${GO_UNAME}-v${VERSION}"
    url="https://github.com/ickc/sman/releases/download/v${VERSION}/${filename}.tgz"

    if command -v curl > /dev/null; then
        # shellcheck disable=SC2312
        curl -fL "${url}" | tar -xz
    elif command -v wget > /dev/null; then
        # shellcheck disable=SC2312
        wget -O - "${url}" | tar -xz
    fi
    mkdir -p "${BINDIR}"
    mv "${filename}" "${BINDIR}/sman"
}

sman_install_rc() {
    mkdir -p "${XDG_CONFIG_HOME}/zsh/functions"
    github_download_file_to ickc sman master sman.rc "${XDG_CONFIG_HOME}/zsh/functions/sman.rc"
}

sman_install_snippets() {
    if [[ -d ~/git/source/sman-snippets ]]; then
        cd ~/git/source/sman-snippets
        git pull
    else
        mkdir -p ~/git/source
        cd ~/git/source
        github_clone_git ickc sman-snippets
    fi
}

sman_install() {
    sman_install_bin
    sman_install_rc
    sman_install_snippets
}

sman_uninstall() {
    rm -f "${BINDIR}/sman" "${XDG_CONFIG_HOME}/zsh/functions/sman.rc"
    rm -rf ~/git/source/sman-snippets
}

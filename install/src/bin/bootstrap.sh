#!/usr/bin/env bash

set -eo pipefail

__MAMBA_ENV_DOWNLOAD=1

source ../lib/util/git.sh
# source ../lib/dotfiles.sh

download_dotfiles() {
    echo 'Temporarily downloading dotfiles'
    github_download_file_to ickc dotfiles main home/.zshenv ~/.zshenv
    github_download_file_to ickc dotfiles main home/.zshrc ~/.zshrc
}

download_dotfiles
# shellcheck disable=SC1090
. ~/.zshenv || true
# shellcheck disable=SC1090
. ~/.zshrc || true
# this must be after sourcing dotfiles
source ../../../env.sh
source ../lib/util/helpers.sh
source ../lib/util/ssh.sh
source ../lib/code.sh
source ../lib/mamba.sh
source ../lib/mamba-env.sh
source ../lib/sman.sh
source ../lib/zim.sh

main() {

    # print_double_line
    # echo 'Installing dotfiles'
    # dotfiles_install
    # # shellcheck disable=SC1090
    # . ~/.bashrc || true

    print_double_line
    echo 'Installing VSCode CLI'
    code_install
    print_double_line
    echo "Installing mamba to ${MAMBA_ROOT_PREFIX}"
    mamba_install
    # shellcheck disable=SC1090
    # . ~/.bashrc || true

    print_double_line
    echo 'Installing system environment via mamba'
    mamba_env_install
    print_double_line
    echo 'Installing zim'
    zim_install

    # shellcheck disable=SC1090
    . ~/.zshrc || true

    print_double_line
    echo 'Generating SSH key and login to GitHub'
    ssh_keygen_and_login

    mkdir -p ~/git/source
    cd ~/git/source
    if [[ ! -d ~/git/source/dotfiles ]]; then
        print_double_line
        echo 'Cloning dotfiles'
        github_clone_git ickc dotfiles
    fi
    cd dotfiles
    print_double_line
    echo 'Installing dotfiles'
    # this will overwrite ~/.zshenv
    make all

    # this clone sman-snippets so it must be after ssh_keygen_and_login
    # sman and envoy also touches ${XDG_CONFIG_HOME}/zsh/functions so must be after dotfiles
    print_double_line
    echo 'Installing sman'
    sman_install

    mkdir -p ~/git/source
    cd ~/git/source
    if [[ ! -d ~/git/source/envoy ]]; then
        print_double_line
        echo 'Cloning envoy'
        github_clone_git ickc envoy
    fi
    envoy/completion/generate.sh

    print_double_line
    echo 'Installing to ~/.ssh'
    ssh_dir_install
}

main

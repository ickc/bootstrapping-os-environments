#!/usr/bin/env bash

XDG_CONFIG_HOME="${XDG_CONFIG_HOME:-"${HOME}/.config"}"
_ZSH_DIR="${XDG_CONFIG_HOME}/zsh/functions"

XDG_DATA_HOME="${XDG_DATA_HOME:-"${HOME}/.local/share"}"
BASH_COMPLETION_USER_DIR="${BASH_COMPLETION_USER_DIR:-"${XDG_DATA_HOME}/bash-completion"}"
_BASH_DIR="${BASH_COMPLETION_USER_DIR}/completions"

mkdir -p "${_BASH_DIR}"
mkdir -p "${_ZSH_DIR}"

bat --completion bash > "${_BASH_DIR}/_bat"
bat --completion zsh > "${_ZSH_DIR}/_bat"
gh completion -s bash > "${_BASH_DIR}/_gh"
gh completion -s zsh > "${_ZSH_DIR}/_gh"
pandoc --bash-completion > "${_BASH_DIR}/_pandoc"
pixi completion --shell bash > "${_BASH_DIR}/_pixi"
pixi completion --shell zsh > "${_ZSH_DIR}/_pixi"
starship completions bash > "${_BASH_DIR}/_starship"
starship completions zsh > "${_ZSH_DIR}/_starship"
zellij setup --generate-completion bash > "${_BASH_DIR}/_zellij"
zellij setup --generate-completion zsh > "${_ZSH_DIR}/_zellij"

echo "Completions generated in ${_BASH_DIR} and ${_ZSH_DIR}"

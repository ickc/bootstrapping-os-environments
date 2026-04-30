auto_ssh_agent() {
    # modified from https://github.com/zimfw/ssh/blob/master/init.zsh

    # Check if ssh-agent is already running
    ssh-add -l &> /dev/null
    if [[ $? -eq 2 ]]; then
        # Unable to contact the authentication agent

        # Load stored agent connection info
        ssh_env="${HOME}/.ssh-agent"
        if [[ ! -r ${ssh_env} ]]; then
            # Start agent and store agent connection info
            (
                umask 066
                ssh-agent > "${ssh_env}"
            )
        fi
        # shellcheck disable=SC1090
        . "${ssh_env}" > /dev/null

        # there's a chance that the stored process has been killed
        ssh-add -l &> /dev/null
        if [[ $? -eq 2 ]]; then
            # generate a new one
            (
                umask 066
                ssh-agent > "${ssh_env}"
            )
            # shellcheck disable=SC1090
            . "${ssh_env}" > /dev/null
        fi
    fi
    # Load identities
    ssh-add -l &> /dev/null
    if [[ $? -eq 1 ]]; then
        ssh-add 2> /dev/null
    fi
}

path_prepend() {
    if [[ -d $1 ]]; then
        case ":${PATH}:" in
            *":$1:"*) : ;;
            *) export PATH="${1}${PATH:+:${PATH}}" ;;
        esac
    fi
}

# variants of the above with $1 as the prefix only
# modifies PATH, MANPATH, INFOPATH
path_prepend_all() {
    if [[ -d "$1/bin" ]]; then
        case ":${PATH}:" in
            *":$1/bin:"*) : ;;
            *) export PATH="${1}/bin${PATH:+:${PATH}}" ;;
        esac
    fi
    if [[ -d "$1/share/man" ]]; then
        case ":${MANPATH}:" in
            *":$1/share/man:"*) : ;;
            *) export MANPATH="${1}/share/man${MANPATH:+:${MANPATH}}" ;;
        esac
    fi
    if [[ -d "$1/share/info" ]]; then
        case ":${INFOPATH}:" in
            *":$1/share/info:"*) : ;;
            *) export INFOPATH="${1}/share/info${INFOPATH:+:${INFOPATH}}" ;;
        esac
    fi
}

conda_envs_path_prepend() {
    if [[ -d $1 ]]; then
        case ":${CONDA_ENVS_PATH}:" in
            *":$1:"*) : ;;
            *) export CONDA_ENVS_PATH="${1}${CONDA_ENVS_PATH:+:${CONDA_ENVS_PATH}}" ;;
        esac
    fi
}

# just put conda and mamba in the PATH
path_prepend "${MAMBA_ROOT_PREFIX}/condabin"
path_prepend_all "${__OPT_ROOT}/system"
path_prepend_all "${__OPT_ROOT}"

if command -v mamba > /dev/null 2>&1; then
    # * this source the conda functions but not changing the PATH directly
    # it allows you to put the conda function available without letting it
    # changing your PATH
    __SAVED_PATH__="${PATH}"
    # shellcheck disable=SC1091,SC2312
    . <(mamba shell hook --shell zsh)
    export PATH="${__SAVED_PATH__}"
    unset __SAVED_PATH__
fi

conda_envs_path_prepend "${XDG_DATA_HOME}/conda/envs"
conda_envs_path_prepend "${__OPT_ROOT}"

command -v direnv > /dev/null 2>&1 && eval "$(direnv hook zsh)"
command -v starship > /dev/null 2>&1 && eval "$(starship init zsh)"
command -v fzf > /dev/null 2>&1 && eval "$(fzf --zsh)"
command -v ssh-agent > /dev/null 2>&1 && auto_ssh_agent

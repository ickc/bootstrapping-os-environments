# detect arch
read -r __OSTYPE __ARCH <<< "$(uname -sm)"
export __OSTYPE __ARCH

# __LOCAL_ROOT <- arch-indep software prefix
export __LOCAL_ROOT="${HOME}/.local"
# __OPT_ROOT <- arch-dep software prefix
export __OPT_ROOT="${__LOCAL_ROOT}/opt/${__OSTYPE}-${__ARCH}";

export XDG_CONFIG_HOME="${HOME}/.config"
export XDG_DATA_HOME="${__LOCAL_ROOT}/share"

export MAMBA_ROOT_PREFIX="${__OPT_ROOT}/miniforge3"
export MAMBA_EXE="${MAMBA_ROOT_PREFIX}/condabin/mamba"
export PIXI_HOME="${PIXI_HOME:-${__OPT_ROOT}/pixi}"

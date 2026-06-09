# Fish shell library: envoy installer path detection.
# Source from fish startup to set envoy-managed paths.
# Respects pre-existing values; dotfiles may set __APPDIR, XDG vars, etc. first.
#
# GENERATED from bsos.installers._env - do not edit. Regenerate with:
#   pixi run generate-env-fish

# Platform detection (always re-detected - pure platform facts)
set -l __envoy_uname (uname -sm | string split ' ')
set -gx __OSTYPE $__envoy_uname[1]
set -gx __ARCH $__envoy_uname[2]

# Path derivation (respects __APPDIR if pre-set by dotfiles)
if not set -q __LOCAL_ROOT; or test -z "$__LOCAL_ROOT"
    if set -q __APPDIR; and test -n "$__APPDIR"
        set -gx __LOCAL_ROOT "$__APPDIR/local"
    else
        set -gx __LOCAL_ROOT "$HOME/.local"
    end
else
    set -gx __LOCAL_ROOT "$__LOCAL_ROOT"
end

if not set -q __OPT_ROOT; or test -z "$__OPT_ROOT"
    set -gx __OPT_ROOT "$__LOCAL_ROOT/opt/$__OSTYPE-$__ARCH"
else
    set -gx __OPT_ROOT "$__OPT_ROOT"
end

# Tool paths
if not set -q MAMBA_ROOT_PREFIX; or test -z "$MAMBA_ROOT_PREFIX"
    set -gx MAMBA_ROOT_PREFIX "$__OPT_ROOT/micromamba"
else
    set -gx MAMBA_ROOT_PREFIX "$MAMBA_ROOT_PREFIX"
end

if not set -q PIXI_HOME; or test -z "$PIXI_HOME"
    set -gx PIXI_HOME "$__OPT_ROOT/pixi"
else
    set -gx PIXI_HOME "$PIXI_HOME"
end

if not set -q ZIM_HOME; or test -z "$ZIM_HOME"
    set -gx ZIM_HOME "$HOME/.zim"
else
    set -gx ZIM_HOME "$ZIM_HOME"
end

if not set -q __LMOD_INIT; or test -z "$__LMOD_INIT"
    set -gx __LMOD_INIT "$__OPT_ROOT/system/lmod/lmod/init"
else
    set -gx __LMOD_INIT "$__LMOD_INIT"
end

# XDG base dirs
if not set -q XDG_CONFIG_HOME; or test -z "$XDG_CONFIG_HOME"
    set -gx XDG_CONFIG_HOME "$HOME/.config"
else
    set -gx XDG_CONFIG_HOME "$XDG_CONFIG_HOME"
end

if not set -q XDG_DATA_HOME; or test -z "$XDG_DATA_HOME"
    set -gx XDG_DATA_HOME "$__LOCAL_ROOT/share"
else
    set -gx XDG_DATA_HOME "$XDG_DATA_HOME"
end

if not set -q XDG_STATE_HOME; or test -z "$XDG_STATE_HOME"
    set -gx XDG_STATE_HOME "$__LOCAL_ROOT/state"
else
    set -gx XDG_STATE_HOME "$XDG_STATE_HOME"
end

if not set -q XDG_CACHE_HOME; or test -z "$XDG_CACHE_HOME"
    set -gx XDG_CACHE_HOME "$HOME/.cache"
else
    set -gx XDG_CACHE_HOME "$XDG_CACHE_HOME"
end

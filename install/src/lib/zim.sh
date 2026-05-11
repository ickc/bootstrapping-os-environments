zim_install() {
    curl -fsSL --create-dirs -o "${ZIM_HOME}/zimfw.zsh" https://github.com/zimfw/zimfw/releases/latest/download/zimfw.zsh
}

zim_uninstall() {
    rm -rf "${ZIM_HOME}"
}

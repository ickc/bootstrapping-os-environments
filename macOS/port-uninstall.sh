#!/usr/bin/env bash

# https://guide.macports.org/chunked/installing.macports.uninstalling.html#installing.macports.uninstalling.users

# helpers ##############################################################

startsudo() {
    sudo -v
    (while true; do
        sudo -v
        /bin/sleep 50
    done) &
    SUDO_PID="$!"
    trap stopsudo SIGINT SIGTERM
}
stopsudo() {
    kill "${SUDO_PID}"
    trap - SIGINT SIGTERM
    sudo -k
}

print_double_line() {
    eval printf %.0s= '{1..'"${COLUMNS:-$(tput cols)}"\}
}

print_line() {
    eval printf %.0s- '{1..'"${COLUMNS:-$(tput cols)}"\}
}

########################################################################

startsudo

print_double_line
echo 'Uninstall All Ports'
sudo port -fp uninstall installed

print_line
echo 'Remove Users and Groups'
sudo dscl . -delete /Users/macports
sudo dscl . -delete /Groups/macports

print_line
echo 'Remove the Rest of MacPorts'
sudo rm -rf \
    /opt/local \
    /Applications/DarwinPorts \
    /Applications/MacPorts \
    /Library/LaunchDaemons/org.macports.* \
    /Library/Receipts/DarwinPorts*.pkg \
    /Library/Receipts/MacPorts*.pkg \
    /Library/StartupItems/DarwinPortsStartup \
    /Library/Tcl/darwinports1.0 \
    /Library/Tcl/macports1.0 \
    ~/.macports

stopsudo

#!/usr/bin/env bash

set -e

# sudo loop
while true; do
    sudo -n true
    sleep 60
    kill -0 "$$" || exit
done 2> /dev/null &

# helpers ##############################################################

print_double_line() {
    eval printf %.0s= '{1..'"${COLUMNS:-$(tput cols)}"\}
}

print_line() {
    eval printf %.0s- '{1..'"${COLUMNS:-$(tput cols)}"\}
}

########################################################################

print_double_line
echo "Setting samba..."
sudo smbpasswd -a "$USER"
sudo smbpasswd -e "$USER"
# https://unix.stackexchange.com/a/562993
sudo setsebool -P samba_export_all_ro=1 samba_export_all_rw=1
sudo systemctl enable --now {smb,nmb}

print_double_line
echo "Changing shell to zsh..."
chsh -s $(which zsh)

# updatedb is causing a lot of activity
# see https://unix.stackexchange.com/a/113681
print_double_line
echo "Removing mlocate..."
sudo yum remove mlocate -y || true

print_double_line
echo "Running yum update..."
sudo yum update -y

# https://docs.fedoraproject.org/en-US/epel/#_rhel_8
print_double_line
echo "Add RHEL..."
sudo subscription-manager repos --enable codeready-builder-for-rhel-8-$(arch)-rpms
sudo dnf install https://dl.fedoraproject.org/pub/epel/epel-release-latest-8.noarch.rpm -y

print_double_line
echo "Running yum install..."
grep -v '^#' yum.txt | xargs --no-run-if-empty -- sudo yum install -y

print_double_line
echo "Setting firewall for samba and mosh..."
sudo firewall-cmd --permanent --add-service=samba
# mosh
sudo firewall-cmd --zone=public --permanent --add-port=60000-61000/udp
sudo firewall-cmd --reload

print_double_line
echo "Detecting sensors..."
sudo sensors-detect --auto

print_double_line
echo "installing mamba..."
../install/mamba.sh

print_double_line
echo "installing zerotier..."
../install/zerotier.sh

print_double_line
echo "installing basher..."
../install/basher.sh
(
    cd ../common
    ./basher.sh
)

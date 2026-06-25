#!/usr/bin/env bash

set -e

# https://openzfs.github.io/openzfs-docs/Getting%20Started/RHEL-based%20distro/index.html

sudo dnf install https://zfsonlinux.org/epel/zfs-release.el8_5.noarch.rpm
sudo rpm --import /etc/pki/rpm-gpg/RPM-GPG-KEY-zfsonlinux

# check finger print, should be
# C93A FFFD 9F3F 7B03 C310 CEB6 A9D5 A1C0 F14A B620
gpg /etc/pki/rpm-gpg/RPM-GPG-KEY-zfsonlinux

sudo dnf config-manager --disable zfs
sudo dnf config-manager --enable zfs-kmod
sudo dnf install zfs

echo zfs | sudo tee /etc/modules-load.d/zfs.conf > /dev/null

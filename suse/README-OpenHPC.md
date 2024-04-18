# Introduction

This is a note to deploy OpenHPC 3.0 with OpenSUSE Leap 15.5 and SLURM variant.
The heading number used below here coincides with "OpenHPC (v3.0) Cluster Building Recipes—OpenSUSE Leap 15.5 Base OS Warewulf/SLURM Edition for Linux* (x86 64)".

OpenHPC documentation is excellent.
The only confusion is the its discovery—nowhere in its website makes it clear to know where to start reading the manual.
Links to the manual can be found in
[3.x · openhpc/ohpc Wiki](https://github.com/openhpc/ohpc/wiki/3.x).

# 2 Install Base Operating System (BOS)

Manual: follow on-screen guidance

- setup timezone, keyboard layout
- Choose server (not transactional as it is still experimental)
- Customize drive prep with
    - btrfs
    - without swap
- by default, it chooses wicked, alternatively, you can choose Network Manager

Automated: follow the AutoYaST guide and use profile from pre-existing installation.

## Hostname

```bash
# tailor this
export sms_name=ohpc \
    sms_ip=192.168.4.20
sudo hostnamectl set-hostname "$sms_name"
echo "$sms_ip $sms_name" | sudo tee -a /etc/hosts
hostnamectl
```

## Installing dependencies

```bash
sudo zypper update
sudo zypper install \
    bat \
    btop \
    fzf \
    fzf-bash-completion \
    fzf-tmux \
    fzf-zsh-completion \
    gh \
    git \
    gnu_parallel \
    hddtemp \
    htop \
    jq \
    lsb-release \
    lsd \
    make \
    mosh \
    ncdu \
    python3-glances \
    ranger \
    rasdaemon \
    s-tui \
    sensors \
    ShellCheck \
    shfmt \
    starship \
    tmux \
    tree \
    vim-fzf \
    zsh
chsh -s /usr/bin/zsh
# ZFS
sudo zypper addrepo https://download.opensuse.org/repositories/filesystems/$(lsb_release -rs)/filesystems.repo
sudo zypper refresh
sudo zypper install zfs
```

## Firewall

TODO: in the documentation, it mentions `SuSEfirewall2` should be disabled.
But `firewalld` is used in OpenSUSE Leap 15.5.
It is possible it actually meant to disable that instead.
So far let's set it up without disabling.

> Warning: Since Leap 15.0 Firewalld has been the default way to manage firewall configuration. Official SuSEfirewall2 packages are no longer available. [SuSEfirewall2 - openSUSE Wiki](https://en.opensuse.org/SuSEfirewall2)

Open UDP ports for mosh:

```bash
sudo firewall-cmd --zone=public --add-service=mosh --permanent
sudo firewall-cmd --reload
sudo firewall-cmd --zone=public --list-ports
sudo firewall-cmd --zone=public --list-services
```

To remove ports:

```bash
sudo firewall-cmd --zone=<zone> --remove-port=<port-number>/<protocol> --permanent
```

## Sensors

```bash
sudo sensors-detect
# and follow on screen instructions
```

## Personalize

Do your own personalization here.

# 3 Install OpenHPC Components

## 3.1 Enable OpenHPC repository for local use

```bash
sudo rpm -ivh http://repos.openhpc.community/OpenHPC/3/Leap_15/x86_64/ohpc-release-3-1.leap15.x86_64.rpm
```

# A Installation Template

C.f. <https://github.com/openhpc/ohpc/blob/3.x/docs/recipes/install/leap15/input.local.template>.

```bash
sudo zypper -n install docs-ohpc
mkdir -p ~/ohpc
cd ~/ohpc
cp /opt/ohpc/pub/doc/recipes/leap15/input.local .
cp -p /opt/ohpc/pub/doc/recipes/leap15/x86_64/warewulf/slurm/recipe.sh .
# tailor
# TODO: check eth_provision
```
Tailor this, for example,

```bash
# input.local
sms_name=ohpc
sms_ip=192.168.4.20
bmc_password=...
nagios_web_password=...

# recipe.sh
# probably they haven't updated the script for this part yet as of writing:
sed -i 's/SuSEfirewall2/firewalld/' recipe.sh
export OHPC_INPUT_LOCAL="$(realpath input.local)"
sudo ./recipe.sh
```

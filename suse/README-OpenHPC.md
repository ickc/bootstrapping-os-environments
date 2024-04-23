# 1 Introduction

This is a note to deploy OpenHPC 3.0 with OpenSUSE Leap 15.5 and SLURM variant.
The heading number used below here coincides with [OpenHPC (v3.0) Cluster Building Recipes—OpenSUSE Leap 15.5 Base OS Warewulf/SLURM Edition for Linux* (x86 64)](https://github.com/openhpc/ohpc/releases/download/v3.0.GA/Install_guide-Leap_15-Warewulf-SLURM-3.0-x86_64.pdf).

OpenHPC documentation is excellent.
The only confusion is the its discovery—nowhere in its website makes it clear to know where to start reading the manual.
Links to the manual can be found in
[3.x · openhpc/ohpc Wiki](https://github.com/openhpc/ohpc/wiki/3.x).

## OS choice

OpenHPC only supports RHEL derivatives or SUSE derivatives.

See [CERN Linux Landscape Update (2023-10-06)](https://indico.cern.ch/event/1253805/contributions/5556270/attachments/2729315/4744119/SoC3_Linux.pdf) for the recent EULA change made by Red Hat on June 21 2023.
In short, Red Hat is actively discourage the existence of a clone including the discontinuation of CentOS,
and the EULA change that is designed to kill off 3rd party clone such as Rocky Linux.

Because of this, OpenSUSE is recommended and used in this guide.
If RHEL derivatives is a must, AlmaLinux is recommended
as they aim for ABI compatibility,
avoiding the EULA restriction from Red Hat.

## UEFI

- Turn off Secure Boot if you need ZFS (or else self-signed the ZFS kernel module later)

## IPMI

`ipmitool` commands are skipped in this guide. Check the OpenHPC doc for details.

## 1.3 Inputs

OpenHPC doc and the automated script assumes some variables are defined.
Define these for the following, see appendix A for details.

```bash
# tailor this
export sms_name=ohpc \
    sms_ip=192.168.4.5 \
    ntp_server=0.uk.pool.ntp.org \
    bmc_password=... \
    nagios_web_password=...
```

# 2 Install Base Operating System (BOS)

This guide installs the OpenSUSE Leap 15.5.

Manual: follow on-screen guidance

- setup timezone, keyboard layout
- Choose server (not transactional as it is still experimental)
- Customize drive prep with
    - btrfs
    - without swap
- by default, it chooses wicked, alternatively, you can choose Network Manager
- turn off firewall, as OpenHPC doc will ask you to turn it off later

Automated: follow the AutoYaST guide and use profile from pre-existing installation.

## Hostname

C.f. [Inputs](#13-inputs).

```bash
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
    neofetch \
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

Skip this if you didn't enable firewall in the first place.

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

## 3.2 Installation template

Optionally, jump to [appendix A](#a-installation-template) to automate the followings by running a script.

## 3.3 Add provisioning services on *master* node

```bash
sudo zypper -n install ohpc-base
sudo zypper -n install ohpc-warewulf

# by default, OpenSUSE has this line
# include /etc/chrony.d/*.conf
# so that the file created below will be included
# also, note that /etc/chrony.d/pool.conf has default config, which is removed below
# tailor the "allow all" line to a more specific range if needed
sudo tee /etc/chrony.d/ohpc.conf <<EOF
local stratum 10
server ${ntp_server} iburst
allow ${sms_ip%.*}.0/24
EOF
sudo rm -f /etc/chrony.d/pool.conf
sudo systemctl restart chronyd
# showing some info
chronyc tracking
chronyc sources
chronyc sourcestats
```

## 3.4 Add resource management services on *master* node

```bash
sudo zypper -n install ohpc-slurm-server
sudo cp /etc/slurm/slurm.conf.ohpc /etc/slurm/slurm.conf
sudo cp /etc/slurm/cgroup.conf.example /etc/slurm/cgroup.conf
# this line edit SlurmctldHost
sudo perl -pi -e "s/SlurmctldHost=\S+/SlurmctldHost=${sms_name}/" /etc/slurm/slurm.conf
sudo nano /etc/slurm/slurm.conf
# edit this line
# NodeName=c[1-2] Sockets=1 CoresPerSocket=2 ThreadsPerCore=2 State=UNKNOWN
```

Optionally, set up `slurm-slurmdbd-ohpc`.

# A Installation Template

C.f. <https://github.com/openhpc/ohpc/blob/3.x/docs/recipes/install/leap15/input.local.template>.

```bash
sudo zypper install docs-ohpc
mkdir -p ~/ohpc
cd ~/ohpc
cp /opt/ohpc/pub/doc/recipes/leap15/input.local .
cp -p /opt/ohpc/pub/doc/recipes/leap15/x86_64/warewulf/slurm/recipe.sh .
# tailor
# TODO: check eth_provision
```

Tailor this, for `input.local`, c.f. [Inputs](#13-inputs).
For `recipe.sh`:

```bash
# probably they haven't updated the script for this part yet as of writing:
sed -i 's/SuSEfirewall2/firewalld/' recipe.sh
export OHPC_INPUT_LOCAL="$(realpath input.local)"
sudo ./recipe.sh
# fix some problems with the script
sudo nano /etc/slurm/slurm.conf
# edit this line
# NodeName=c[1-2] Sockets=1 CoresPerSocket=2 ThreadsPerCore=2 State=UNKNOWN
```

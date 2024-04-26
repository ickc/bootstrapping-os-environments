# 1 Introduction

This is a note to deploy OpenHPC 3.0 with OpenSUSE Leap 15.5 and SLURM variant.
The heading number used below here coincides with [OpenHPC (v3.0) Cluster Building Recipes—OpenSUSE Leap 15.5 Base OS Warewulf/SLURM Edition for Linux* (x86 64)](https://github.com/openhpc/ohpc/releases/download/v3.0.GA/Install_guide-Leap_15-Warewulf-SLURM-3.0-x86_64.pdf).

OpenHPC documentation is excellent.
The only confusion is its discovery—nowhere in its website makes it clear where to find the manual, which is in
[3.x · openhpc/ohpc Wiki](https://github.com/openhpc/ohpc/wiki/3.x).

## OS choice

OpenHPC only supports RHEL derivatives or SUSE derivatives.

See [CERN Linux Landscape Update (2023-10-06)](https://indico.cern.ch/event/1253805/contributions/5556270/attachments/2729315/4744119/SoC3_Linux.pdf) for the recent EULA change made by Red Hat on June 21 2023.
In short, Red Hat is actively discouraging the existence of a clone including the discontinuation of CentOS,
and the EULA change that is designed to kill off 3rd party clone such as Rocky Linux.

Because of this, OpenSUSE is recommended and used in this guide.
If RHEL derivatives is a must, AlmaLinux is recommended
as they aim for ABI compatibility,
avoiding the issues associated with making bug-for-bug-compatible clones after the Red Hat EULA change.

## UEFI

- Turn off Secure Boot if you need ZFS (or else self-signed the ZFS kernel module later).
    Note that this might already be the default, such as on ThinkSystem SR650 V3.

## IPMI

`ipmitool` commands are skipped in this guide. Check the OpenHPC doc for details.

## 1.2 Requirements/Assumptions

This guide follows the reference design of OpenHPC in Fig. 1 of the documentation.
In particular, there's a separate network connecting the master node to compute nodes.

Note that the reference design as shown in Fig. 1 has an optional parallel file system.
This is excluded in this guide, and the baseline choice would be Ceph.

Also note that the master node (a.k.a. head node, or SMS) is supposed to export an NFS.
In this guide, we will build a ZFS pool and export that as the NFS mount.
This is a choice orthogonal to the OpenHPC documentation and is documented in [the ZFS section](#zfs).

## 1.3 Inputs

OpenHPC doc and the automated script assumes some variables are defined.
Define these for the following sections. See appendix A for details.

```bash
# tailor this
export sms_name=penrose-master \
    sms_ip=192.168.1.5 \
    internal_netmask=255.255.255.0 \
    sms_eth_internal=p1p1 \
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
    - btrfs, chosen to guard against bit-rot with better support to be used as root drive in Linux. OpenSUSE supports this and is the default choice. This is especially important for storage nodes.
        - Ideally, to minimize any chance of bit rot, turn off any hardware RAID expose the raw device as JBOD. Setup btrfs yourself to use 2 drives in RAID 1 configuration (such as 512MiB for UEFI boot partition, the rest for btrfs.)
    - without swap
- by default, it chooses wicked, alternatively, you can choose Network Manager
- turn off firewall, as OpenHPC doc will ask you to turn it off later

Automated: follow the AutoYaST guide and use profile from pre-existing installation. This is useful to redeploy OpenSUSE to identical hardware configurations.

## Hostname

C.f. [Inputs](#13-inputs).

```bash
sudo hostnamectl set-hostname "$sms_name"
echo "$sms_ip $sms_name" | sudo tee -a /etc/hosts
hostnamectl
```

## Installing dependencies

Tailor this section to your liking:

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
    lldpd \
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
```

## Firewall

Skip this if you didn't enable firewall in the first place.

TODO: in the documentation, it mentions `SuSEfirewall2` should be disabled.
But `firewalld` is used in OpenSUSE Leap 15.5.
It is possible it actually meant to disable that instead.

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

Do your own personalization here, such as setting up your own dotfiles.

# ZFS

Install ZFS:

```bash
sudo zypper addrepo https://download.opensuse.org/repositories/filesystems/$(lsb_release -rs)/filesystems.repo
sudo zypper refresh
sudo zypper install zfs
```

In this example, preparing for the NFS mount from the master to compute nodes,
we will create a ZFS pool of 90 HDDs using draid.
For an introduction to draid, see the [documentation](https://openzfs.github.io/openzfs-docs/Basic%20Concepts/dRAID%20Howto.html), which is very light on details,
or [this 2020 presentation from ZFS developer](https://docs.google.com/presentation/d/1uo0nBfY84HIhEqGWEx-Tbm8fPbJKtIP3ICo4toOPcJo/).

Here we make the following choice:

- parity: 2
- data: 9
- children: 90
- spares: 2

Note that we are not choosing 8 data + 2 parity configuration as we want to have some hot spares.
This recommendation is based on an
[undocumented internal analysis available here](https://docs.google.com/spreadsheets/d/11skQ6fB39xiTJCtHYazxsIJZWKxzcWrH/edit?usp=sharing&ouid=117180715885747044421&rtpof=true&sd=true).
The decision rule is based on the criteria that we require at least 4/3 PB of usable storage space,
and a subjective judgement to balance between IOPS, risk, and no. of hot spares.

Before proceeding, follow this guide on
[Advanced Format hard disk drives](https://wiki.archlinux.org/title/Advanced_Format#Advanced_Format_hard_disk_drives)
to check if there are advanced format options,
and if so, perform advance formatting with 4k (4096).

```bash
# this is just a quick and dirty trick to get the list of HDDs on the storage nodes
# The trick would fails if not all the HDDs are 18.2T
readarray -t disks < <(lsblk | grep '18.2T' | cut -d' ' -f1)
# E.g. disks=(sda sdb sdc sdd sde sdf sdg sdh sdi sdj sdk sdl sdm sdn sdo sdp sdq sdr sds sdt sdu sdv sdw sdx sdy sdz sdaa sdab sdac sdad sdae sdaf sdag sdah sdai sdaj sdak sdal sdam sdan sdao sdap sdaq sdar sdas sdat sdau sdav sdaw sdax sday sdaz sdba sdbb sdbc sdbd sdbe sdbf sdbg sdbh sdbi sdbj sdbk sdbl sdbm sdbn sdbo sdbp sdbq sdbr sdbs sdbt sdbu sdbv sdbw sdbx sdby sdbz sdca sdcb sdcc sdcd sdce sdcf sdcg sdch sdci sdcj sdck sdcl)
# atime, acl, compression and xattr settings are chosen for performance
sudo zpool create \
    -f \
    -n \
    -m /srv/dicke \
    -o ashift=12 \
    -o autoexpand=on \
    -O acltype=off \
    -O atime=off \
    -O compression=off \
    -O normalization=formD \
    -O xattr=sa \
    dicke \
    draid2:9d:90c:2s \
    ${disks[@]}
# the above command is run with `-n` for dry-run
# once confirmed it is good to go, rerun without `-n`
# import by id to guard against silent change of ordering of device names such as sda, sdb, ...
sudo zpool export dicke
sudo zpool import -d /dev/disk/by-id dicke
```

Now, your pool should be available at `/srv/dicke`.

## Adding SLOG & L2ARC

Optionally but highly recommended, follow the section "Adding an L2ARC" from the blog post
[Aaron Toponce : ZFS Administration, Part IV- The Adjustable Replacement Cache](https://web.archive.org/web/20230828024336/https://pthree.org/2012/12/07/zfs-administration-part-iv-the-adjustable-replacement-cache/).

The command involved is something like

```bash
parted /dev/nvme... unit s mklabel gpt mkpart primary zfs 2048 4G mkpart primary zfs 4G 100%
parted /dev/nvme... unit s mklabel gpt mkpart primary zfs 2048 4G mkpart primary zfs 4G 100%
zpool add dicke \
    log mirror \
        /dev/disk/by-id/...-part1 \
        /dev/disk/by-id/...-part1 \
    cache \
        /dev/disk/by-id/...-part2 \
        /dev/disk/by-id/...-part2
```

But you need to adjust the device names, the device IDs, and the size to your specific case.

## NFS share

You have 2 choices,

1. Export this path through NFS by following the OpenHPC doc, or alternatively,
2. uses the ZFS specific method to share over NFS by following this guide:
    [Aaron Toponce : ZFS Administration, Part XV- iSCSI, NFS and Samba](https://web.archive.org/web/20230828014245/https://pthree.org/2012/12/31/zfs-administration-part-xv-iscsi-nfs-and-samba/).
    To see the motivation of using the ZFS specific method, see the "Motivation" section of that blog post.

## ZFS References

- [OpenZFS Documentation — OpenZFS documentation](https://openzfs.github.io/openzfs-docs/index.html)
- [System Administration - OpenZFS](https://openzfs.org/wiki/System_Administration)
- [Aaron Toponce : Install ZFS on Debian GNU/Linux](https://web.archive.org/web/20230904234829/https://pthree.org/2012/04/17/install-zfs-on-debian-gnulinux/)

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

## 3.7 Complete basic Warewulf setup for *master* node

```bash
sudo cp /etc/warewulf/provision.conf /etc/warewulf/provision.conf.old
sudo perl -pi -e "s/device = eth1/device = ${sms_eth_internal}/" /etc/warewulf/provision.conf
sudo perl -pi -e "s#\#tftpdir = /var/lib/#tftpdir = /srv/#" /etc/warewulf/provision.conf
sudo perl -pi -e "s,cacert =.*,cacert = /etc/ssl/ca-bundle.pem," /etc/warewulf/provision.conf

sudo cp /etc/sysconfig/dhcpd /etc/sysconfig/dhcpd.old
sudo perl -pi -e "s/^DHCPD_INTERFACE=\S+/DHCPD_INTERFACE=${sms_eth_internal}/" /etc/sysconfig/dhcpd

sudo cp /etc/apache2/conf.d/warewulf-httpd.conf /etc/apache2/conf.d/warewulf-httpd.conf.old
sudo perl -pi -e "s#modules/mod_perl.so\$#/usr/lib64/apache2/mod_perl.so#" /etc/apache2/conf.d/warewulf-httpd.conf

# skip this if you have already configured the network
sudo ip link set dev ${sms_eth_internal} up
# skip this if you do not use a separate network between master and compute nodes as in Fig. 1
sudo ip address add ${sms_ip}/${internal_netmask} broadcast + dev ${sms_eth_internal}

sudo a2enmod mod_rewrite

sudo systemctl enable mariadb.service
sudo systemctl restart mysql
sudo systemctl enable apache2.service
sudo systemctl restart apache2
sudo systemctl enable dhcpd.service
sudo systemctl enable tftp.socket
sudo systemctl start tftp.socket
```

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

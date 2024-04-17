# Install Base Operating System (BOS)

Manual: follow on-screen guidance

- setup timezone, keyboard layout
- Choose server (not transactional as it is still experimental)
- Customize drive prep with
    - btrfs
    - without swap
- by default, it chooses wicked, alternatively, you can chooce Network Manager

Automated: follow the AutoYaST guide and use profile from pre-existing installation.

## Variables

C.f. template: `/opt/ohpc/pub/doc/recipes/leap15/input.local`
or <https://github.com/openhpc/ohpc/blob/b2e3d64f628870e82c2508cadbbb40fa040a348c/docs/recipes/install/leap15/input.local.template#L4>.

```bash
# tailor this
export sms_name=ohpc \
    sms_ip=192.168.4.20
```

## Hostname

```bash
sudo hostnamectl set-hostname "$sms_name"
echo "$sms_ip $sms_name" | sudo tee -a /etc/hosts
hostnamectl
```

## Installing dependencies

```bash
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

## Personalize

Do your own personalization here.

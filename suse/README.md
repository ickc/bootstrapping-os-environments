# Installing OS

Manual: follow on-screen guidance

- setup timezone, keyboard layout
- Choose transactional server
- Customize drive prep with
    - encryption
    - btrfs
    - without swap
- Optionally setup bonding (802.3ad)

Automated: follow the AutoYaST guide and use profile from pre-existing installation.

# Disable periodic transactional update

```bash
sudo systemctl disable --now transactional-update.timer
```

# Installing dependencies

```bash
# or if not using transactional server: sudo zypper update && sudo zypper install...
sudo transactional-update pkg install \
    apcupsd \
    bat \
    btop \
    exfatprogs \
    f3 \
    fastfetch \
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
    samba \
    sensors \
    ShellCheck \
    shfmt \
    starship \
    tmux \
    tree \
    vim-fzf \
    zsh
# after reboot
chsh -s /usr/bin/zsh
# ZFS
sudo zypper addrepo https://download.opensuse.org/repositories/filesystems/$(lsb_release -rs)/filesystems.repo
sudo zypper refresh
sudo transactional-update pkg install zfs
```

# Firewall

Open UDP ports for mosh:

```bash
sudo firewall-cmd --zone=public --add-service=mosh --permanent
sudo firewall-cmd --reload
sudo firewall-cmd --zone=public --list-ports
```

For Samba:

```bash
sudo firewall-cmd --zone=public --add-service=samba --permanent
sudo firewall-cmd --reload
sudo firewall-cmd --zone=public --list-ports
sudo firewall-cmd --zone=public --list-services
```

To remove ports:

```bash
sudo firewall-cmd --zone=<zone> --remove-port=<port-number>/<protocol> --permanent
```

# Sensors

```bash
sudo sensors-detect
# and follow on screen instructions
```

# Personalize

```bash
# create ssh key pair
BSOS_SSH_COMMENT=$USER@$HOSTNAME
mkdir -p "$HOME/.ssh"
ssh-keygen -t ed25519 -C "$BSOS_SSH_COMMENT" -f "$HOME/.ssh/id_ed25519"
eval "$(ssh-agent -s)"
ssh-add "$HOME/.ssh/id_ed25519"

# authenticate with GitHub
# open https://github.com/login/device and type the code seen on screen
gh auth login --git-protocol ssh --web

# clone BSOS
mkdir -p "$HOME/git/source"
cd "$HOME/git/source"
git clone git@github.com:ickc/bootstrapping-os-environments.git

# clone dotfiles
mkdir -p "$HOME/git/source"
cd "$HOME/git/source"
git clone git@github.com:ickc/dotfiles.git
cd dotfiles
. "$HOME/git/source/dotfiles/config/zsh/.zshenv"
make install && make

# Installing ssh-dir
git clone git@github.com:ickc/ssh-dir.git "$HOME/.ssh.temp"
cd "$HOME/.ssh.temp"
mv "$HOME/.ssh/id_ed25519" "$HOME/.ssh.temp"
mv "$HOME/.ssh/id_ed25519.pub" "$HOME/.ssh.temp"
rm -rf "$HOME/.ssh"
mv "$HOME/.ssh.temp" "$HOME/.ssh"
```

# Docker

```bash
sudo zypper install docker docker-compose docker-compose-switch
sudo systemctl enable docker
sudo usermod -G docker -a $USER
# make the group change immediate, alternatively, log out and back in again
newgrp docker
sudo systemctl restart docker
# testing
docker version
docker run --rm hello-world
docker images
# docker rmi -f IMAGE_ID
```

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

# Installing dependencies

```bash
sudo transactional-update pkg install \
    bat \
    fzf \
    gh \
    git \
    gnu_parallel \
    htop \
    jq \
    lsd \
    make \
    mosh \
    ncdu \
    python3-glances \
    ranger \
    s-tui \
    sensors \
    ShellCheck \
    shfmt \
    starship \
    tmux \
    tree \
    zsh
# after reboot
chsh -s /usr/bin/zsh
```

# Firewall

Open UDP ports for mosh:

```bash
sudo firewall-cmd --zone=public --add-port=60000-61000/udp --permanent
sudo firewall-cmd --reload
sudo firewall-cmd --zone=public --list-ports
```

# Personalize

```bash
# create ssh key pair
SSH_ALGO=ed25519
BSOS_SSH_COMMENT=$USER@$HOSTNAME
mkdir -p "$HOME/.ssh"
ssh-keygen -t "$SSH_ALGO" -C "$BSOS_SSH_COMMENT" -f "$HOME/.ssh/id_${SSH_ALGO}"
eval "$(ssh-agent -s)"
ssh-add "$HOME/.ssh/id_${SSH_ALGO}"

# authenticate with GitHub
# open https://github.com/login/device
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
# shellcheck disable=SC1091
. "$HOME/git/source/dotfiles/bin/env"
make install && make

# Installing ssh-dir
git clone git@github.com:ickc/ssh-dir.git "$HOME/.ssh.temp"
cd "$HOME/.ssh.temp"
mv "$HOME/.ssh/id_${SSH_ALGO}" "$HOME/.ssh.temp"
mv "$HOME/.ssh/id_${SSH_ALGO}.pub" "$HOME/.ssh.temp"
rm -rf "$HOME/.ssh"
mv "$HOME/.ssh.temp" "$HOME/.ssh"

# Installing basher
cd "$HOME/git/source/bootstrapping-os-environments/install"
./basher.sh
export PATH="$HOME/.basher/bin:$PATH"
print_line
echo "Installing basher packages..."
cd "$HOME/git/source/bootstrapping-os-environments/common"
./basher.sh
```

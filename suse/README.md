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
    btop \
    fzf \
    fzf-bash-completion \
    fzf-tmux \
    fzf-zsh-completion \
    gh \
    git \
    gnu_parallel \
    htop \
    jq \
    lsb-release \
    lsd \
    make \
    mosh \
    ncdu \
    python3-glances \
    ranger \
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
```

To remove ports:

```bash
sudo firewall-cmd --zone=<zone> --remove-port=<port-number>/<protocol> --permanent
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

# Installing basher
cd "$HOME/git/source/bootstrapping-os-environments/install"
./basher.sh
export PATH="$HOME/.basher/bin:$PATH"
print_line
echo "Installing basher packages..."
cd "$HOME/git/source/bootstrapping-os-environments/common"
./basher.sh
```

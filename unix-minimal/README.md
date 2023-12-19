# Dependencies

- minimal dependencies
    - curl
    - git or unzip

# Steps

## Add record to ssh-config

On local machine,

```sh
code ~/.ssh/config
```

Create a record for this remote machine.

Alternatively, skip this and [Install vscode-cli](#install-vscode-cli).

## Installing dependencies

### Installing dependencies via system package manager (optional)

Optionally install dependencies and change shell first:

```sh
... install zsh git make curl wget openssh-server
chsh -s $(which zsh)
```

### Installing dependencies via conda (mandatory)

This would also clone this repo automatically at `~/git/source/bootstrapping-os-environments`.

```bash
curl -L https://github.com/ickc/bootstrapping-os-environments/raw/master/unix-minimal/bootstrap.sh | bash
```

### Install vscode-server

Connect to this server using vscode remote SSH.

Run on the remote, study how this new remote system is setting up dotfiles first. Update dotfiles to add this system before proceeding.
Also remove useless initial files in home.

#### Install vscode-cli

Alternatively, install vscode-cli instead,

```bash
curl -L https://github.com/ickc/bootstrapping-os-environments/raw/master/install/vscode_cli.sh | bash
~/.local/bin/code tunnel --disable-telemetry
```

Or if this repo is cloned already:

```bash
~/git/source/bootstrapping-os-environments/unix-minimal/vscode_cli.sh
~/.local/bin/code tunnel --disable-telemetry
```

## Install

Then run,

```sh
mkdir ~/temp
cd ~/temp
curl -O -L https://github.com/ickc/bootstrapping-os-environments/raw/master/unix-minimal/install.sh
bash install.sh
```

Or if this repo is cloned already:

```sh
~/git/source/bootstrapping-os-environments/unix-minimal/install.sh
```

## All in one go

Some manual interaction needed:

```sh
export BSOS_SSH_COMMENT="$USER@$HOSTNAME"; curl -L https://github.com/ickc/bootstrapping-os-environments/raw/master/unix-minimal/bootstrap.sh | bash && curl -L https://github.com/ickc/bootstrapping-os-environments/raw/master/install/vscode_cli.sh | bash && ~/git/source/bootstrapping-os-environments/unix-minimal/install.sh && ~/.local/bin/code tunnel --disable-telemetry
```

At Blackett,

```sh
curl -L https://github.com/ickc/bootstrapping-os-environments/raw/master/unix-minimal/bootstrap-xrootd.sh | bash
```

# Links

You may need to open <https://github.com/login/device> and input the one-time code to authenticate.

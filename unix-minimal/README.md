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

## Installing dependencies

### Installing dependencies via system package manager (optional)

Optionally install dependencies and change shell first:

```sh
... install zsh git make curl wget openssh-server
chsh -s $(which zsh)
```

### Installing dependencies via conda (mandatory)

```bash
curl -L https://github.com/ickc/bootstrapping-os-environments/raw/master/unix-minimal/bootstrap.sh | bash
```

### Install vscode-server

Connect to this server using vscode remote SSH.

Run on the remote, study how this new remote system is setting up dotfiles first. Update dotfiles to add this system before proceeding.
Also remove useless initial files in home.

## Install

Then run,

```sh
mkdir ~/temp
cd ~/temp
curl -O -L https://github.com/ickc/bootstrapping-os-environments/raw/master/unix-minimal/install.sh
bash install.sh
```

# Dependencies

- minimal dependencies
    - curl
    - git
    - make

# Steps

## Add record to ssh-config

On local machine,

```sh
code ~/git/private/ssh-dir/.ssh/config
```

Create a record for this remote machine.

## Install vscode-server

Connect to this server using vscode remote SSH.

Run on the remote, study how this new remote system is setting up dotfiles first. Update dotfiles to add this system before proceeding.
Also remove useless initial files in home.

## Install and setup

In case of very old system, generate ssh keys yourself, add it to your GitHub account in <https://github.com/settings/keys> first.

You may want to tailor dotfiles before running this.

Optionally install dependencies and change shell first:

```sh
... install zsh git make curl wget openssh-server
chsh -s $(which zsh)
```

Then run,

```sh
mkdir -p ~/git/source && cd ~/git/source && git clone git@github.com:ickc/bootstrapping-os-environments.git && bootstrapping-os-environments/linux-minimal/install.sh
```

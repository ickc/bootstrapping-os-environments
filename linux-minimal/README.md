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

Then run,

```sh
mkdir -p ~/git/source && cd ~/git/source && git clone git@github.com:ickc/bootstrapping-os-environments.git && bootstrapping-os-environments/linux-minimal/install.sh
```

or use curl-bash if agent forwarding doesn't work on old systems:

```sh
curl -sL https://github.com/ickc/bootstrapping-os-environments/raw/master/linux-minimal/install.sh -o install.sh && ./install.sh && rm -f install.sh
```

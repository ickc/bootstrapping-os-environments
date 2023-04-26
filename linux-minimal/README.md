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

Run on the remote, study how this new remote system is setting up dotfiles first. Update dotfiles to add this system before proceeding.
Also remove useless initial files in home.
Then run,

```sh
bash <(curl -sL https://github.com/ickc/bootstrapping-os-environments/raw/master/linux-minimal/install.sh)
# or
curl -sL https://github.com/ickc/bootstrapping-os-environments/raw/master/linux-minimal/install.sh -o install.sh
bash install.sh
```

### Install vscode-server

Connect to this server using vscode remote SSH.

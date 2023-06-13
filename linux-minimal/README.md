# Dependencies

- minimal dependencies
    - curl
    - git
    - make

If git is not present, there's a workaround below.

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

### Preparation

In case of very old system, generate ssh keys yourself, add it to your GitHub account in <https://github.com/settings/keys> first.

### Installing dependencies via system package manager (optional)

Optionally install dependencies and change shell first:

```sh
... install zsh git make curl wget openssh-server
chsh -s $(which zsh)
```

### Installing dependencies via conda (mandatory)

1. Download bootstrapping-os-environments
    1. Without git

        Obtain bootstrapping-os-environments without git:

        ```bash
        mkdir -p ~/git/source &&
        cd ~/git/source &&
        curl -O -L https://github.com/ickc/bootstrapping-os-environments/archive/refs/heads/master.zip &&
        unzip master.zip &&
        rm -f master.zip &&
        mv bootstrapping-os-environments-master bootstrapping-os-environments
        ```

    2. With git

        ```bash
        mkdir -p ~/git/source &&
        cd ~/git/source &&
        git clone git@github.com:ickc/bootstrapping-os-environments.git
        ```

    3. Then run `mamba.sh`:

        ```bash
        cd ~/git/source/bootstrapping-os-environments/install/
        CONDA_PREFIX=~/.mambaforge ./mamba.sh
        . ~/.mambaforge/bin/activate

        cd ~/git/source/bootstrapping-os-environments/common/conda/
        ./conda-system.sh
        export PATH="$PATH:$HOME/.local/bin"
        ```

    4. Switching back to git, if no-git is used above,

        ```bash
        rm -rf ~/git/source/bootstrapping-os-environments &&
        cd ~/git/source &&
        git clone git@github.com:ickc/bootstrapping-os-environments.git
        ```

### Install

Then run,

```sh
~/git/source/bootstrapping-os-environments/linux-minimal/install.sh
```

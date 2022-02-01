# How to use R in the conda ecosystem

## Create a conda environment and install the IRkernel in jupyter

This assumes you want R and jupyter in a separate environment.

```bash
# install irkernel, which draws its dependences including R
mamba create --name r r-irkernel -y
```

And then we need to run the following in R (use `Rscript` to run it from shell):

```bash
Rscript -e 'IRkernel::installspec()'
```

which would fails as it calls `jupyter kernelspec --version`.

In order for it to call jupyter in your other jupyter environment successfully,
you need to manually stack the 2 environments, by something like this:

```bash
# adjust path to jupyter by running `which jupyter`
export PATH="$PATH:$HOME/.mambaforge/envs/jupyterlab/bin"
```

In short,

```bash
mamba create --name r r-irkernel -y
conda activate r
# adjust path to jupyter by running `which jupyter`
export PATH="$PATH:$HOME/.mambaforge/envs/jupyterlab/bin"
Rscript -e 'IRkernel::installspec()'
```

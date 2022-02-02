# How to use R in the conda ecosystem

## Create a conda environment and install the IRkernel in jupyter

This assumes you want R and jupyter in a separate environment.

```bash
# install irkernel, which draws its dependences including R
mamba create --name ir r-irkernel -y
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
mamba env create -f ir.yml
conda activate ir
# adjust path to jupyter by running `which jupyter`
export PATH="$PATH:$HOME/.mambaforge/envs/jupyterlab/bin"
Rscript -e 'IRkernel::installspec()'
```

# Notes

Installing `r-dlm` this way will have the following error (on macOS Monterey): `.../libRlapack.dylib' (no such file)`.

The simpler way probably is just install RStudio and use it to install any R packages needed:

```bash
# r must be installed, otherwise rstudio will complain upon opening
# see https://stackoverflow.com/a/69473115/5769446
# which suggest r must be installed before rstudio
brew install --cask r
brew install --cask rstudio
# open rstudio to manually install irkernel, languageserver, dlm...
# then install the irkernel for jupyterlab
conda activate jupyterlab
Rscript -e 'IRkernel::installspec()'
```

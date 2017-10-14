# Usage

See `conda.sh -h`.

The default files used will be the `conda.sh`, a more minimal setup.

For a relatively complete setup, uses

```bash
# Example
./conda.sh -v 3 -c intel -n all -C conda-all.txt -P pip-all.txt -m mpich
```

# Caveats

Note that by default (search regex `(conda_install|pip install)` in `conda.sh`), the following will be installed (even without being specified in `conda.txt`/`pip.txt`):

- `pyslalib`
- a version of `mpi4py` will be installed depending on the `-m` flag
- on `intel` channel:
    - `ipython` from the `defaults` channel instead
    - `scipy<0.19`
- when installing Python 2 (`-v 2` flag):
    - `weave`
    - `functools32`

Reasons for these are briefly mentioned in comments of `conda.sh`. Ideally, more flags to control these behavior, and/or looking up the existence of these in the `conda.txt` file first are desired. But for me this is what I needed anyway so I didn't do that. Pull request is welcomed to remedy this though.

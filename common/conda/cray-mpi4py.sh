#!/usr/bin/env bash

set -e

# TODO: better choice of this tempdir
tempDir="$HOME/.mpi4py/"
mpi4pyVersion="3.0.3" #TODO
mpiName="mpi4py-$mpi4pyVersion"

mkdir -p "$tempDir" && cd "$tempDir"
wget -qO- https://bitbucket.org/mpi4py/mpi4py/downloads/$mpiName.tar.gz | tar -xzf -
cd $mpiName

if [[ -n $NERSC_HOST ]]; then
    module swap PrgEnv-intel PrgEnv-gnu
    module unload craype-hugepages2M
    module unload libfabric || true

    python setup.py build --mpicc="$(which cc) -shared" && python setup.py install
    # this is not needed
    # c.f. https://mpi4py.readthedocs.io/en/stable/appendix.html#mpi-enabled-python-interpreter
    # also, https://docs.nersc.gov/programming/libraries/hdf5/h5py/
    # python setup.py build_exe --mpicc="$(which cc) -dynamic" && python setup.py install_exe
else
    # * see https://bitbucket.org/mpi4py/mpi4py/issues/143/build-failure-with-openmpi
    cat << EOF > conf/sysconfigdata-conda-user.py
import os, sysconfig
from distutils.util import split_quoted

_key = '_PYTHON_SYSCONFIGDATA_NAME'
_val = os.environ.pop(_key, None)
_name = sysconfig._get_sysconfigdata_name(True)

_data = __import__(_name, globals(), locals(), ['build_time_vars'], 0)
build_time_vars = _data.build_time_vars

def _fix_options(opt):
    if not isinstance(opt, str):
        return opt
    try:
        opt = split_quoted(opt)
    except:
        return opt
    try:
        i = opt.index('-B')
        del opt[i:i+2]
    except ValueError:
        pass
    try:
        i = opt.index('-Wl,--sysroot=/')
        del opt[i]
    except ValueError:
        pass
    return " ".join(opt)

for _key in build_time_vars:
    build_time_vars[_key] = _fix_options(build_time_vars[_key])
EOF
    _PYTHON_SYSCONFIGDATA_NAME=sysconfigdata-conda-user python setup.py build && python setup.py install
fi

cd -

rm -rf "$tempDir"

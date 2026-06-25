#!/usr/bin/env bash

set -e

MPI4PYTMPDIR="${MPI4PYTMPDIR:-${HOME}/.mpi4py/}"
MPI4PY_VERSION="${MPI4PY_VERSION:-3.1.3}"

if [[ -n ${NERSC_HOST} ]]; then
    # https://docs.nersc.gov/development/languages/python/parallel-python/#mpi4py-in-your-custom-conda-environment
    echo NERSC host detected, using NERSC recommended method to install mpi4py...
    module swap PrgEnv-${PE_ENV,,} PrgEnv-gnu
    module unload craype-hugepages2M
    module unload libfabric || true

    MPICC="cc -shared" pip install --force --no-cache-dir --no-binary=mpi4py "mpi4py==${MPI4PY_VERSION}"
else
    mpiName="mpi4py-${MPI4PY_VERSION}"
    mkdir -p "${MPI4PYTMPDIR}" && cd "${MPI4PYTMPDIR}"
    wget -qO- "https://github.com/mpi4py/mpi4py/releases/download/${MPI4PY_VERSION}/mpi4py-${MPI4PY_VERSION}.tar.gz" | tar -xzf -
    cd ${mpiName}

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

rm -rf "${MPI4PYTMPDIR}"

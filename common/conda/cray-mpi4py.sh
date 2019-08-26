#!/usr/bin/env bash

set -e

# TODO: better choice of this tempdir
tempDir="$HOME/.mpi4py/"
mpi4pyVersion="3.0.2" #TODO
mpiName="mpi4py-$mpi4pyVersion"

mkdir -p "$tempDir" && cd "$tempDir"
wget -qO- https://bitbucket.org/mpi4py/mpi4py/downloads/$mpiName.tar.gz | tar -xzf -
cd $mpiName

if [[ -n $NERSC_HOST ]]; then
    module swap PrgEnv-intel PrgEnv-gnu
    module unload craype-hugepages2M
    module unload libfabric || true
fi

python setup.py build --mpicc="$(which cc) -shared"
python setup.py build_exe --mpicc="$(which cc) -dynamic"
python setup.py install
python setup.py install_exe

cd -

rm -rf "$tempDir"

#!/usr/bin/env bash

set -e

# optionally override these with env. var.
VERSION=${VERSION-3.3.8}
PREFIX="${PREFIX-"${SCRATCH}/local/toast-gnu/compile"}"
TEMPDIR="${TEMPDIR-"${SCRATCH}/local/toast-gnu/git"}"

# c.f. https://stackoverflow.com/a/23378780/5769446
P="${P-$(if [[ "$(uname)" == Darwin ]]; then sysctl -n hw.physicalcpu_max; else lscpu -p | grep -E -v '^#' | sort -u -t, -k 2,4 | wc -l; fi)}"
echo "Using ${P} processes..."

print_log() {
    eval printf %.0s= '{1..'"${COLUMNS:-$(tput cols)}"\}
    printf "$@\n"
}

print_log "download fftw to ${TEMPDIR}"

mkdir -p "${TEMPDIR}"
cd "${TEMPDIR}"
wget -qO- http://www.fftw.org/fftw-${VERSION}.tar.gz | tar -xzf -

print_log configure

cd fftw-${VERSION}
# CC=icc
if [[ $(uname) == Darwin ]]; then
    echo "I'm patching it according to https://github.com/FFTW/fftw3/issues/136"
    sed -i 's/target_link_libraries (\${fftw3_lib}_omp \${fftw3_lib})/target_link_libraries (\${fftw3_lib}_omp \${fftw3_lib})\n\ttarget_link_libraries (\${fftw3_lib}_omp \${OpenMP_C_FLAGS})/g' CMakeLists.txt
    CC=gcc-9
else
    CC=gcc
fi
# CC=${CC} CFLAGS='-Ofast -ffast-math -march=native' ./configure --enable-float --enable-openmp --prefix=${PREFIX} --enable-avx2
cmake . -DCMAKE_C_COMPILER=gcc-9 -DCMAKE_CXX_COMPILER=g++-9 -DENABLE_THREADS=ON -DENABLE_OPENMP=ON -DBUILD_TESTS=OFF -DCMAKE_BUILD_TYPE=DEBUG -DCMAKE_INSTALL_PREFIX:PATH=${PREFIX}

print_log make

make -j ${P}
make install

# print_log cleanup
# rm -rf "${TEMPDIR}"

echo '# export these PATH'
# echo export PATH="${PREFIX}/bin:\${PATH}"
echo export LD_LIBRARY_PATH=${PREFIX}/lib:\${LD_LIBRARY_PATH}"
# echo export MANPATH="${PREFIX}/share/man:\${MANPATH}

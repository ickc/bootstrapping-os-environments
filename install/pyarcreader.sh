#!/usr/bin/env bash

# this is an example script on compiling this on NERSC
# assume libarchive is installed already (see example from https://github.com/ickc/reproducible-os-environments/blob/master/install/libarchive.sh)
# assume you have chosen a compiler you want via module
# e.g. module swap intel/19.1.2.254 intel/19.1.3.304
# optionally override these with env. var.
TEMPDIR="${TEMPDIR-"$SCRATCH/.pbarchive"}"
PREFIX="${PREFIX-"$CONDA_PREFIX"}"
BOLOUSER="${BOLOUSER-"$USER"}"

# c.f. https://stackoverflow.com/a/23378780/5769446
P="${P-$(if [[ "$(uname)" == Darwin ]]; then sysctl -n hw.physicalcpu_max; else lscpu -p | grep -E -v '^#' | sort -u -t, -k 2,4 | wc -l; fi)}"
echo "Using $P processes..."

NUMPY_INCLUDE="$(find "$PREFIX" -type d -path '*/lib/python*/site-packages/numpy/core/include')"
echo "Using numpy include dir: $NUMPY_INCLUDE"

mkdir -p "$TEMPDIR" &&
    cd "$TEMPDIR" &&
    git clone "$BOLOUSER@bolowiki.berkeley.edu:/pbrepo/PbArchive.git" &&
    cd PbArchive &&
    ./autogen.sh &&
    mkdir -p "$PREFIX" &&
    CPPFLAGS="-I${PREFIX}/include -I$NUMPY_INCLUDE" LDFLAGS="-L${PREFIX}/lib" ./configure --prefix="$PREFIX" --with-libarchive="$PREFIX" &&
    make -j "$P" &&
    make install -j "$P" &&
    rm -rf "$TEMPDIR"

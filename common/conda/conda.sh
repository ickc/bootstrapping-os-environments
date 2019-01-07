#!/usr/bin/env bash

set -e

usage="${BASH_SOURCE[0]} [-h] [-v version] [-c channel] [-n name] [-p conda PATH] [-C conda-path] [-P pip-path] [-m mpi] --- create conda environments

where:
	-h	show this help message
	-v	python version. 2 or 3. Default: %s
	-c	conda channel. e.g. intel, defaults. Default: %s
	-n	prefix of the name of environment. Default: %s
	-p	Full path to conda environment prefix. If not specified, conda's default will be used.
	-C	path to a file that contains the list of conda packages to be installed. Default: %s
	-P	path to a file that contains the list of pip packages to be installed. Default: %s
	-m	custom version of mpi4py if sepecified. e.g. mpich/openmpi to use mpich/openmpi from the mpi4py channel; cray to custom build using cray compiler.
"

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# getopts ######################################################################

# reset getopts
OPTIND=1

# Initialize parameters
version=2
channel=defaults
prefix=ab
condaInstallPath=None
path2conda="$DIR/conda.txt"
path2pip="$DIR/pip.txt"
mpi=None

# get the options
while getopts "v:c:n:p:C:P:m:h" opt; do
	case "$opt" in
	v)	version="$OPTARG"
		;;
	c)	channel="$OPTARG"
		;;
	n)	prefix="$OPTARG"
		;;
	p)	condaInstallPath="$OPTARG"
		;;
	C)	path2conda="$OPTARG"
		;;
	P)	path2pip="$OPTARG"
		;;
	m)	mpi="$OPTARG"
		;;
	h)	printf "$usage" "$version" "$channel" "$prefix" "$path2conda" "$path2pip"
		exit 0
		;;
	*)	printf "$usage" "$version" "$channel" "$prefix" "$path2conda" "$path2pip"
		exit 1
		;;
	esac
done

name="$prefix$version-$channel"
if [[ $mpi != None ]]; then
	name+="-$mpi"
fi
if [[ "$condaInstallPath" != None ]]; then
	name="common-$name"
fi

# check version
if [[ $version != 2 && $version != 3 ]]; then
	printf "%s\n" "version has to be either 2 or 3." >&2
	exit 1
fi

# helpers ##############################################################

conda_create () {
	if [[ "$condaInstallPath" == None ]]; then
		conda create -n $@
	else
		conda create -p $@
	fi
}

conda_install () {
	if [[ "$condaInstallPath" == None ]]; then
		conda install -n "$name" -y $@ || conda upgrade -n "$name" -y $@
	else
		conda install -p "$name" -y $@ || conda upgrade -p "$name" -y $@
	fi
}

########################################################################

# TODO: this is stateful and changes the user preference
if [[ $channel == 'intel' ]]; then
	conda config --prepend channels intel
	conda config --append channels defaults
else
	conda config --prepend channels defaults
	conda config --append channels intel
fi
conda config --append channels conda-forge

# enter the conda prefix dir for installing
if [[ "$condaInstallPath" != None ]]; then
	mkdir -p "$condaInstallPath" && cd "$condaInstallPath"
fi

# create conda env
if [[ $channel == 'intel' ]]; then
	conda_create "$name" -c "$channel" intelpython${version}_core python=$version -y
else
	conda_create "$name" -c "$channel" python=$version -y
fi


if [[ "$condaInstallPath" == None ]]; then
    . activate "$name"
else
	. activate "$condaInstallPath/$name"
fi

conda_install -c mjuric pyslalib

# conda
if [[ -e "$path2conda" ]]; then
	# load names of packages
	temp=$(grep -v '#' "$path2conda")
	# flatten them to be space-separated
	temp=$(echo $temp)
	conda_install "$temp" pip
else
	printf "%s\n" "$path2conda not found. Skipped."
fi

# Python 2 only
if [[ $version == 2 ]]; then
	conda_install weave functools32 futures subprocess32 backports.weakref backports.functools_lru_cache backports_abc pathlib2
fi

# pip, and update pickleshare to prevent `ImportError: cannot import name path`
conda_install pip pickleshare
# pip
if [[ -e "$path2pip" ]]; then
	pip install -Ur "$path2pip"
else
	printf "%s\n" "$path2pip not found. Skipped."
fi

# mpich
if [[ $mpi == mpich || $mpi == openmpi ]]; then
	conda_install -c mpi4py mpi4py $mpi
elif [[ $mpi == cray && -n $NERSC_HOST ]]; then
	# TODO: better choice of this tempdir
	tempDir="$HOME/.mpi4py/$name/"
	mpi4pyVersion="3.0.0" #TODO
	mpiName="mpi4py-$mpi4pyVersion"

	mkdir -p "$tempDir" && cd "$tempDir"
	wget -qO- https://bitbucket.org/mpi4py/mpi4py/downloads/$mpiName.tar.gz | tar -xzf -
	cd $mpiName

	module swap PrgEnv-intel PrgEnv-gnu
	if [[ $NERSC_HOST == "cori" ]]; then
		python setup.py build --mpicc=$(which cc)
	elif [[ $NERSC_HOST == "edison" ]]; then
		LDFLAGS="-shared" python setup.py build --mpicc=$(which cc)
	fi
	python setup.py build_exe --mpicc="$(which cc) -dynamic"
	python setup.py install
	python setup.py install_exe
	if [[ "$condaInstallPath" != None ]]; then
		# back to original dir.
		cd "$condaInstallPath"
	else
		# cd to somewhere before rm tempDir
		cd "$HOME"
	fi
	rm -rf "$tempDir"
else
	conda_install -c intel mpi4py
fi

# Don't install ipython from intel channel. See https://software.intel.com/en-us/forums/intel-distribution-for-python/topic/704018
# conda_install -c defaults ipython

python -m ipykernel install --user --name "$name" --display-name "$name"

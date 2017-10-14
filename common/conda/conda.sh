#!/usr/bin/env bash

# xtrace if DEBUG
if [[ $DEBUG ]]; then
	set -x
fi

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
		conda install -n $@ || conda upgrade -n $@
	else
		conda install -p $@ || conda upgrade -p $@
	fi
}

########################################################################

# make intel's priority later than defaults
conda config --append channels intel
# for healpy & weave
conda config --append channels conda-forge
# for quaternion
conda config --append channels moble
# for pyslalib
conda config --append channels kadrlica

# enter the conda prefix dir for installing
if [[ "$condaInstallPath" != None ]]; then
	mkdir -p "$condaInstallPath" && cd "$condaInstallPath" || exit 1
fi

# create conda env
if [[ $channel == 'intel' ]]; then
	conda_create "$name" -c "$channel" intelpython${version}_core python=$version -y || exit 1
else
	conda_create "$name" -c "$channel" python=$version -y || exit 1
fi

. activate "$name" || exit 1

# conda
if [[ -e "$path2conda" ]]; then
	# load names of packages
	temp=$(grep -v '#' "$path2conda")
	# flatten them to be space-separated
	temp=$(echo $temp)
	conda_install "$name" -c "$channel" "$temp" -y || exit 1
else
	printf "%s\n" "$path2conda not found. Skipped."
fi
if [[ $channel == 'intel' ]]; then
	# ipython. See https://software.intel.com/en-us/forums/intel-distribution-for-python/topic/704018
	conda_install "$name" -c defaults ipython -y
	# Intel's scipy 0.19 has caused me some problem
	conda_install "$name" -c intel 'scipy<0.19' -y
fi
# weave
if [[ $version == 2 ]]; then
	conda_install "$name" weave -y
	# Backport of the functools module from Python 3.2.3 for use on 2.7
	conda_install "$name" functools32 -y
fi
# pyslalib
if [[ $(uname) == Darwin || $version == 3 ]]; then
	pip install -U pyslalib || exit 1
else
	# for linux, python 2
	conda_install "$name" -c kadrlica pyslalib -y || exit 1
fi
# pip
if [[ -e "$path2pip" ]]; then
	pip install -Ur "$path2pip" || exit 1
else
	printf "%s\n" "$path2pip not found. Skipped."
fi
# mpich
if [[ $mpi == mpich || $mpi == openmpi ]]; then
	conda_install "$name" -c mpi4py mpi4py $mpi -y || exit 1
elif [[ $mpi == cray && -n $NERSC_HOST ]]; then
	if [[ "$condaInstallPath" != None ]]; then
		tempDir="$SCRATCH/opt/mpi4py/$name/" #TODO: where? Check $SCRATCH
	else
		tempDir="$condaInstallPath/$name/mpi4py"
	fi
	mpi4pyVersion="2.0.0" #TODO
	mpiName="mpi4py-$mpi4pyVersion"

	mkdir -p $tempDir && cd $tempDir || exit 1
	wget -O - https://bitbucket.org/mpi4py/mpi4py/downloads/$mpiName.tar.gz | tar -xvzf - || exit 1
	cd $mpiName

	module swap PrgEnv-intel PrgEnv-gnu
	if [[ $NERSC_HOST == "cori" ]]; then
		python setup.py build --mpicc=$(which cc) || exit 1
	elif [[ $NERSC_HOST == "edison" ]]; then
		LDFLAGS="-shared" python setup.py build --mpicc=$(which cc) || exit 1
	fi
	python setup.py build_exe --mpicc="$(which cc) -dynamic" || exit 1
	python setup.py install || exit 1
	python setup.py install_exe || exit 1
else
	conda_install "$name" -c "$channel" mpi4py -y || exit 1
fi

# install jupyter widget extension
jupyter nbextension enable --py --sys-prefix widgetsnbextension || exit 1

# iPython kernel (seems that it should be installed using the root conda env.)
. activate root && python -m ipykernel install --user --name "$name" --display-name "$name" || exit 1

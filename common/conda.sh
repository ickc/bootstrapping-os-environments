#!/usr/bin/env bash

# xtrace if DEBUG
if [[ $DEBUG ]]; then
	set -x
fi

usage="${BASH_SOURCE[0]} [-h] [-v version] [-c channel] [-p prefix] [-C conda-path] [-P pip-path] [-m mpi] --- create conda environments

where:
	-h	show this help message
	-v	python version. 2 or 3. Default: %s
	-c	conda channel. e.g. intel, defaults. Default: %s
	-p	prefix of the name of environment. Default: %s
	-C	path to a file that contains the list of conda packages to be installed. Default: %s
	-P	path to a file that contains the list of pip packages to be installed. Default: %s
	-m	custom version of mpi4py if sepecified. e.g. mpich/openmpi to use mpich/openmpi from the mpi4py channel; cray to custom build using cray compiler.
"

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# getopts ######################################################################

# reset getopts
OPTIND=1

# Initialize parameters
version=3
channel=defaults
prefix=all
path2conda="$DIR/conda.txt"
path2pip="$DIR/pip.txt"
mpi=None

# get the options
while getopts "v:c:p:C:P:m:h" opt; do
	case "$opt" in
	v)	version="$OPTARG"
		;;
	c)	channel="$OPTARG"
		;;
	p)	prefix="$OPTARG"
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

if [[ $mpi == None ]]; then
	name="$prefix$version-$channel"
else
	name="$prefix$version-$channel-$mpi"
fi

# check version
if [[ $version != 2 && $version != 3 ]]; then
	printf "%s\n" "version has to be either 2 or 3." >&2
	exit 1
fi

########################################################################

# for healpy & weave
conda config --append channels conda-forge
# for pyephem
conda config --append channels astropy
# for pythonpy
conda config --append channels bioconda
# for pyslalib
conda config --append channels kadrlica
# for terminaltables
conda config --append channels rogerramos

# create conda env
if [[ $channel == 'intel' ]]; then
	conda create -n "$name" -c "$channel" intelpython${version}_core python=$version -y || exit 1
else
	conda create -n "$name" -c "$channel" python=$version -y || exit 1
fi

. activate "$name" || exit 1

# conda
if [[ -e "$path2conda" ]]; then
	grep -v '#' "$path2conda" | xargs conda install -c "$channel" -y || exit 1
else
	printf "%s\n" "$path2conda not found. Skipped."
fi
# pyslalib
if [[ $(uname) == Darwin || $version == 3 ]]; then
	pip install -U pyslalib || exit 1
else
	# for linux, python 2
	conda install -c kadrlica pyslalib -y || exit 1
fi
# pip
if [[ -e "$path2pip" ]]; then
	pip install -Ur "$path2pip" || exit 1
else
	printf "%s\n" "$path2pip not found. Skipped."
fi
# mpich
if [[ $mpi == mpich || $mpi == openmpi ]]; then
	conda install -c mpi4py mpi4py $mpi -y || exit 1
elif [[ $mpi == cray && -n $NERSC_HOST ]]; then
	tempDir="$SCRATCH/opt/mpi4py/$name/" #TODO: where? Check $SCRATCH
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
	conda install -c "$channel" mpi4py -y || exit 1
fi

# iPython kernel
python -m ipykernel install --user --name "$name" --display-name "${name^^}" || exit 1

# install jupyter widget extension
jupyter nbextension enable --py --sys-prefix widgetsnbextension || exit 1

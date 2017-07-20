#!/usr/bin/env bash

# xtrace if DEBUG
if [[ $DEBUG ]]; then
	set -x
fi

usage="./$(basename "$0") [-h] [-v version] [-c channel] [-p prefix] --- create conda environments

where:
	-h	show this help message
	-v	python version. 2 or 3. Default: %s
	-c	conda channel. e.g. intel, defaults. Default: %s
	-p	prefix of the name of environment. Default: %s
	-C	path to a file that contains the list of conda packages to be installed. Default: %s
	-P	path to a file that contains the list of pip packages to be installed. Default: %s
	-m	custom version of mpi4py if sepecified. e.g. mpich to use mpich from the mpi4py channel; cray to custom build using cray compiler.
"

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# getopts ######################################################################

# reset getopts
OPTIND=1

# Initialize parameters
version=2
channel=defaults
prefix=ab
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

# create conda env
if [[ $channel == 'intel' ]]; then
	conda create -n "$name" -c "$channel" intelpython${version}_core python=$version -y
else
	conda create -n "$name" -c "$channel" python=$version -y
fi

. activate "$name"

# conda
grep -v '#' "$path2conda" | xargs conda install -c "$channel" -y
# pip
pip install -Ur "$path2pip"
# mpich
if [[ $mpi == mpich ]]; then
	conda install -c mpi4py mpi4py mpich -y
elif [[ $mpi == cray && -n $NERSC_HOST ]]; then
	tempDir="$HOME/.mpi4py/" #TODO
	mpi4pyVersion="2.0.0" #TODO
	mpiName="mpi4py-$mpi4pyVersion"

	mkdir -p $tempDir && cd $tempDir
	wget -O - https://bitbucket.org/mpi4py/mpi4py/downloads/$mpiName.tar.gz | tar -xvzf -
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
	rm -r $tempDir #TODO
else
	conda install -c "$channel" mpi4py -y
fi

# iPython kernel
python -m ipykernel install --user --name "$name" --display-name "${name^^}"

# install jupyter widget extension
jupyter nbextension enable --py --sys-prefix widgetsnbextension

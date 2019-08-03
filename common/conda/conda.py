#!/usr/bin/env python

import argparse
import platform
import sys

__version__ = '0.1.1'


def filter_line(line):
    line = line.strip()
    if line.startswith('#'):
        line = ''
    return line


def read_env(path):
    with open(path, 'r') as f:
        return list(filter(None, map(filter_line, f)))


def cook_yaml(
    python_version=2,
    channel='defaults',
    name='ab',
    prefix=None,
    conda_path='conda.txt',
    pip_path='pip.txt',
    mpi=None
):
    conda_envs = read_env(conda_path)
    pip_envs = read_env(pip_path)

    dict_ = dict()

    # channel
    dict_['channels'] = ['intel', 'defaults', 'conda-forge'] if channel == 'intel' else ['defaults', 'intel', 'conda-forge']

    dict_['dependencies'] = conda_envs
    if platform.system() == 'Darwin':
        dict_['dependencies'] += ['python.app']

    # python_version
    dict_['dependencies'].append(f'python={python_version}')
    if channel == 'intel':
        dict_['dependencies'].append(f'intelpython{python_version}_core')
    if python_version == 2:
        dict_['dependencies'] += [
            'weave',
            'functools32',
            'futures',
            'subprocess32',
            'backports.weakref',
            'backports.functools_lru_cache',
            'backports_abc',
            'pathlib2'
        ]
        # conda cannot resolve subprocess32 and mypy in python2
        try:
            dict_['dependencies'].remove('mypy')
        except ValueError:
            pass

    if mpi == 'cray':
        print('Install mpi4py compiled using Cray compiler from cray-mpi4py.sh', file=sys.stderr)
    elif mpi in ('mpich', 'openmpi'):
        dict_['dependencies'].append(f'mpi4py::{mpi}')
        dict_['dependencies'].append('mpi4py::mpi4py')
    else:
        dict_['dependencies'].append('mpi4py')

    dict_['dependencies'].append({
        'pip': pip_envs
    })

    # name
    dict_['name'] = f'{name}{python_version}-{channel}' + ('' if mpi is None else f'-{mpi}')
    # prefix
    if prefix:
        dict_['prefix'] = prefix
    return dict_


def cli():
    parser = argparse.ArgumentParser(description='Generate conda environment YAML file.')

    parser.add_argument('-o', '--yaml', type=argparse.FileType('w'), default=sys.stdout,
                        help="Output YAML.")
    parser.add_argument('-v', '--version', type=int, default=2,
                        help='python version. 2 or 3. Default: 2')
    parser.add_argument('-c', '--channel', default='defaults',
                        help='conda channel. e.g. intel, defaults. Default: defaults')
    parser.add_argument('-n', '--name', default='ab',
                        help='prefix of the name of environment. Default: ab')
    parser.add_argument('-p', '--prefix',
                        help="Full path to conda environment prefix. If not specified, conda's default will be used.")
    parser.add_argument('-C', '--conda-txt',
                        help="path to a file that contains the list of conda packages to be installed.")
    parser.add_argument('-P', '--pip-txt',
                        help="path to a file that contains the list of pip packages to be installed.")
    parser.add_argument('-m', '--mpi',
                        help="custom version of mpi4py if sepecified. e.g. mpich/openmpi to use mpich/openmpi from the mpi4py channel; cray to custom build using cray compiler.")

    parser.add_argument('-V', action='version',
                        version='%(prog)s {}'.format(__version__))

    args = parser.parse_args()

    dict_ = cook_yaml(
        python_version=args.version,
        channel=args.channel,
        name=args.name,
        prefix=args.prefix,
        conda_path=args.conda_txt,
        pip_path=args.pip_txt,
        mpi=args.mpi,
    )
    try:
        import yaml
        yaml.dump(dict_, args.yaml, default_flow_style=False)
    except ImportError:
        import json
        print(json.dumps(dict_), file=args.yaml)


if __name__ == "__main__":
    cli()

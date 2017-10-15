#!/usr/bin/env bash

# install conda environments

# ab2-defaults
../common/conda/conda.sh &&
# ab2-intel
../common/conda/conda.sh -c intel &&
# ab3-defaults
../common/conda/conda.sh -v 3 &&
# ab3-intel
../common/conda/conda.sh -c intel -v 3 &&

# all2-defaults
../common/conda/conda.sh -n all -C ../common/conda/conda-all.txt -P ../common/conda/pip-all.txt &&
# all2-intel
../common/conda/conda.sh -n all -C ../common/conda/conda-all.txt -P ../common/conda/pip-all.txt -c intel &&
# all3-defaults
../common/conda/conda.sh -n all -C ../common/conda/conda-all.txt -P ../common/conda/pip-all.txt -v 3 &&
# all3-intel
../common/conda/conda.sh -n all -C ../common/conda/conda-all.txt -P ../common/conda/pip-all.txt -c intel -v 3

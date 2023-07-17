SHELL = /usr/bin/env bash

_python ?= python
# for bump2version, valid options are: major, minor, patch
PART ?= patch

PANDOC = pandoc
pandocArgs = --toc -M date="`date "+%B %e, %Y"`" --filter=pantable --wrap=none
RSTs = CHANGELOG.rst README.rst

# Main Targets #################################################################

.PHONY: docs api html test clean

docs: $(RSTs)
	$(MAKE) html
api: docs/api/
html: dist/docs/

test:
	rm -f .coverage*
	coverage run -m pytest -vv $(PYTESTARGS) \
		tests
	coverage combine
	coverage report
	coverage html

clean:
	rm -f $(RSTs) .coverage*

# docs #########################################################################

README.rst: docs/README.md docs/badges.csv
	printf \
		"%s\n\n" \
		".. This is auto-generated from \`$<\`. Do not edit this file directly." \
		> $@
	cd $(<D); \
	$(PANDOC) $(pandocArgs) $(<F) -V title='pantable Documentation' -s -t rst \
		>> ../$@

%.rst: %.md
	printf \
		"%s\n\n" \
		".. This is auto-generated from \`$<\`. Do not edit this file directly." \
		> $@
	$(PANDOC) $(pandocArgs) $< -s -t rst >> $@

docs/api/:
	sphinx-apidoc \
		--maxdepth 6 \
		--force \
		--separate \
		--module-first \
		--implicit-namespaces \
		--doc-project API \
		--output-dir $@ src/bsos

dist/docs/:
	sphinx-build -E -b dirhtml docs dist/docs
	# sphinx-build -b linkcheck docs dist/docs

# maintenance ##################################################################

.PHONY: pypi pypiManual gh-pages pep8 flake8 pylint
# Deploy to PyPI
## by CI, properly git tagged
pypi:
	git push origin v0.1.0
## Manually
pypiManual:
	rm -rf dist
	poetry build
	twine upload dist/*

gh-pages:
	ghp-import --no-jekyll --push dist/docs

# check python styles
pep8:
	pycodestyle . --ignore=E501
flake8:
	flake8 . --ignore=E501
pylint:
	pylint bsos
format:
	black . && isort .
	find \! -path '*/.ipynb_checkpoints/*' -name '*.ipynb' -exec jupytext --sync --pipe black --pipe 'isort - --treat-comment-as-code "# %%" --float-to-top' {} +
	python src/bsos/core.py common/conda/conda.csv common/conda/conda.csv
print-%:
	$(info $* = $($*))

# poetry #######################################################################

.PHONY: editable
editable:
	$(_python) -m pip install --no-dependencies -e .

# releasing ####################################################################

.PHONY: bump
bump:
	bump2version $(PART)
	git push --follow-tags

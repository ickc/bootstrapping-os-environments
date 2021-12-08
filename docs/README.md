---
title:	naive_cookiecutter—just a naive cookiecutter to boostrap Python project
...

``` {.table}
---
header: false
markdown: true
include: badges.csv
...
```

# Introduction

naive_cookiecutter is just a naive cookiecutter to boostrap Python project.

# Instruction

```bash
NEW_NAME=...
NEW_NAME_UPPER="$(echo $NEW_NAME | tr '[:lower:]' '[:upper:]')"
find . \! -path '*/.git/*' -type f -exec sed -i "s/naive_cookiecutter/$NEW_NAME/g" {} +
find . \! -path '*/.git/*' -type f -exec sed -i "s/NAIVE_COOKIECUTTER/$NEW_NAME_UPPER/g" {} +
mv src/naive_cookiecutter "src/$NEW_NAME"
```

- update title in
    - `docs/README.md`
    - `pyproject.toml`

Optionally also sed

- version `0.1.0`
- GitHub username `ickc`
- author name `Kolen Cheung`
- author email `christian.kolen@gmail.com`
- copyright year 2021

# Copy

```bash
rsync -av --stats --exclude .git ./ $TARGET_GIT_REPO_DIRECTORY
```

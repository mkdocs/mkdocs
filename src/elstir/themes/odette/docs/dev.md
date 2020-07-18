# Developer guide

The project uses [Poetry](https://poetry.eustace.io/). To install the package with all dependencies in development mode, clone the repo and run `poetry install` in the cloned repo directory.


## Releasing a new version

### Automatically

Just use [git flow](https://github.com/nvie/gitflow) to make a release, and the new version will be published to PyPI automatically by Travis CI:

```shell
$ git flow release start 0.7.8
$ poetry version
$ git add poetry.toml
$ git commit -m "Bump version."
$ git flow release finish 0.7.8
$ git push --all && git push --tags
```

### Manually

If for some reason you want to publish the release manually, use [poetry publish](https://poetry.eustace.io/docs/cli/#publish) command:

```shell
$ poetry publish --build
```

## Building the docs locally

```shell
$ poetry run mkdocs serve
```

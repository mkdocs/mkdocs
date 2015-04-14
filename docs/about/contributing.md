# Contributing to MkDocs

An introduction to contributing to the MkDocs project.

The MkDocs project welcomes, and depends, on contributions from
developers and users in the open source community. Contributions
can be made in a number of ways, a few examples are:

- Code patches via pull requests
- Documentation improvements
- Bug reports and patch reviews

## Reporting an issue?

Please include as much detail as you can. Let us know your
platform and MkDocs version. If the problem is visual (for
example a theme or design issue) please add a screenshot and if
you get an error please include the the full error and traceback.


## Installing for development

First you'll need to fork and clone the repository. Once you have
a local copy, run the following command. It is recommended that
you do this within a [virtualenv](virtualenv).

```text
pip install --editable .
```

This will install MkDocs in development mode which binds the
`mkdocs` command to the git repository.


## Running the tests

To run the tests, it is recommended that you use [Tox](tox). This
just needs to be pip installed and then the test suite can be ran
for MkDocs but running the command `tox` in the root of your
MkDocs repository.

It will attempt to run the tests against all of the Python
versions we support. So don't be concerned if you are missing
some and they fail. The rest will be verified by [Travis](travis)
when you submit a pull request.

## Submitting Pull Requests

Once you are happy with your changes or you are ready for some
feedback, push it to your fork and send a pull request. For a
change to be accepted it will most likely need to have tests and
documentation if it is a new feature.

[virtualenv]: https://virtualenv.pypa.io/en/latest/userguide.html
[tox]: https://tox.readthedocs.org/en/latest/
[travis]: https://travis-ci.org/repositories

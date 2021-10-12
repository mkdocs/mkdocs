# Contributing to MkDocs

An introduction to contributing to the MkDocs project.

The MkDocs project welcomes, and depends, on contributions from developers and
users in the open source community. Contributions can be made in a number of
ways, a few examples are:

- Code patches via pull requests
- Documentation improvements
- Bug reports and patch reviews

For information about available communication channels please refer to the
[README](https://github.com/mkdocs/mkdocs/blob/master/README.md) file in our
GitHub repository.

## Code of Conduct

Everyone interacting in the MkDocs project's codebases, issue trackers, chat
rooms, and mailing lists is expected to follow the [PyPA Code of Conduct].

## Reporting an Issue

Please include as much detail as you can. Let us know your platform and MkDocs
version. If the problem is visual (for example a theme or design issue) please
add a screenshot and if you get an error please include the full error and
traceback.

## Testing the Development Version

If you want to just install and try out the latest development version of
MkDocs you can do so with the following command. This can be useful if you
want to provide feedback for a new feature or want to confirm if a bug you
have encountered is fixed in the git master. It is **strongly** recommended
that you do this within a [virtualenv].

```bash
pip install https://github.com/mkdocs/mkdocs/archive/master.tar.gz
```

## Installing for Development

First you'll need to fork and clone the repository. Once you have a local
copy, run the following command. It is **strongly** recommended that you do
this within a [virtualenv].

```bash
pip install --editable .
```

This will install MkDocs in development mode which binds the `mkdocs` command
to the git repository.

## Running the tests

To run the tests, it is recommended that you use [tox].

Install Tox using [pip] by running the command `pip install tox`.
Then the test suite can be run for MkDocs by running the command `tox` in the
root of your MkDocs repository.

It will attempt to run the tests against all of the Python versions we
support. So don't be concerned if you are missing some and they fail. The rest
will be verified by [Github Actions] when you submit a pull request.

## Translating themes

To localize a theme to your favorite language, follow the guide on [Translating
Themes]. We welcome translation Pull Requests!

## Submitting Pull Requests

If you're considering a large code contribution to MkDocs, please prefer to
open an issue first to get early feedback on the idea.

Once you think the code is ready to be reviewed, push
it to your fork and send a pull request. For a change to be accepted it will
most likely need to have tests and documentation if it is a new feature.

### Submitting changes to the builtin themes

When installed with `i18n` support (`pip install mkdocs[i18n]`), MkDocs allows
themes to support being translated into various languages (referred to as
locales) if they respect [Jinja's i18n extension] by wrapping text placeholders
with `{% trans %}` and `{% endtrans %}` tags.

Each time a translatable text placeholder is added, removed or changed in a
theme template, the theme's Portable Object Template (`pot`) file needs to be
updated by running the `extract_messages` command. For example, to update the
`pot` file of the `mkdocs` theme, run the following command:

```bash
python setup.py extract_messages -t mkdocs
```

The updated `pot` file should be included in a PR with the updated template.
The updated `pot` file will allow translation contributors to propose the
translations needed for their preferred language. See the guide on [Translating
Themes] for details.

!!! Note

    Contributors are not expected to provide translations with their changes to
    a theme's templates. However, they are expected to include an updated `pot`
    file so that everything is ready for translators to do their job.

[virtualenv]: https://virtualenv.pypa.io/en/latest/user_guide.html
[pip]: https://pip.pypa.io/en/stable/
[tox]: https://tox.readthedocs.io/en/latest/
[Github Actions]: https://docs.github.com/actions
[PyPA Code of Conduct]: https://www.pypa.io/en/latest/code-of-conduct/
[Translating Themes]: ../dev-guide/translations.md
[Jinja's i18n extension]: https://jinja.palletsprojects.com/en/latest/extensions/#i18n-extension

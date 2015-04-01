"""
# MkDocs Integration tests

This is a simple integration test that builds the MkDocs
documentation against all of the builtin themes.

From the root of the MkDocs git repo, use:

    python -m mkdocs.tests.integration --help


TODOs
    - Build with different configuration options.
    - Build documentation other than just MkDocs as it is relatively simple.
"""

from __future__ import print_function

import os
import click
import contextlib
import sys
try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO

from mkdocs import main as mkdocs_main

MKDOCS_CONFIG = os.path.join(os.path.dirname(__file__), '../../mkdocs.yml')
MKDOCS_THEMES = os.listdir(os.path.join(os.path.dirname(__file__), '../themes'))


@contextlib.contextmanager
def capture():
    oldout, olderr = sys.stdout, sys.stderr
    try:
        out = [StringIO(), StringIO()]
        sys.stdout, sys.stderr = out
        yield out
    finally:
        sys.stdout, sys.stderr = oldout, olderr
        out[0] = out[0].getvalue()
        out[1] = out[1].getvalue()


def build(theme_name, output=None, config=None, quiet=False):
    """
    Given a theme name and output directory use the configuration
    for the MkDocs documentation and overwrite the site_dir and
    theme. If no output is provided, serve the documentation on
    each theme, one at a time.
    """

    serve = output is None
    options = {}

    if not serve:
        if not os.path.exists(output):
            os.makedirs(output)
        options['site_dir'] = os.path.join(output, theme_name)

    if config is None:
        config = MKDOCS_CONFIG

    if not quiet:
        print("Using config: {0}".format(config))

    options['config'] = config
    options['theme'] = theme_name

    if serve:
        if not quiet:
            print("Serving {0}".format(theme_name))
        try:
            mkdocs_main.main('serve', None, options)
        except KeyboardInterrupt:
            return
    else:
        if not quiet:
            print("Building {0}".format(theme_name))

        with capture() as out:
            mkdocs_main.main('build', None, options)
            mkdocs_main.main('json', None, options)

        if not quiet:
            print(''.join(out))


@click.command()
@click.option('--output',
              help="The output directory to use when building themes",
              type=click.Path(file_okay=False, writable=True))
@click.option('--config',
              help="The MkDocs project config to use.",
              type=click.Path(dir_okay=False))
@click.option('--quiet', is_flag=True)
def main(output=None, config=None, quiet=False):

    for theme in sorted(MKDOCS_THEMES):

        build(theme, output, config, quiet)

    print("The theme builds are available in {0}".format(output))

if __name__ == '__main__':
    main()

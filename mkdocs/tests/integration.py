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

from six.moves import cStringIO

from mkdocs import cli, config, serve, build, utils

MKDOCS_CONFIG = os.path.join(os.path.dirname(__file__), '../../mkdocs.yml')
MKDOCS_THEMES = utils.get_theme_names()


@contextlib.contextmanager
def capture_stdout():
    oldout, olderr = sys.stdout, sys.stderr
    try:
        out = [cStringIO(), cStringIO()]
        sys.stdout, sys.stderr = out
        yield out
    finally:
        sys.stdout, sys.stderr = oldout, olderr
        out[0] = out[0].getvalue()
        out[1] = out[1].getvalue()


def run_build(theme_name, output=None, config_file=None, quiet=False):
    """
    Given a theme name and output directory use the configuration
    for the MkDocs documentation and overwrite the site_dir and
    theme. If no output is provided, serve the documentation on
    each theme, one at a time.
    """

    should_serve = output is None
    options = {}

    if not serve:
        if not os.path.exists(output):
            os.makedirs(output)
        options['site_dir'] = os.path.join(output, theme_name)

    if config_file is None:
        config_file = open(MKDOCS_CONFIG, 'rb')

    if not quiet:
        print("Using config: {0}".format(config_file))

    cli.configure_logging()
    conf = config.load_config(config_file=config_file, theme=theme_name)

    if should_serve:
        if not quiet:
            print("Serving {0}".format(theme_name))
        try:
            serve.serve(conf)
        except KeyboardInterrupt:
            return
    else:
        if not quiet:
            print("Building {0}".format(theme_name))

        try:
            with capture_stdout() as out:
                build.build(conf)
                build.build(conf, dump_json=True)
        except Exception:
            print("Failed building {0}".format(theme_name), file=sys.stderr)
            raise

        if not quiet:
            print(''.join(out))


@click.command()
@click.option('--output',
              help="The output directory to use when building themes",
              type=click.Path(file_okay=False, writable=True))
@click.option('--config',
              help="The MkDocs project config to use.",
              type=click.File('rb'))
@click.option('--quiet', is_flag=True)
def main(output=None, config=None, quiet=False):

    for theme in sorted(MKDOCS_THEMES):

        run_build(theme, output, config, quiet)

    print("The theme builds are available in {0}".format(output))

if __name__ == '__main__':
    main()

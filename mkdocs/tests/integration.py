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

import click
import logging
import os
import sys

from mkdocs import cli, config, build, utils

DIR = os.path.dirname(__file__)
MKDOCS_CONFIG = os.path.abspath(os.path.join(DIR, '../../mkdocs.yml'))
MKDOCS_THEMES = utils.get_theme_names()


def silence_logging(is_verbose=False):
    '''When a --verbose flag is passed, increase the verbosity of mkdocs'''

    logger = logging.getLogger('mkdocs')
    logger.setLevel(logging.ERROR)


def run_build(theme_name, output, config_file, quiet):
    """
    Given a theme name and output directory use the configuration
    for the MkDocs documentation and overwrite the site_dir and
    theme. If no output is provided, serve the documentation on
    each theme, one at a time.
    """

    options = {
        'theme': theme_name,
    }

    if config_file is None:
        config_file = open(MKDOCS_CONFIG, 'rb')
        if not quiet:
            print("Using config: {0}".format(config_file.name))

    if not os.path.exists(output):
        os.makedirs(output)
    options['site_dir'] = os.path.join(output, theme_name)

    if not quiet:
        print("Building {0}".format(theme_name))

    try:
        conf = config.load_config(config_file=config_file, **options)
        config_file.close()
        build.build(conf)
        build.build(conf, dump_json=True)
    except Exception:
        print("Error building: {0}".format(theme_name), file=sys.stderr)
        raise


@click.command()
@click.option('--output',
              help="The output directory to use when building themes",
              type=click.Path(file_okay=False, writable=True))
@click.option('--config-file',
              help="The MkDocs project config to use.",
              type=click.File('rb'))
@click.option('--quiet', is_flag=True)
def main(output=None, config_file=None, quiet=False):

    if quiet:
        silence_logging()
    else:
        cli.configure_logging()

    for theme in sorted(MKDOCS_THEMES):

        run_build(theme, output, config_file, quiet)

    print("The theme builds are available in {0}".format(output))

if __name__ == '__main__':
    main()

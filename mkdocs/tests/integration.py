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

from __future__ import print_function, unicode_literals

import click
import os
import subprocess

from mkdocs import utils

DIR = os.path.dirname(__file__)
MKDOCS_CONFIG = os.path.abspath(os.path.join(DIR, '../../mkdocs.yml'))
MKDOCS_THEMES = utils.get_theme_names()
TEST_PROJECTS = os.path.abspath(os.path.join(DIR, 'integration'))


@click.command()
@click.option('--output',
              help="The output directory to use when building themes",
              type=click.Path(file_okay=False, writable=True),
              required=True)
def main(output=None):

    for theme in sorted(MKDOCS_THEMES):
        project_dir = os.path.dirname(MKDOCS_CONFIG)
        out = os.path.join(output, theme)
        command = ['mkdocs', 'build', '-v', '--site-dir', out, '--theme', theme]
        subprocess.check_call(command, cwd=project_dir)

    for project in os.listdir(TEST_PROJECTS):

        project_dir = os.path.join(TEST_PROJECTS, project)
        out = os.path.join(output, project)
        command = ['mkdocs', 'build', '--site-dir', out]
        subprocess.check_call(command, cwd=project_dir)

    print("Theme and integration builds are available in {0}".format(output))

if __name__ == '__main__':
    main()

"""
# elstir Integration tests

This is a simple integration test that builds the elstir
documentation against all of the builtin themes.

From the root of the elstir git repo, use:

    python -m elstir.tests.integration --help


TODOs
    - Build with different configuration options.
    - Build documentation other than just elstir as it is relatively simple.
"""


import click
import logging
import os
import subprocess

from elstir import utils

log = logging.getLogger('elstir')

DIR = os.path.dirname(__file__)
elstir_CONFIG = os.path.abspath(os.path.join(DIR, '../../elstir.yml'))
elstir_THEMES = utils.get_theme_names()
TEST_PROJECTS = os.path.abspath(os.path.join(DIR, 'integration'))


@click.command()
@click.option('--output',
              help="The output directory to use when building themes",
              type=click.Path(file_okay=False, writable=True),
              required=True)
def main(output=None):

    log.propagate = False
    stream = logging.StreamHandler()
    formatter = logging.Formatter(
        "\033[1m\033[1;32m *** %(message)s *** \033[0m")
    stream.setFormatter(formatter)
    log.addHandler(stream)
    log.setLevel(logging.DEBUG)

    base_cmd = ['elstir', 'build', '-s', '-v', '--site-dir', ]

    log.debug("Building installed themes.")
    for theme in sorted(elstir_THEMES):
        log.debug("Building theme: {}".format(theme))
        project_dir = os.path.dirname(elstir_CONFIG)
        out = os.path.join(output, theme)
        command = base_cmd + [out, '--theme', theme]
        subprocess.check_call(command, cwd=project_dir)

    log.debug("Building test projects.")
    for project in os.listdir(TEST_PROJECTS):
        log.debug("Building test project: {}".format(project))
        project_dir = os.path.join(TEST_PROJECTS, project)
        out = os.path.join(output, project)
        command = base_cmd + [out, ]
        subprocess.check_call(command, cwd=project_dir)

    log.debug("Theme and integration builds are in {}".format(output))


if __name__ == '__main__':
    main()

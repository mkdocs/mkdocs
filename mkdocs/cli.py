#!/usr/bin/env python
# coding: utf-8

import logging
import click

from mkdocs import __version__
from mkdocs import build
from mkdocs import gh_deploy
from mkdocs import new
from mkdocs import serve
from mkdocs import utils
from mkdocs import exceptions
from mkdocs.config import load_config

log = logging.getLogger(__name__)


def configure_logging(log_name='mkdocs', level=logging.INFO):
    '''When a --verbose flag is passed, increase the verbosity of mkdocs'''

    logger = logging.getLogger(log_name)
    logger.propagate = False
    stream = logging.StreamHandler()
    formatter = logging.Formatter("%(levelname)-7s -  %(message)s ")
    stream.setFormatter(formatter)
    logger.addHandler(stream)

    logger.setLevel(level)


clean_help = "Remove old files from the site_dir before building"
config_file_help = "Provide a specific MkDocs config"
dev_addr_help = ("IP address and port to serve documentation locally (default: "
                 "localhost:8000)")
strict_help = ("Enable strict mode. This will cause MkDocs to abort the build "
               "on any warnings.")
theme_help = "The theme to use when building your documentation."
theme_choices = utils.get_theme_names()
site_dir_help = "The directory to output the result of the documentation build."
reload_help = "Enable and disable the live reloading in the development server."
commit_message_help = ("A commit message to use when commiting to the "
                       "Github Pages remote branch")
remote_branch_help = ("The remote branch to commit to for Github Pages. This "
                      "overrides the value specified in config")


@click.group(context_settings={'help_option_names': ['-h', '--help']})
@click.option('-v', '--verbose', is_flag=True, help="Enable verbose output")
@click.version_option(__version__, '-V', '--version')
def cli(verbose):
    """
    MkDocs - Project documentation with Markdown.
    """

    if verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO

    configure_logging(level=level)


@cli.command(name="serve")
@click.option('-f', '--config-file', type=click.File('rb'), help=config_file_help)
@click.option('-a', '--dev-addr', help=dev_addr_help, metavar='<IP:PORT>')
@click.option('-s', '--strict', is_flag=True, help=strict_help)
@click.option('-t', '--theme', type=click.Choice(theme_choices), help=theme_help)
@click.option('--livereload/--no-livereload', default=True, help=reload_help)
def serve_command(dev_addr, config_file, strict, theme, livereload):
    """Run the builtin development server"""

    logging.getLogger('tornado').setLevel(logging.WARNING)

    try:
        serve.serve(
            config_file=config_file,
            dev_addr=dev_addr,
            strict=strict,
            theme=theme,
            livereload=livereload,
        )
    except exceptions.ConfigurationError as e:
        # Avoid ugly, unhelpful traceback
        raise SystemExit('\n' + str(e))


@cli.command(name="build")
@click.option('-c', '--clean', is_flag=True, help=clean_help)
@click.option('-f', '--config-file', type=click.File('rb'), help=config_file_help)
@click.option('-s', '--strict', is_flag=True, help=strict_help)
@click.option('-t', '--theme', type=click.Choice(theme_choices), help=theme_help)
@click.option('-d', '--site-dir', type=click.Path(), help=site_dir_help)
def build_command(clean, config_file, strict, theme, site_dir):
    """Build the MkDocs documentation"""
    try:
        build.build(load_config(
            config_file=config_file,
            strict=strict,
            theme=theme,
            site_dir=site_dir
        ), clean_site_dir=clean)
    except exceptions.ConfigurationError as e:
        # Avoid ugly, unhelpful traceback
        raise SystemExit('\n' + str(e))


@cli.command(name="json")
@click.option('-c', '--clean', is_flag=True, help=clean_help)
@click.option('-f', '--config-file', type=click.File('rb'), help=config_file_help)
@click.option('-s', '--strict', is_flag=True, help=strict_help)
@click.option('-d', '--site-dir', type=click.Path(), help=site_dir_help)
def json_command(clean, config_file, strict, site_dir):
    """Build the MkDocs documentation to JSON files

    Rather than building your documentation to HTML pages, this
    outputs each page in a simple JSON format. This command is
    useful if you want to index your documentation in an external
    search engine.
    """

    log.warning("The json command is deprcated and will be removed in a future "
                "MkDocs release. For details on updating: "
                "http://www.mkdocs.org/about/release-notes/")

    try:
        build.build(load_config(
            config_file=config_file,
            strict=strict,
            site_dir=site_dir
        ), dump_json=True, clean_site_dir=clean)
    except exceptions.ConfigurationError as e:
        # Avoid ugly, unhelpful traceback
        raise SystemExit('\n' + str(e))


@cli.command(name="gh-deploy")
@click.option('-c', '--clean', is_flag=True, help=clean_help)
@click.option('-f', '--config-file', type=click.File('rb'), help=config_file_help)
@click.option('-m', '--message', help=commit_message_help)
@click.option('-b', '--remote-branch', help=remote_branch_help)
def gh_deploy_command(config_file, clean, message, remote_branch):
    """Deply your documentation to GitHub Pages"""
    try:
        config = load_config(
            config_file=config_file,
            remote_branch=remote_branch
        )
        build.build(config, clean_site_dir=clean)
        gh_deploy.gh_deploy(config, message=message)
    except exceptions.ConfigurationError as e:
        # Avoid ugly, unhelpful traceback
        raise SystemExit('\n' + str(e))


@cli.command(name="new")
@click.argument("project_directory")
def new_command(project_directory):
    """Create a new MkDocs project"""
    new.new(project_directory)

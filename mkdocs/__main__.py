#!/usr/bin/env python
# coding: utf-8

from __future__ import unicode_literals
import logging
import click
import socket

from mkdocs import __version__
from mkdocs import utils
from mkdocs import exceptions
from mkdocs import config
from mkdocs.commands import build, gh_deploy, new, serve

log = logging.getLogger(__name__)

# Disable the warning that Click displays (as of Click version 5.0) when users
# use unicode_literals in Python 2.
# See http://click.pocoo.org/dev/python3/#unicode-literals for more details.
click.disable_unicode_literals_warning = True


class State(object):
    ''' Maintain logging level.'''

    def __init__(self, log_name='mkdocs', level=logging.INFO):
        self.logger = logging.getLogger(log_name)
        self.logger.propagate = False
        stream = logging.StreamHandler()
        formatter = logging.Formatter("%(levelname)-7s -  %(message)s ")
        stream.setFormatter(formatter)
        self.logger.addHandler(stream)

        self.logger.setLevel(level)


pass_state = click.make_pass_decorator(State, ensure=True)


def verbose_option(f):
    def callback(ctx, param, value):
        state = ctx.ensure_object(State)
        if value:
            state.logger.setLevel(logging.DEBUG)
    return click.option('-v', '--verbose',
                        is_flag=True,
                        expose_value=False,
                        help='Enable verbose output',
                        callback=callback)(f)


def quiet_option(f):
    def callback(ctx, param, value):
        state = ctx.ensure_object(State)
        if value:
            state.logger.setLevel(logging.ERROR)
    return click.option('-q', '--quiet',
                        is_flag=True,
                        expose_value=False,
                        help='Silence warnings',
                        callback=callback)(f)


def common_options(f):
    f = verbose_option(f)
    f = quiet_option(f)
    return f


clean_help = "Remove old files from the site_dir before building (the default)."
config_help = "Provide a specific MkDocs config"
dev_addr_help = ("IP address and port to serve documentation locally (default: "
                 "localhost:8000)")
strict_help = ("Enable strict mode. This will cause MkDocs to abort the build "
               "on any warnings.")
theme_dir_help = "The theme directory to use when building your documentation."
theme_help = "The theme to use when building your documentation."
theme_choices = utils.get_theme_names()
site_dir_help = "The directory to output the result of the documentation build."
reload_help = "Enable the live reloading in the development server (this is the default)"
no_reload_help = "Disable the live reloading in the development server."
dirty_reload_help = "Enable the live reloading in the development server, but only re-build files that have changed"
commit_message_help = ("A commit message to use when commiting to the "
                       "Github Pages remote branch")
remote_branch_help = ("The remote branch to commit to for Github Pages. This "
                      "overrides the value specified in config")
remote_name_help = ("The remote name to commit to for Github Pages. This "
                    "overrides the value specified in config")
force_help = "Force the push to the repository."


@click.group(context_settings={'help_option_names': ['-h', '--help']})
@click.version_option(__version__, '-V', '--version')
@common_options
def cli():
    """
    MkDocs - Project documentation with Markdown.
    """


@cli.command(name="serve")
@click.option('-f', '--config-file', type=click.File('rb'), help=config_help)
@click.option('-a', '--dev-addr', help=dev_addr_help, metavar='<IP:PORT>')
@click.option('-s', '--strict', is_flag=True, help=strict_help)
@click.option('-t', '--theme', type=click.Choice(theme_choices), help=theme_help)
@click.option('-e', '--theme-dir', type=click.Path(), help=theme_dir_help)
@click.option('--livereload', 'livereload', flag_value='livereload', help=reload_help, default=True)
@click.option('--no-livereload', 'livereload', flag_value='no-livereload', help=no_reload_help)
@click.option('--dirtyreload', 'livereload', flag_value='dirty', help=dirty_reload_help)
@common_options
def serve_command(dev_addr, config_file, strict, theme, theme_dir, livereload):
    """Run the builtin development server"""

    logging.getLogger('tornado').setLevel(logging.WARNING)

    # Don't override config value if user did not specify --strict flag
    # Conveniently, load_config drops None values
    strict = strict or None

    try:
        serve.serve(
            config_file=config_file,
            dev_addr=dev_addr,
            strict=strict,
            theme=theme,
            theme_dir=theme_dir,
            livereload=livereload
        )
    except (exceptions.ConfigurationError, socket.error) as e:  # pragma: no cover
        # Avoid ugly, unhelpful traceback
        raise SystemExit('\n' + str(e))


@cli.command(name="build")
@click.option('-c', '--clean/--dirty', is_flag=True, default=True, help=clean_help)
@click.option('-f', '--config-file', type=click.File('rb'), help=config_help)
@click.option('-s', '--strict', is_flag=True, help=strict_help)
@click.option('-t', '--theme', type=click.Choice(theme_choices), help=theme_help)
@click.option('-e', '--theme-dir', type=click.Path(), help=theme_dir_help)
@click.option('-d', '--site-dir', type=click.Path(), help=site_dir_help)
@common_options
def build_command(clean, config_file, strict, theme, theme_dir, site_dir):
    """Build the MkDocs documentation"""

    # Don't override config value if user did not specify --strict flag
    # Conveniently, load_config drops None values
    strict = strict or None

    try:
        build.build(config.load_config(
            config_file=config_file,
            strict=strict,
            theme=theme,
            theme_dir=theme_dir,
            site_dir=site_dir
        ), dirty=not clean)
    except exceptions.ConfigurationError as e:  # pragma: no cover
        # Avoid ugly, unhelpful traceback
        raise SystemExit('\n' + str(e))


@cli.command(name="gh-deploy")
@click.option('-c', '--clean/--dirty', is_flag=True, default=True, help=clean_help)
@click.option('-f', '--config-file', type=click.File('rb'), help=config_help)
@click.option('-m', '--message', help=commit_message_help)
@click.option('-b', '--remote-branch', help=remote_branch_help)
@click.option('-r', '--remote-name', help=remote_name_help)
@click.option('--force', is_flag=True, help=force_help)
@common_options
def gh_deploy_command(config_file, clean, message, remote_branch, remote_name, force):
    """Deploy your documentation to GitHub Pages"""
    try:
        cfg = config.load_config(
            config_file=config_file,
            remote_branch=remote_branch,
            remote_name=remote_name
        )
        build.build(cfg, dirty=not clean)
        gh_deploy.gh_deploy(cfg, message=message, force=force)
    except exceptions.ConfigurationError as e:  # pragma: no cover
        # Avoid ugly, unhelpful traceback
        raise SystemExit('\n' + str(e))


@cli.command(name="new")
@click.argument("project_directory")
@common_options
def new_command(project_directory):
    """Create a new MkDocs project"""
    new.new(project_directory)


if __name__ == '__main__':  # pragma: no cover
    cli()

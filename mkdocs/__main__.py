#!/usr/bin/env python

import os
import sys
import logging
import click

# TODO: Remove this check at some point in the future.
# (also remove flake8's 'ignore E402' comments below)
if sys.version_info[0] < 3:  # pragma: no cover
    raise ImportError('A recent version of Python 3 is required.')

from mkdocs import __version__                            # noqa: E402
from mkdocs import utils                                  # noqa: E402
from mkdocs import exceptions                             # noqa: E402
from mkdocs import config                                 # noqa: E402
from mkdocs.commands import build, gh_deploy, new, serve  # noqa: E402

log = logging.getLogger(__name__)


class State:
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

clean_help = "Remove old files from the site_dir before building (the default)."
config_help = "Provide a specific MkDocs config"
dev_addr_help = ("IP address and port to serve documentation locally (default: "
                 "localhost:8000)")
strict_help = ("Enable strict mode. This will cause MkDocs to abort the build "
               "on any warnings.")
theme_help = "The theme to use when building your documentation."
theme_choices = utils.get_theme_names()
site_dir_help = "The directory to output the result of the documentation build."
use_directory_urls_help = "Use directory URLs when building pages (the default)."
reload_help = "Enable the live reloading in the development server (this is the default)"
no_reload_help = "Disable the live reloading in the development server."
dirty_reload_help = "Enable the live reloading in the development server, but only re-build files that have changed"
commit_message_help = ("A commit message to use when committing to the "
                       "Github Pages remote branch. Commit {sha} and MkDocs {version} are available as expansions")
remote_branch_help = ("The remote branch to commit to for Github Pages. This "
                      "overrides the value specified in config")
remote_name_help = ("The remote name to commit to for Github Pages. This "
                    "overrides the value specified in config")
force_help = "Force the push to the repository."
ignore_version_help = "Ignore check that build is not being deployed with an older version of MkDocs."


def add_options(opts):
    def inner(f):
        for i in reversed(opts):
            f = i(f)
        return f

    return inner


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


common_options = add_options([quiet_option, verbose_option])
common_config_options = add_options([
    click.option('-f', '--config-file', type=click.File('rb'), help=config_help),
    # Don't override config value if user did not specify --strict flag
    # Conveniently, load_config drops None values
    click.option('-s', '--strict', is_flag=True, default=None, help=strict_help),
    click.option('-t', '--theme', type=click.Choice(theme_choices), help=theme_help),
    # As with --strict, set the default to None so that this doesn't incorrectly
    # override the config file
    click.option('--use-directory-urls/--no-directory-urls', is_flag=True, default=None, help=use_directory_urls_help)
])

pgk_dir = os.path.dirname(os.path.abspath(__file__))


@click.group(context_settings={'help_option_names': ['-h', '--help']})
@click.version_option(
    '{} from {} (Python {})'.format(__version__, pgk_dir, sys.version[:3]),
    '-V', '--version')
@common_options
def cli():
    """
    MkDocs - Project documentation with Markdown.
    """


@cli.command(name="serve")
@click.option('-a', '--dev-addr', help=dev_addr_help, metavar='<IP:PORT>')
@click.option('--livereload', 'livereload', flag_value='livereload', help=reload_help, default=True)
@click.option('--no-livereload', 'livereload', flag_value='no-livereload', help=no_reload_help)
@click.option('--dirtyreload', 'livereload', flag_value='dirty', help=dirty_reload_help)
@common_config_options
@common_options
def serve_command(dev_addr, livereload, **kwargs):
    """Run the builtin development server"""

    logging.getLogger('tornado').setLevel(logging.WARNING)

    try:
        serve.serve(
            dev_addr=dev_addr,
            livereload=livereload,
            **kwargs
        )
    except (exceptions.ConfigurationError, OSError) as e:  # pragma: no cover
        # Avoid ugly, unhelpful traceback
        raise SystemExit('\n' + str(e))


@cli.command(name="build")
@click.option('-c', '--clean/--dirty', is_flag=True, default=True, help=clean_help)
@common_config_options
@click.option('-d', '--site-dir', type=click.Path(), help=site_dir_help)
@common_options
def build_command(clean, **kwargs):
    """Build the MkDocs documentation"""

    try:
        build.build(config.load_config(**kwargs), dirty=not clean)
    except exceptions.ConfigurationError as e:  # pragma: no cover
        # Avoid ugly, unhelpful traceback
        raise SystemExit('\n' + str(e))


@cli.command(name="gh-deploy")
@click.option('-c', '--clean/--dirty', is_flag=True, default=True, help=clean_help)
@click.option('-m', '--message', help=commit_message_help)
@click.option('-b', '--remote-branch', help=remote_branch_help)
@click.option('-r', '--remote-name', help=remote_name_help)
@click.option('--force', is_flag=True, help=force_help)
@click.option('--ignore-version', is_flag=True, help=ignore_version_help)
@common_config_options
@click.option('-d', '--site-dir', type=click.Path(), help=site_dir_help)
@common_options
def gh_deploy_command(clean, message, remote_branch, remote_name, force, ignore_version, **kwargs):
    """Deploy your documentation to GitHub Pages"""
    try:
        cfg = config.load_config(
            remote_branch=remote_branch,
            remote_name=remote_name,
            **kwargs
        )
        build.build(cfg, dirty=not clean)
        gh_deploy.gh_deploy(cfg, message=message, force=force, ignore_version=ignore_version)
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

from __future__ import annotations

import dataclasses
import datetime
import functools
import logging
from typing import Iterator, Mapping

import yaml

from mkdocs import utils
from mkdocs.config.base import _open_config_file
from mkdocs.plugins import EntryPoint, entry_points
from mkdocs.utils.cache import download_and_cache_url

log = logging.getLogger(__name__)


def _extract_names(cfg, key: str) -> Iterator[str]:
    """Get names of plugins/extensions from the config - in either a list of dicts or a dict."""
    try:
        items = iter(cfg.get(key, ()))
    except TypeError:
        log.error(f"Invalid config entry '{key}'")
    for item in items:
        try:
            if not isinstance(item, str):
                [item] = item
            yield item
        except (ValueError, TypeError):
            log.error(f"Invalid config entry '{key}': {item}")


@functools.lru_cache()
def _entry_points(group: str) -> Mapping[str, EntryPoint]:
    eps = {ep.name: ep for ep in entry_points(group=group)}
    log.debug(f"Available '{group}' entry points: {sorted(eps)}")
    return eps


@dataclasses.dataclass(frozen=True)
class PluginKind:
    projects_key: str
    entry_points_key: str

    def __str__(self) -> str:
        return self.projects_key.rpartition('_')[-1]


def get_deps(projects_file_url: str, config_file_path: str | None = None) -> None:
    """
    Print PyPI package dependencies inferred from a mkdocs.yml file based on a reverse mapping of known projects.

    Parameters:
        projects_file_url: URL or local path of the registry file that declares all known MkDocs-related projects.
            The file is in YAML format and contains `projects: [{mkdocs_theme:, mkdocs_plugin:, markdown_extension:}]
        config_file_path: Non-default path to mkdocs.yml.
    """
    with _open_config_file(config_file_path) as f:
        cfg = utils.yaml_load(f)

    if all(c not in cfg for c in ('site_name', 'theme', 'plugins', 'markdown_extensions')):
        log.warning("The passed config file doesn't seem to be a mkdocs.yml config file")

    try:
        theme = cfg['theme']['name']
    except (KeyError, TypeError):
        theme = cfg.get('theme')
    themes = {theme} if theme else set()

    plugins = set(_extract_names(cfg, 'plugins'))
    extensions = set(_extract_names(cfg, 'markdown_extensions'))

    wanted_plugins = (
        (PluginKind('mkdocs_theme', 'mkdocs.themes'), themes - {'mkdocs', 'readthedocs'}),
        (PluginKind('mkdocs_plugin', 'mkdocs.plugins'), plugins - {'search'}),
        (PluginKind('markdown_extension', 'markdown.extensions'), extensions),
    )
    for kind, wanted in wanted_plugins:
        log.debug(f'Wanted {kind}s: {sorted(wanted)}')

    content = download_and_cache_url(projects_file_url, datetime.timedelta(days=7))
    projects = yaml.safe_load(content)['projects']

    packages_to_install = set()
    for project in projects:
        for kind, wanted in wanted_plugins:
            available = project.get(kind.projects_key, ())
            if isinstance(available, str):
                available = (available,)
            for entry_name in available:
                if entry_name in wanted or (
                    # Also check theme-namespaced plugin names against the current theme.
                    '/' in entry_name
                    and theme is not None
                    and kind.projects_key == 'mkdocs_plugin'
                    and entry_name.startswith(f'{theme}/')
                    and entry_name[len(theme) + 1 :] in wanted
                ):
                    if 'pypi_id' in project:
                        install_name = project['pypi_id']
                    elif 'github_id' in project:
                        install_name = 'git+https://github.com/{github_id}'.format_map(project)
                    else:
                        log.error(
                            f"Can't find how to install {kind} '{entry_name}' although it was identified as {project}"
                        )
                        continue
                    packages_to_install.add(install_name)
                    wanted.remove(entry_name)

    for kind, wanted in wanted_plugins:
        for entry_name in sorted(wanted):
            dist_name = None
            ep = _entry_points(kind.entry_points_key).get(entry_name)
            if ep is not None and ep.dist is not None:
                dist_name = ep.dist.name
            if dist_name not in ('mkdocs', 'Markdown'):
                warning = f"{str(kind).capitalize()} '{entry_name}' is not provided by any registered project"
                if ep is not None:
                    warning += " but is installed locally"
                    if dist_name:
                        warning += f" from '{dist_name}'"
                    log.info(warning)
                else:
                    log.warning(warning)

    for pkg in sorted(packages_to_install):
        print(pkg)

from __future__ import annotations

import dataclasses
import datetime
import functools
import logging
import sys
from typing import Mapping, Sequence

if sys.version_info >= (3, 10):
    from importlib.metadata import EntryPoint, entry_points
else:
    from importlib_metadata import EntryPoint, entry_points

import yaml

from mkdocs import utils
from mkdocs.config.base import _open_config_file
from mkdocs.utils.cache import download_and_cache_url

log = logging.getLogger(__name__)

# Note: do not rely on functions in this module, it is not public API.


class YamlLoader(yaml.SafeLoader):
    pass


# Prevent errors from trying to access external modules which may not be installed yet.
YamlLoader.add_constructor("!ENV", lambda loader, node: None)  # type: ignore
YamlLoader.add_constructor("!relative", lambda loader, node: None)  # type: ignore
YamlLoader.add_multi_constructor(
    "tag:yaml.org,2002:python/name:", lambda loader, suffix, node: None
)
YamlLoader.add_multi_constructor(
    "tag:yaml.org,2002:python/object/apply:", lambda loader, suffix, node: None
)

NotFound = ()


def dig(cfg, keys: str):
    """Receives a string such as 'foo.bar' and returns `cfg['foo']['bar']`, or `NotFound`.

    A list of single-item dicts gets converted to a flat dict. This is intended for `plugins` config.
    """
    key, _, rest = keys.partition('.')
    try:
        cfg = cfg[key]
    except (KeyError, TypeError):
        return NotFound
    if isinstance(cfg, list):
        orig_cfg = cfg
        cfg = {}
        for item in reversed(orig_cfg):
            if isinstance(item, dict) and len(item) == 1:
                cfg.update(item)
            elif isinstance(item, str):
                cfg[item] = {}
    if not rest:
        return cfg
    return dig(cfg, rest)


def strings(obj) -> Sequence[str]:
    if isinstance(obj, str):
        return (obj,)
    else:
        return tuple(obj)


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
        cfg = utils.yaml_load(f, loader=YamlLoader)  # type: ignore

    packages_to_install = set()

    if all(c not in cfg for c in ('site_name', 'theme', 'plugins', 'markdown_extensions')):
        log.warning("The passed config file doesn't seem to be a mkdocs.yml config file")
    else:
        if dig(cfg, 'theme.locale') not in (NotFound, 'en'):
            packages_to_install.add('mkdocs[i18n]')
        else:
            packages_to_install.add('mkdocs')

    try:
        theme = cfg['theme']['name']
    except (KeyError, TypeError):
        theme = cfg.get('theme')
    themes = {theme} if theme else set()

    plugins = set(strings(dig(cfg, 'plugins')))
    extensions = set(strings(dig(cfg, 'markdown_extensions')))

    wanted_plugins = (
        (PluginKind('mkdocs_theme', 'mkdocs.themes'), themes - {'mkdocs', 'readthedocs'}),
        (PluginKind('mkdocs_plugin', 'mkdocs.plugins'), plugins - {'search'}),
        (PluginKind('markdown_extension', 'markdown.extensions'), extensions),
    )
    for kind, wanted in wanted_plugins:
        log.debug(f'Wanted {kind}s: {sorted(wanted)}')

    content = download_and_cache_url(projects_file_url, datetime.timedelta(days=7))
    projects = yaml.safe_load(content)['projects']

    for project in projects:
        for kind, wanted in wanted_plugins:
            available = strings(project.get(kind.projects_key, ()))
            for entry_name in available:
                if (  # Also check theme-namespaced plugin names against the current theme.
                    '/' in entry_name
                    and theme is not None
                    and kind.projects_key == 'mkdocs_plugin'
                    and entry_name.startswith(f'{theme}/')
                    and entry_name[len(theme) + 1 :] in wanted
                    and entry_name not in wanted
                ):
                    entry_name = entry_name[len(theme) + 1 :]
                if entry_name in wanted:
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
                    for extra_key, extra_pkgs in project.get('extra_dependencies', {}).items():
                        if dig(cfg, extra_key) is not NotFound:
                            packages_to_install.update(strings(extra_pkgs))

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
        print(pkg)  # noqa: T201

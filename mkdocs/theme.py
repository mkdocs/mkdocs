from __future__ import annotations

import logging
import os
from typing import Any, Collection, MutableMapping

import jinja2

from mkdocs import localization, utils
from mkdocs.config.base import ValidationError
from mkdocs.utils import templates

log = logging.getLogger(__name__)


class Theme(MutableMapping[str, Any]):
    """
    A Theme object.

    Parameters:
        name: The name of the theme as defined by its entrypoint.
        custom_dir: User defined directory for custom templates.
        static_templates: A list of templates to render as static pages.

    All other keywords are passed as-is and made available as a key/value mapping.
    """

    def __init__(
        self,
        name: str | None = None,
        *,
        custom_dir: str | None = None,
        static_templates: Collection[str] = (),
        locale: str | None = None,
        **user_config,
    ) -> None:
        self.name = name
        self._custom_dir = custom_dir
        _vars: dict[str, Any] = {'name': name, 'locale': 'en'}
        # _vars is soft-deprecated, intentionally hide it from mypy.
        setattr(self, '_vars', _vars)

        # MkDocs provided static templates are always included
        package_dir = os.path.abspath(os.path.dirname(__file__))
        mkdocs_templates = os.path.join(package_dir, 'templates')
        self.static_templates = set(os.listdir(mkdocs_templates))

        # Build self.dirs from various sources in order of precedence
        self.dirs = []

        if custom_dir is not None:
            self.dirs.append(custom_dir)

        if name:
            self._load_theme_config(name)

        # Include templates provided directly by MkDocs (outside any theme)
        self.dirs.append(mkdocs_templates)

        # Handle remaining user configs. Override theme configs (if set)
        self.static_templates.update(static_templates)
        _vars.update(user_config)

        # Validate locale and convert to Locale object
        _vars['locale'] = localization.parse_locale(
            locale if locale is not None else _vars['locale']
        )

    name: str | None

    @property
    def locale(self) -> localization.Locale:
        return self['locale']

    @property
    def custom_dir(self) -> str | None:
        return self._custom_dir

    dirs: list[str]

    static_templates: set[str]

    def __repr__(self) -> str:
        return "{}(name={!r}, dirs={!r}, static_templates={!r}, {})".format(
            self.__class__.__name__,
            self.name,
            self.dirs,
            self.static_templates,
            ', '.join(f'{k}={v!r}' for k, v in self.items()),
        )

    def __getitem__(self, key: str) -> Any:
        return self._vars[key]  # type: ignore[attr-defined]

    def __setitem__(self, key: str, value):
        self._vars[key] = value  # type: ignore[attr-defined]

    def __delitem__(self, key: str):
        del self._vars[key]  # type: ignore[attr-defined]

    def __contains__(self, item: object) -> bool:
        return item in self._vars  # type: ignore[attr-defined]

    def __len__(self):
        return len(self._vars)  # type: ignore[attr-defined]

    def __iter__(self):
        return iter(self._vars)  # type: ignore[attr-defined]

    def _load_theme_config(self, name: str) -> None:
        """Recursively load theme and any parent themes."""

        theme_dir = utils.get_theme_dir(name)
        self.dirs.append(theme_dir)

        try:
            file_path = os.path.join(theme_dir, 'mkdocs_theme.yml')
            with open(file_path, 'rb') as f:
                theme_config = utils.yaml_load(f)
        except OSError as e:
            log.debug(e)
            raise ValidationError(
                f"The theme '{name}' does not appear to have a configuration file. "
                f"Please upgrade to a current version of the theme."
            )

        log.debug(f"Loaded theme configuration for '{name}' from '{file_path}': {theme_config}")

        parent_theme = theme_config.pop('extends', None)
        if parent_theme:
            themes = utils.get_theme_names()
            if parent_theme not in themes:
                raise ValidationError(
                    f"The theme '{name}' inherits from '{parent_theme}', which does not appear to be installed. "
                    f"The available installed themes are: {', '.join(themes)}"
                )
            self._load_theme_config(parent_theme)

        self.static_templates.update(theme_config.pop('static_templates', []))
        self._vars.update(theme_config)  # type: ignore[attr-defined]

    def get_env(self) -> jinja2.Environment:
        """Return a Jinja environment for the theme."""

        loader = jinja2.FileSystemLoader(self.dirs)
        # No autoreload because editing a template in the middle of a build is not useful.
        env = jinja2.Environment(loader=loader, auto_reload=False)
        env.filters['url'] = templates.url_filter
        env.filters['script_tag'] = templates.script_tag_filter
        localization.install_translations(env, self.locale, self.dirs)
        return env

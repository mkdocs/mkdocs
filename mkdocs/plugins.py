"""
Implements the plugin API for MkDocs.

"""


import logging
from collections import OrderedDict
from typing import Any, Callable, Dict, Optional, Sequence, Tuple, TypeVar, overload

import importlib_metadata
import jinja2.environment

from mkdocs.config.base import BaseConfigOption, Config
from mkdocs.livereload import LiveReloadServer
from mkdocs.structure.files import Files
from mkdocs.structure.nav import Navigation
from mkdocs.structure.pages import Page

log = logging.getLogger('mkdocs.plugins')


def get_plugins():
    """Return a dict of all installed Plugins as {name: EntryPoint}."""

    plugins = importlib_metadata.entry_points(group='mkdocs.plugins')

    # Allow third-party plugins to override core plugins
    pluginmap = {}
    for plugin in plugins:
        if plugin.name in pluginmap and plugin.value.startswith("mkdocs.contrib."):
            continue

        pluginmap[plugin.name] = plugin

    return pluginmap


class BasePlugin:
    """
    Plugin base class.

    All plugins should subclass this class.
    """

    config_scheme: Sequence[Tuple[str, BaseConfigOption]] = ()
    config: Config = {}  # type: ignore[assignment]

    def load_config(
        self, options: Dict[str, Any], config_file_path: Optional[str] = None
    ) -> Tuple[list, list]:
        """Load config from a dict of options. Returns a tuple of (errors, warnings)."""

        self.config = Config(schema=self.config_scheme, config_file_path=config_file_path)
        self.config.load_dict(options)

        return self.config.validate()

    # (Note that event implementations shouldn't actually be static methods in subclasses)

    # Global events

    @staticmethod
    def on_serve(
        server: LiveReloadServer, config: Config, builder: Callable
    ) -> Optional[LiveReloadServer]:
        """
        The `serve` event is only called when the `serve` command is used during
        development. It is passed the `Server` instance which can be modified before
        it is activated. For example, additional files or directories could be added
        to the list of "watched" files for auto-reloading.

        Parameters:
            server: `livereload.Server` instance
            config: global configuration object
            builder: a callable which gets passed to each call to `server.watch`

        Returns:
            `livereload.Server` instance
        """
        return server

    @staticmethod
    def on_config(config: Config) -> Optional[Config]:
        """
        The `config` event is the first event called on build and is run immediately
        after the user configuration is loaded and validated. Any alterations to the
        config should be made here.

        Parameters:
            config: global configuration object

        Returns:
            global configuration object
        """
        return config

    @staticmethod
    def on_pre_build(config: Config) -> None:
        """
        The `pre_build` event does not alter any variables. Use this event to call
        pre-build scripts.

        Parameters:
            config: global configuration object
        """

    @staticmethod
    def on_files(files: Files, config: Config) -> Optional[Files]:
        """
        The `files` event is called after the files collection is populated from the
        `docs_dir`. Use this event to add, remove, or alter files in the
        collection. Note that Page objects have not yet been associated with the
        file objects in the collection. Use [Page Events](plugins.md#page-events) to manipulate page
        specific data.

        Parameters:
            files: global files collection
            config: global configuration object

        Returns:
            global files collection
        """
        return files

    @staticmethod
    def on_nav(nav: Navigation, config: Config, files: Files) -> Optional[Navigation]:
        """
        The `nav` event is called after the site navigation is created and can
        be used to alter the site navigation.

        Parameters:
            nav: global navigation object
            config: global configuration object
            files: global files collection

        Returns:
            global navigation object
        """
        return nav

    @staticmethod
    def on_env(
        env: jinja2.Environment, config: Config, files: Files
    ) -> Optional[jinja2.Environment]:
        """
        The `env` event is called after the Jinja template environment is created
        and can be used to alter the
        [Jinja environment](https://jinja.palletsprojects.com/en/latest/api/#jinja2.Environment).

        Parameters:
            env: global Jinja environment
            config: global configuration object
            files: global files collection

        Returns:
            global Jinja Environment
        """
        return env

    @staticmethod
    def on_post_build(config: Config) -> None:
        """
        The `post_build` event does not alter any variables. Use this event to call
        post-build scripts.

        Parameters:
            config: global configuration object
        """

    @staticmethod
    def on_build_error(error: Exception) -> None:
        """
        The `build_error` event is called after an exception of any kind
        is caught by MkDocs during the build process.
        Use this event to clean things up before MkDocs terminates. Note that any other
        events which were scheduled to run after the error will have been skipped. See
        [Handling Errors](plugins.md#handling-errors) for more details.

        Parameters:
            error: exception raised
        """

    # Template events

    @staticmethod
    def on_pre_template(
        template: jinja2.Template, template_name: str, config: Config
    ) -> Optional[jinja2.Template]:
        """
        The `pre_template` event is called immediately after the subject template is
        loaded and can be used to alter the template.

        Parameters:
            template: a Jinja2 [Template](https://jinja.palletsprojects.com/en/latest/api/#jinja2.Template) object
            template_name: string filename of template
            config: global configuration object

        Returns:
            a Jinja2 [Template](https://jinja.palletsprojects.com/en/latest/api/#jinja2.Template) object
        """
        return template

    @staticmethod
    def on_template_context(
        context: Dict[str, Any], template_name: str, config: Config
    ) -> Optional[Dict[str, Any]]:
        """
        The `template_context` event is called immediately after the context is created
        for the subject template and can be used to alter the context for that specific
        template only.

        Parameters:
            context: dict of template context variables
            template_name: string filename of template
            config: global configuration object

        Returns:
            dict of template context variables
        """
        return context

    @staticmethod
    def on_post_template(output_content: str, template_name: str, config: Config) -> str:
        """
        The `post_template` event is called after the template is rendered, but before
        it is written to disc and can be used to alter the output of the template.
        If an empty string is returned, the template is skipped and nothing is is
        written to disc.

        Parameters:
            output_content: output of rendered template as string
            template_name: string filename of template
            config: global configuration object

        Returns:
            output of rendered template as string
        """
        return output_content

    # Page events

    @staticmethod
    def on_pre_page(page: Page, config: Config, files: Files) -> Optional[Page]:
        """
        The `pre_page` event is called before any actions are taken on the subject
        page and can be used to alter the `Page` instance.

        Parameters:
            page: `mkdocs.nav.Page` instance
            config: global configuration object
            files: global files collection

        Returns:
            `mkdocs.nav.Page` instance
        """
        return page

    @staticmethod
    def on_page_read_source(page: Page, config: Config) -> Optional[str]:
        """
        The `on_page_read_source` event can replace the default mechanism to read
        the contents of a page's source from the filesystem.

        Parameters:
            page: `mkdocs.nav.Page` instance
            config: global configuration object

        Returns:
            The raw source for a page as unicode string. If `None` is returned, the
                default loading from a file will be performed.
        """
        return None

    @staticmethod
    def on_page_markdown(markdown: str, page: Page, config: Config, files: Files) -> Optional[str]:
        """
        The `page_markdown` event is called after the page's markdown is loaded
        from file and can be used to alter the Markdown source text. The meta-
        data has been stripped off and is available as `page.meta` at this point.

        Parameters:
            markdown: Markdown source text of page as string
            page: `mkdocs.nav.Page` instance
            config: global configuration object
            files: global files collection

        Returns:
            Markdown source text of page as string
        """
        return markdown

    @staticmethod
    def on_page_content(html: str, page: Page, config: Config, files: Files) -> Optional[str]:
        """
        The `page_content` event is called after the Markdown text is rendered to
        HTML (but before being passed to a template) and can be used to alter the
        HTML body of the page.

        Parameters:
            html: HTML rendered from Markdown source as string
            page: `mkdocs.nav.Page` instance
            config: global configuration object
            files: global files collection

        Returns:
            HTML rendered from Markdown source as string
        """
        return html

    @staticmethod
    def on_page_context(
        context: Dict[str, Any], page: Page, config: Config, nav: Navigation
    ) -> Optional[Dict[str, Any]]:
        """
        The `page_context` event is called after the context for a page is created
        and can be used to alter the context for that specific page only.

        Parameters:
            context: dict of template context variables
            page: `mkdocs.nav.Page` instance
            config: global configuration object
            nav: global navigation object

        Returns:
            dict of template context variables
        """
        return context

    @staticmethod
    def on_post_page(output: str, page: Page, config: Config) -> str:
        """
        The `post_page` event is called after the template is rendered, but
        before it is written to disc and can be used to alter the output of the
        page. If an empty string is returned, the page is skipped and nothing is
        written to disc.

        Parameters:
            output: output of rendered template as string
            page: `mkdocs.nav.Page` instance
            config: global configuration object

        Returns:
            output of rendered template as string
        """
        return output


EVENTS = tuple(k[3:] for k in dir(BasePlugin) if k.startswith('on_'))

T = TypeVar('T')


class PluginCollection(OrderedDict):
    """
    A collection of plugins.

    In addition to being a dict of Plugin instances, each event method is registered
    upon being added. All registered methods for a given event can then be run in order
    by calling `run_event`.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.events = {k: [] for k in EVENTS}

    def _register_event(self, event_name, method):
        """Register a method for an event."""
        self.events[event_name].append(method)

    def __setitem__(self, key: str, value: BasePlugin, **kwargs):
        if not isinstance(value, BasePlugin):
            raise TypeError(
                f'{self.__module__}.{self.__name__} only accepts values which'
                f' are instances of {BasePlugin.__module__}.{BasePlugin.__name__}'
                ' subclasses'
            )
        super().__setitem__(key, value, **kwargs)
        # Register all of the event methods defined for this Plugin.
        for event_name in (x for x in dir(value) if x.startswith('on_')):
            method = getattr(value, event_name)
            if callable(method) and method is not getattr(BasePlugin, event_name):
                self._register_event(event_name[3:], method)

    @overload
    def run_event(self, name: str, item: None, **kwargs) -> None:
        ...

    @overload
    def run_event(self, name: str, item: T, **kwargs) -> T:
        ...

    def run_event(self, name: str, item: T = None, **kwargs) -> Optional[T]:
        """
        Run all registered methods of an event.

        `item` is the object to be modified or replaced and returned by the event method.
        If it isn't given the event method creates a new object to be returned.
        All other keywords are variables for context, but would not generally
        be modified by the event method.
        """

        pass_item = item is not None
        for method in self.events[name]:
            if pass_item:
                result = method(item, **kwargs)
            else:
                result = method(**kwargs)
            # keep item if method returned `None`
            if result is not None:
                item = result
        return item

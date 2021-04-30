"""
Implements the plugin API for MkDocs.

"""


import logging
from collections import OrderedDict

import importlib_metadata

from mkdocs.config.base import Config

log = logging.getLogger('mkdocs.plugins')


EVENTS = (
    'config',
    'pre_build',
    'files',
    'nav',
    'env',
    'pre_template',
    'template_context',
    'post_template',
    'pre_page',
    'page_read_source',
    'page_markdown',
    'page_content',
    'page_context',
    'post_page',
    'post_build',
    'serve',
    'build_error',
)


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

    config_scheme = ()
    config = {}

    def load_config(self, options, config_file_path=None):
        """Load config from a dict of options. Returns a tuple of (errors, warnings)."""

        self.config = Config(schema=self.config_scheme, config_file_path=config_file_path)
        self.config.load_dict(options)

        return self.config.validate()

    # Global events

    def on_serve(self, server, config, builder):
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

    def on_config(self, config):
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

    def on_pre_build(self, config):
        """
        The `pre_build` event does not alter any variables. Use this event to call
        pre-build scripts.

        Parameters:
            config: global configuration object
        """

    def on_files(self, files, config):
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

    def on_nav(self, nav, config, files):
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

    def on_env(self, env, config, files):
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

    def on_post_build(self, config):
        """
        The `post_build` event does not alter any variables. Use this event to call
        post-build scripts.

        Parameters:
            config: global configuration object
        """

    def on_build_error(self, error):
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

    def on_pre_template(self, template, template_name, config):
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

    def on_template_context(self, context, template_name, config):
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

    def on_post_template(self, output_content, template_name, config):
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

    def on_pre_page(self, page, config, files):
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

    def on_page_read_source(self, page, config):
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

    def on_page_markdown(self, markdown, page, config, files):
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

    def on_page_content(self, html, page, config, files):
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

    def on_page_context(self, context, page, config, nav):
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

    def on_post_page(self, output, page, config):
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


class PluginCollection(OrderedDict):
    """
    A collection of plugins.

    In addition to being a dict of Plugin instances, each event method is registered
    upon being added. All registered methods for a given event can then be run in order
    by calling `run_event`.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __setitem__(self, key, value, **kwargs):
        if not isinstance(value, BasePlugin):
            raise TypeError(
                f'{self.__module__}.{self.__name__} only accepts values which'
                f' are instances of {BasePlugin.__module__}.{BasePlugin.__name__}'
                ' subclasses'
            )
        super().__setitem__(key, value, **kwargs)

    def run_event(self, name, item=None, **kwargs):
        """
        Run all registered methods of an event.

        `item` is the object to be modified or replaced and returned by the event method.
        If it isn't given the event method creates a new object to be returned.
        All other keywords are variables for context, but would not generally
        be modified by the event method.
        """

        name = 'on_' + name
        pass_item = item is not None
        getattr(BasePlugin, name)  # just to produce AttributeError
        for plugin in list(self.values()):  # can change size during iteration
            method = getattr(plugin, name)
            if pass_item:
                result = method(item, **kwargs)
            else:
                result = method(**kwargs)
            # keep item if method returned `None`
            if result is not None:
                item = result
        return item

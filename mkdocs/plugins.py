"""
Implements the plugin API for MkDocs.

"""


import pkg_resources
import logging
from collections import OrderedDict

from mkdocs.config.base import Config


log = logging.getLogger('mkdocs.plugins')


EVENTS = (
    'config', 'pre_build', 'files', 'nav', 'env', 'pre_template', 'template_context',
    'post_template', 'pre_page', 'page_read_source', 'page_markdown',
    'page_content', 'page_context', 'post_page', 'post_build', 'serve'
)


def get_plugins():
    """ Return a dict of all installed Plugins by name. """

    plugins = pkg_resources.iter_entry_points(group='mkdocs.plugins')

    return {plugin.name: plugin for plugin in plugins}


class BasePlugin:
    """
    Plugin base class.

    All plugins should subclass this class.
    """

    config_scheme = ()
    config = {}

    def load_config(self, options, config_file_path=None):
        """ Load config from a dict of options. Returns a tuple of (errors, warnings)."""

        self.config = Config(schema=self.config_scheme, config_file_path=config_file_path)
        self.config.load_dict(options)

        return self.config.validate()


class PluginCollection(OrderedDict):
    """
    A collection of plugins.

    In addition to being a dict of Plugin instances, each event method is registered
    upon being added. All registered methods for a given event can then be run in order
    by calling `run_event`.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.events = {x: [] for x in EVENTS}

    def _register_event(self, event_name, method):
        """ Register a method for an event. """
        self.events[event_name].append(method)

    def __setitem__(self, key, value, **kwargs):
        if not isinstance(value, BasePlugin):
            raise TypeError(
                '{0}.{1} only accepts values which are instances of {2}.{3} '
                'sublcasses'.format(self.__module__, self.__name__,
                                    BasePlugin.__module__, BasePlugin.__name__))
        super().__setitem__(key, value, **kwargs)
        # Register all of the event methods defined for this Plugin.
        for event_name in (x for x in dir(value) if x.startswith('on_')):
            method = getattr(value, event_name)
            if callable(method):
                self._register_event(event_name[3:], method)

    def run_event(self, name, item=None, **kwargs):
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

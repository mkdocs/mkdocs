# coding: utf-8

from __future__ import unicode_literals
import logging

from mkdocs.structure.pages import Page
from mkdocs.utils import string_types, nest_paths

log = logging.getLogger(__name__)


class Navigation(object):
    def __init__(self, items, pages):
        self.items = items  # Nested List with full navigation of Sections, Pages, and Links.
        self.pages = pages  # Flat List of subset of Pages in nav, in order.

        self.homepage = None
        for page in pages:
            if page.is_homepage:
                self.homepage = page
                break

    def __repr__(self):
        return '\n'.join([item._indent_print() for item in self])

    def __iter__(self):
        return iter(self.items)

    def __len__(self):
        return len(self.items)


class Section(object):
    def __init__(self, title, children):
        self.title = title
        self.children = children

        self.parent = None
        self.active = False

        self.is_section = True
        self.is_page = False
        self.is_link = False

    def __repr__(self):
        return "Section(title='{0}')".format(self.title)

    def _get_active(self):
        """ Return active status of section. """
        return self.__active

    def _set_active(self, value):
        """ Set active status of section and ancestors. """
        self.__active = bool(value)
        if self.parent is not None:
            self.parent.active = bool(value)

    active = property(_get_active, _set_active)

    @property
    def ancestors(self):
        if self.parent is None:
            return []
        return [self.parent] + self.parent.ancestors

    def _indent_print(self, depth=0):
        ret = ['{}{}'.format('    ' * depth, repr(self))]
        for item in self.children:
            ret.append(item._indent_print(depth + 1))
        return '\n'.join(ret)


class Link(object):
    def __init__(self, title, url):
        self.title = title
        self.url = url
        self.parent = None

        # These should never change but are included for consistency with sections and pages.
        self.children = None
        self.active = False
        self.is_section = False
        self.is_page = False
        self.is_link = True

    def __repr__(self):
        title = "'{}'".format(self.title) if (self.title is not None) else '[blank]'
        return "Link(title={}, url='{}')".format(title, self.url)

    @property
    def ancestors(self):
        if self.parent is None:
            return []
        return [self.parent] + self.parent.ancestors

    def _indent_print(self, depth=0):
        return '{}{}'.format('    ' * depth, repr(self))


def get_navigation(files, config):
    """ Build site navigation from config and files."""
    nav_config = config['nav'] or nest_paths(f.src_path for f in files.documentation_pages())
    items = _data_to_navigation(nav_config, files, config)
    if not isinstance(items, list):
        items = [items]

    # Get only the pages from the navigation, ignoring any sections and links.
    pages = _get_by_type(items, Page)

    # Include next, previous and parent links.
    _add_previous_and_next_links(pages)
    _add_parent_links(items)

    missing_from_config = [file for file in files.documentation_pages() if file.page is None]
    if missing_from_config:
        log.info(
            'The following pages exist in the docs directory, but are not '
            'included in the "nav" configuration:\n  - {}'.format(
                '\n  - '.join([file.src_path for file in missing_from_config]))
        )
        # Any documentation files not found in the nav should still have an associated page.
        # However, these page objects are only accessable from File instances as `file.page`.
        for file in missing_from_config:
            Page(None, file, config)

    links = _get_by_type(items, Link)
    if links:
        # Assume all links are external.
        log.debug(
            'The following paths are included in the "nav" configuration, '
            'but do not exist in the docs directory:\n  - {}'.format(
                '\n  - '.join([link.url for link in links]))
        )
    return Navigation(items, pages)


def _data_to_navigation(data, files, config):
    if isinstance(data, dict):
        return [
            _data_to_navigation((key, value), files, config)
            if isinstance(value, string_types) else
            Section(title=key, children=_data_to_navigation(value, files, config))
            for key, value in data.items()
        ]
    elif isinstance(data, list):
        return [
            _data_to_navigation(item, files, config)[0]
            if isinstance(item, dict) and len(item) == 1 else
            _data_to_navigation(item, files, config)
            for item in data
        ]
    title, path = data if isinstance(data, tuple) else (None, data)
    file = files.get_file_from_path(path)
    if file:
        return Page(title, file, config)
    return Link(title, path)


def _get_by_type(nav, T):
    ret = []
    for item in nav:
        if isinstance(item, T):
            ret.append(item)
        elif item.children:
            ret.extend(_get_by_type(item.children, T))
    return ret


def _add_parent_links(nav):
    for item in nav:
        if item.is_section:
            for child in item.children:
                child.parent = item
            _add_parent_links(item.children)


def _add_previous_and_next_links(pages):
    bookended = [None] + pages + [None]
    zipped = zip(bookended[:-2], bookended[1:-1], bookended[2:])
    for page0, page1, page2 in zipped:
        page1.previous_page, page1.next_page = page0, page2

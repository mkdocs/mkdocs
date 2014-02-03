#coding: utf-8

"""
Deals with generating the site-wide navigation.

This consists of building a set of interlinked page and header objects.
"""

from mkdocs import utils
import posixpath
import os


class SiteNavigation(object):
    def __init__(self, pages_config, use_directory_urls=True):
        self.url_context = URLContext()
        self.nav_items, self.pages = \
            _generate_site_navigation(pages_config, self.url_context, use_directory_urls)
        self.homepage = self.pages[0] if self.pages else None

    def __str__(self):
        return ''.join([str(item) for item in self])

    def __iter__(self):
        return iter(self.nav_items)

    def walk_pages(self):
        """
        Returns each page in the site in turn.

        Additionally this sets the active status of the pages and headers,
        in the site navigation, so that the rendered navbar can correctly
        highlight the currently active page and/or header item.
        """
        page = self.homepage
        page.set_active()
        self.url_context.set_current_url(page.abs_url)
        yield page
        while page.next_page:
            page.set_active(False)
            page = page.next_page
            page.set_active()
            self.url_context.set_current_url(page.abs_url)
            yield page
        page.set_active(False)


class URLContext(object):
    def __init__(self):
        self.base_path = '/'

    def set_current_url(self, current_url):
        self.base_path = posixpath.dirname(current_url)

    def make_relative(self, url):
        return posixpath.relpath(url, start=self.base_path)


class Page(object):
    def __init__(self, title, url, path, url_context):
        self.title = title
        self.abs_url = url
        self.active = False
        self.url_context = url_context

        # Relative paths to the input markdown file and output html file.
        self.input_path = path
        self.output_path = utils.get_html_path(path)

        # Links to related pages
        self.previous_page = None
        self.next_page = None
        self.ancestors = []

    @property
    def url(self):
        return self.url_context.make_relative(self.abs_url)

    @property
    def is_homepage(self):
        return os.path.splitext(self.input_path)[0] == 'index'

    def __str__(self):
        return self._indent_print()

    def _indent_print(self, depth=0):
        indent = '    ' * depth
        active_marker = ' [*]' if self.active else ''
        return '%s%s - %s%s\n' % (indent, self.title, self.abs_url, active_marker)

    def set_active(self, active=True):
        self.active = active
        for ancestor in self.ancestors:
            ancestor.active = active


class Header(object):
    def __init__(self, title, children):
        self.title, self.children = title, children
        self.active = False

    def __str__(self):
        return self._indent_print()

    def _indent_print(self, depth=0):
        indent = '    ' * depth
        active_marker = ' [*]' if self.active else ''
        ret = '%s%s%s\n' % (indent, self.title, active_marker)
        for item in self.children:
            ret += item._indent_print(depth + 1)
        return ret


def _generate_site_navigation(pages_config, url_context, use_directory_urls=True):
    """
    Returns a list of Page and Header instances that represent the
    top level site navigation.
    """
    nav_items = []
    pages = []
    previous = None

    for config_line in pages_config:
        if len(config_line) == 2:
            path, title = config_line
            child_title = None
        elif len(config_line) == 3:
            path, title, child_title = config_line
        else:
            msg = (
                "Line in 'page' config contained %d items.  "
                "Expected 2 or 3." % len(config_line)
            )
            assert False, msg

        url = utils.get_url_path(path, use_directory_urls)

        if not child_title:
            # New top level page.
            page = Page(title=title, url=url, path=path, url_context=url_context)
            nav_items.append(page)
        elif not nav_items or (nav_items[-1].title != title):
            # New second level page.
            page = Page(title=child_title, url=url, path=path, url_context=url_context)
            header = Header(title=title, children=[page])
            nav_items.append(header)
            page.ancestors = [header]
        else:
            # Additional second level page.
            page = Page(title=child_title, url=url, path=path, url_context=url_context)
            header = nav_items[-1]
            header.children.append(page)
            page.ancestors = [header]

        # Add in previous and next information.
        if previous:
            page.previous_page = previous
            previous.next_page = page
        previous = page

        pages.append(page)

    return (nav_items, pages)

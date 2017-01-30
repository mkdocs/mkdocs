# coding: utf-8

"""
Deals with generating the site-wide navigation.

This consists of building a set of interlinked page and header objects.
"""

from __future__ import unicode_literals
import datetime
import logging
import os

from mkdocs import utils, exceptions

log = logging.getLogger(__name__)


def filename_to_title(filename):
    """
    Automatically generate a default title, given a filename.
    """
    if utils.is_homepage(filename):
        return 'Home'

    return utils.filename_to_title(filename)


class SiteNavigation(object):
    def __init__(self, pages_config, use_directory_urls=True):
        self.url_context = URLContext()
        self.file_context = FileContext()
        self.nav_items, self.pages = _generate_site_navigation(
            pages_config, self.url_context, use_directory_urls)
        self.homepage = self.pages[0] if self.pages else None
        self.use_directory_urls = use_directory_urls

    def __str__(self):
        return ''.join([str(item) for item in self])

    def __iter__(self):
        return iter(self.nav_items)

    def __len__(self):
        return len(self.nav_items)

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
        self.file_context.set_current_path(page.input_path)
        yield page
        while page.next_page:
            page.set_active(False)
            page = page.next_page
            page.set_active()
            self.url_context.set_current_url(page.abs_url)
            self.file_context.set_current_path(page.input_path)
            yield page
        page.set_active(False)

    @property
    def source_files(self):
        if not hasattr(self, '_source_files'):
            self._source_files = set([page.input_path for page in self.pages])
        return self._source_files


class URLContext(object):
    """
    The URLContext is used to ensure that we can generate the appropriate
    relative URLs to other pages from any given page in the site.

    We use relative URLs so that static sites can be deployed to any location
    without having to specify what the path component on the host will be
    if the documentation is not hosted at the root path.
    """

    def __init__(self):
        self.base_path = '/'
        self.force_abs_urls = False

    def set_current_url(self, current_url):
        self.base_path = os.path.dirname(current_url)

    def make_relative(self, url):
        """
        Given a URL path return it as a relative URL,
        given the context of the current page.
        """
        if self.force_abs_urls:
            abs_url = '%s/%s' % (self.base_path.rstrip('/'), utils.path_to_url(url.lstrip('/')))
            return abs_url

        suffix = '/' if (url.endswith('/') and len(url) > 1) else ''
        # Workaround for bug on `os.path.relpath()` in Python 2.6
        if self.base_path == '/':
            if url == '/':
                # Workaround for static assets
                return '.'
            return url.lstrip('/')
        # Under Python 2.6, relative_path adds an extra '/' at the end.
        relative_path = os.path.relpath(url, start=self.base_path)
        relative_path = relative_path.rstrip('/') + suffix

        return utils.path_to_url(relative_path)


class FileContext(object):
    """
    The FileContext is used to ensure that we can generate the appropriate
    full path for other pages given their relative path from a particular page.

    This is used when we have relative hyperlinks in the documentation, so that
    we can ensure that they point to markdown documents that actually exist
    in the `pages` config.
    """
    def __init__(self):
        self.current_file = None
        self.base_path = ''

    def set_current_path(self, current_path):
        self.current_file = current_path
        self.base_path = os.path.dirname(current_path)

    def make_absolute(self, path):
        """
        Given a relative file path return it as a POSIX-style
        absolute filepath, given the context of the current page.
        """
        return os.path.normpath(os.path.join(self.base_path, path))


class Page(object):
    def __init__(self, title, url, path, url_context):

        self.title = title
        self.abs_url = url
        self.active = False
        self.url_context = url_context

        # Support SOURCE_DATE_EPOCH environment variable for "reproducible" builds.
        # See https://reproducible-builds.org/specs/source-date-epoch/
        if 'SOURCE_DATE_EPOCH' in os.environ:
            self.update_date = datetime.datetime.utcfromtimestamp(
                int(os.environ['SOURCE_DATE_EPOCH'])
            ).strftime("%Y-%m-%d")
        else:
            self.update_date = datetime.datetime.now().strftime("%Y-%m-%d")

        # Relative paths to the input markdown file and output html file.
        self.input_path = path
        self.output_path = utils.get_html_path(path)

        # Links to related pages
        self.previous_page = None
        self.next_page = None
        self.ancestors = []

        # Placeholders to be filled in later in the build
        # process when we have access to the config.
        self.canonical_url = None
        self.edit_url = None
        self.content = None
        self.meta = None
        self.toc = None

    @property
    def url(self):
        return self.url_context.make_relative(self.abs_url)

    @property
    def is_homepage(self):
        return utils.is_homepage(self.input_path)

    @property
    def is_top_level(self):
        return len(self.ancestors) == 0

    def __str__(self):
        return self.indent_print()

    def indent_print(self, depth=0):
        indent = '    ' * depth
        active_marker = ' [*]' if self.active else ''
        title = self.title if (self.title is not None) else '[blank]'
        return '%s%s - %s%s\n' % (indent, title, self.abs_url, active_marker)

    def set_active(self, active=True):
        self.active = active
        for ancestor in self.ancestors:
            ancestor.set_active(active)

    def set_canonical_url(self, base):
        if not base.endswith('/'):
            base += '/'
        self.canonical_url = utils.urljoin(base, self.abs_url.lstrip('/'))

    def set_edit_url(self, repo_url, edit_uri):
        if not repo_url.endswith('/'):
            repo_url += '/'
        if not edit_uri:
            self.edit_url = repo_url
        else:
            if not edit_uri.endswith('/'):
                edit_uri += '/'
            self.edit_url = utils.urljoin(
                repo_url + edit_uri,
                self.input_path)


class Header(object):
    def __init__(self, title, children):
        self.title, self.children = title, children
        self.active = False
        self.ancestors = []

    def __str__(self):
        return self.indent_print()

    @property
    def is_top_level(self):
        return len(self.ancestors) == 0

    def indent_print(self, depth=0):
        indent = '    ' * depth
        active_marker = ' [*]' if self.active else ''
        ret = '%s%s%s\n' % (indent, self.title, active_marker)
        for item in self.children:
            ret += item.indent_print(depth + 1)
        return ret

    def set_active(self, active=True):
        self.active = active
        for ancestor in self.ancestors:
            ancestor.set_active(active)


def _path_to_page(path, title, url_context, use_directory_urls):
    if title is None:
        title = filename_to_title(path.split(os.path.sep)[-1])
    url = utils.get_url_path(path, use_directory_urls)
    return Page(title=title, url=url, path=path,
                url_context=url_context)


def _follow(config_line, url_context, use_dir_urls, header=None, title=None):

    if isinstance(config_line, utils.string_types):
        path = os.path.normpath(config_line)
        page = _path_to_page(path, title, url_context, use_dir_urls)

        if header:
            page.ancestors = header.ancestors + [header, ]
            header.children.append(page)

        yield page
        raise StopIteration

    elif not isinstance(config_line, dict):
        msg = ("Line in 'page' config is of type {0}, dict or string "
               "expected. Config: {1}").format(type(config_line), config_line)
        raise exceptions.ConfigurationError(msg)

    if len(config_line) > 1:
        raise exceptions.ConfigurationError(
            "Page configs should be in the format 'name: markdown.md'. The "
            "config contains an invalid entry: {0}".format(config_line))
    elif len(config_line) == 0:
        log.warning("Ignoring empty line in the pages config.")
        raise StopIteration

    next_cat_or_title, subpages_or_path = next(iter(config_line.items()))

    if isinstance(subpages_or_path, utils.string_types):
        path = subpages_or_path
        for sub in _follow(path, url_context, use_dir_urls, header=header, title=next_cat_or_title):
            yield sub
        raise StopIteration

    elif not isinstance(subpages_or_path, list):
        msg = ("Line in 'page' config is of type {0}, list or string "
               "expected for sub pages. Config: {1}"
               ).format(type(config_line), config_line)
        raise exceptions.ConfigurationError(msg)

    next_header = Header(title=next_cat_or_title, children=[])
    if header:
        next_header.ancestors = [header]
        header.children.append(next_header)
    yield next_header

    subpages = subpages_or_path

    for subpage in subpages:
        for sub in _follow(subpage, url_context, use_dir_urls, next_header):
            yield sub


def _generate_site_navigation(pages_config, url_context, use_dir_urls=True):
    """
    Returns a list of Page and Header instances that represent the
    top level site navigation.
    """
    nav_items = []
    pages = []

    previous = None

    for config_line in pages_config:

        for page_or_header in _follow(
                config_line, url_context, use_dir_urls):

            if isinstance(page_or_header, Header):

                if page_or_header.is_top_level:
                    nav_items.append(page_or_header)

            elif isinstance(page_or_header, Page):

                if page_or_header.is_top_level:
                    nav_items.append(page_or_header)

                pages.append(page_or_header)

                if previous:
                    page_or_header.previous_page = previous
                    previous.next_page = page_or_header
                previous = page_or_header

    if len(pages) == 0:
        raise exceptions.ConfigurationError(
            "No pages found in the pages config. "
            "Remove it entirely to enable automatic page discovery.")

    return (nav_items, pages)

import logging
from urllib.parse import urlsplit

from mkdocs.structure.pages import Page
from mkdocs.utils import nest_paths

log = logging.getLogger(__name__)


class Navigation:
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


class Section:
    def __init__(self, title, children):
        self.title = title
        self.children = children

        self.parent = None
        self.active = False

        self.is_section = True
        self.is_page = False
        self.is_link = False

    def __repr__(self):
        return f"Section(title='{self.title}')"

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


class Link:
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
        title = f"'{self.title}'" if (self.title is not None) else '[blank]'
        return f"Link(title={title}, url='{self.url}')"

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
        # Any documentation files not found in the nav should still have an associated page, so we
        # create them here. The Page object will automatically be assigned to `file.page` during
        # its creation (and this is the only way in which these page objects are accessible).
        for file in missing_from_config:
            Page(None, file, config)

    links = _get_by_type(items, Link)
    for link in links:
        scheme, netloc, path, query, fragment = urlsplit(link.url)
        if scheme or netloc:
            log.debug(
                f"An external link to '{link.url}' is included in the 'nav' configuration."
            )
        elif link.url.startswith('/'):
            log.debug(
                f"An absolute path to '{link.url}' is included in the 'nav' "
                "configuration, which presumably points to an external resource."
            )
    return Navigation(items, pages)

def _data_to_navigation(data, files, config):
    return [_handle_nav_element(element, files, config) for element in data]

def _handle_nav_element(data, files, config):
    assert type(data) in [dict, str], 'each nav element should be a dict or string'

    if isinstance(data, str):
        return Page(None, files.get_file_from_path(data), config)

    if isinstance(data, dict):
        assert len(data) == 1, 'each nav element dict should only have one element'
        name, value = list(data.items())[0]

        if isinstance(value, list):
            items = _merge_dicts(value)
            return _handle_blog_page(name, items, files, config) if items.get('sections', False) \
                else Section(title=name, children=_data_to_navigation(value, files, config))
        
        return Page(name, files.get_file_from_path(value), config)

    raise Exception('No conditions met when handling nav elements')

def _handle_blog_page(key, items, files, config):
    name = items['name'] if items.get('name', False) else \
                (None if key.endswith('.md') else key)
    file_path = items['path'] if items.get('path', False) else \
            (key if key.endswith('.md') else None)

    assert file_path, f'file path to {name} must be set in config file'

    page = Page(name, files.get_file_from_path(file_path), config)
    page.sections = _handle_blog_sections(items['sections'], files, config, page)
    return page

def _handle_blog_sections(sections, files, config, parent):
    sections = _merge_dicts(sections)
    ret = {}
    for name, folder_path in sections.items():
        article_files = files.get_files_from_folder_path(folder_path)
        article_pages = [Page(None, article_file, config, parent) for article_file in article_files]
        _add_previous_and_next_links(article_pages)
        ret[name] = article_pages
    return ret

def _merge_dicts(l):
    ret = {}
    for i in l:
        if isinstance(i, str):
            continue
        ret.update(i)
    return ret

def _get_by_type(nav, T):
    ret = []
    for item in nav:
        if isinstance(item, T):
            ret.append(item)
        if item.children:
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

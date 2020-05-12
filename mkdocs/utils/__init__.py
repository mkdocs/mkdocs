"""
Standalone file utils.

Nothing in this module should have an knowledge of config or the layout
and structure of the site and pages in the site.
"""


import logging
import os
import pkg_resources
import shutil
import re
import yaml
import fnmatch
import posixpath
from datetime import datetime, timezone
from urllib.parse import urlparse

from mkdocs import exceptions

log = logging.getLogger(__name__)

markdown_extensions = [
    '.markdown',
    '.mdown',
    '.mkdn',
    '.mkd',
    '.md'
]


def yaml_load(source, loader=yaml.Loader):
    """
    Wrap PyYaml's loader so we can extend it to suit our needs.

    Load all strings as unicode.
    https://stackoverflow.com/a/2967461/3609487
    """

    def construct_yaml_str(self, node):
        """
        Override the default string handling function to always return
        unicode objects.
        """
        return self.construct_scalar(node)

    class Loader(loader):
        """
        Define a custom loader derived from the global loader to leave the
        global loader unaltered.
        """

    # Attach our unicode constructor to our custom loader ensuring all strings
    # will be unicode on translation.
    Loader.add_constructor('tag:yaml.org,2002:str', construct_yaml_str)

    try:
        return yaml.load(source, Loader)
    finally:
        # TODO: Remove this when external calls are properly cleaning up file
        # objects. Some mkdocs internal calls, sometimes in test lib, will
        # load configs with a file object but never close it.  On some
        # systems, if a delete action is performed on that file without Python
        # closing that object, there will be an access error. This will
        # process the file and close it as there should be no more use for the
        # file once we process the yaml content.
        if hasattr(source, 'close'):
            source.close()


def modified_time(file_path):
    """
    Return the modified time of the supplied file. If the file does not exists zero is returned.
    see build_pages for use.
    """
    if os.path.exists(file_path):
        return os.path.getmtime(file_path)
    else:
        return 0.0


def get_build_timestamp():
    """
    Returns the number of seconds since the epoch.

    Support SOURCE_DATE_EPOCH environment variable for reproducible builds.
    See https://reproducible-builds.org/specs/source-date-epoch/
    """
    source_date_epoch = os.environ.get('SOURCE_DATE_EPOCH')
    if source_date_epoch is None:
        return int(datetime.now(timezone.utc).timestamp())

    return int(source_date_epoch)


def get_build_datetime():
    """
    Returns an aware datetime object.

    Support SOURCE_DATE_EPOCH environment variable for reproducible builds.
    See https://reproducible-builds.org/specs/source-date-epoch/
    """
    source_date_epoch = os.environ.get('SOURCE_DATE_EPOCH')
    if source_date_epoch is None:
        return datetime.now(timezone.utc)

    return datetime.fromtimestamp(int(source_date_epoch), timezone.utc)


def get_build_date():
    """
    Returns the displayable date string.

    Support SOURCE_DATE_EPOCH environment variable for reproducible builds.
    See https://reproducible-builds.org/specs/source-date-epoch/
    """
    return get_build_datetime().strftime('%Y-%m-%d')


def reduce_list(data_set):
    """ Reduce duplicate items in a list and preserve order """
    seen = set()
    return [item for item in data_set if
            item not in seen and not seen.add(item)]


def copy_file(source_path, output_path):
    """
    Copy source_path to output_path, making sure any parent directories exist.

    The output_path may be a directory.
    """
    output_dir = os.path.dirname(output_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    if os.path.isdir(output_path):
        output_path = os.path.join(output_path, os.path.basename(source_path))
    shutil.copyfile(source_path, output_path)


def write_file(content, output_path):
    """
    Write content to output_path, making sure any parent directories exist.
    """
    output_dir = os.path.dirname(output_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    with open(output_path, 'wb') as f:
        f.write(content)


def clean_directory(directory):
    """
    Remove the content of a directory recursively but not the directory itself.
    """
    if not os.path.exists(directory):
        return

    for entry in os.listdir(directory):

        # Don't remove hidden files from the directory. We never copy files
        # that are hidden, so we shouldn't delete them either.
        if entry.startswith('.'):
            continue

        path = os.path.join(directory, entry)
        if os.path.isdir(path):
            shutil.rmtree(path, True)
        else:
            os.unlink(path)


def get_html_path(path):
    """
    Map a source file path to an output html path.

    Paths like 'index.md' will be converted to 'index.html'
    Paths like 'about.md' will be converted to 'about/index.html'
    Paths like 'api-guide/core.md' will be converted to 'api-guide/core/index.html'
    """
    path = os.path.splitext(path)[0]
    if os.path.basename(path) == 'index':
        return path + '.html'
    return "/".join((path, 'index.html'))


def get_url_path(path, use_directory_urls=True):
    """
    Map a source file path to an output html path.

    Paths like 'index.md' will be converted to '/'
    Paths like 'about.md' will be converted to '/about/'
    Paths like 'api-guide/core.md' will be converted to '/api-guide/core/'

    If `use_directory_urls` is `False`, returned URLs will include the a trailing
    `index.html` rather than just returning the directory path.
    """
    path = get_html_path(path)
    url = '/' + path.replace(os.path.sep, '/')
    if use_directory_urls:
        return url[:-len('index.html')]
    return url


def is_markdown_file(path):
    """
    Return True if the given file path is a Markdown file.

    https://superuser.com/questions/249436/file-extension-for-markdown-files
    """
    return any(fnmatch.fnmatch(path.lower(), '*{}'.format(x)) for x in markdown_extensions)


def is_html_file(path):
    """
    Return True if the given file path is an HTML file.
    """
    ext = os.path.splitext(path)[1].lower()
    return ext in [
        '.html',
        '.htm',
    ]


def is_template_file(path):
    """
    Return True if the given file path is an HTML file.
    """
    ext = os.path.splitext(path)[1].lower()
    return ext in [
        '.html',
        '.htm',
        '.xml',
    ]


_ERROR_TEMPLATE_RE = re.compile(r'^\d{3}\.html?$')


def is_error_template(path):
    """
    Return True if the given file path is an HTTP error template.
    """
    return bool(_ERROR_TEMPLATE_RE.match(path))


def get_relative_url(url, other):
    """
    Return given url relative to other.
    """
    if other != '.':
        # Remove filename from other url if it has one.
        parts = posixpath.split(other)
        other = parts[0] if '.' in parts[1] else other
    relurl = posixpath.relpath(url, other)
    return relurl + '/' if url.endswith('/') else relurl


def normalize_url(path, page=None, base=''):
    """ Return a URL relative to the given page or using the base. """
    path = path_to_url(path or '.')
    # Allow links to be fully qualified URL's
    parsed = urlparse(path)
    if parsed.scheme or parsed.netloc or path.startswith(('/', '#')):
        return path

    # We must be looking at a local path.
    if page is not None:
        return get_relative_url(path, page.url)
    else:
        return posixpath.join(base, path)


def create_media_urls(path_list, page=None, base=''):
    """
    Return a list of URLs relative to the given page or using the base.
    """
    urls = []

    for path in path_list:
        urls.append(normalize_url(path, page, base))

    return urls


def path_to_url(path):
    """Convert a system path to a URL."""

    return '/'.join(path.split('\\'))


def get_theme_dir(name):
    """ Return the directory of an installed theme by name. """

    theme = get_themes()[name]
    return os.path.dirname(os.path.abspath(theme.load().__file__))


def get_themes():
    """ Return a dict of all installed themes as (name, entry point) pairs. """

    themes = {}
    builtins = pkg_resources.get_entry_map(dist='mkdocs', group='mkdocs.themes')

    for theme in pkg_resources.iter_entry_points(group='mkdocs.themes'):

        if theme.name in builtins and theme.dist.key != 'mkdocs':
            raise exceptions.ConfigurationError(
                "The theme {} is a builtin theme but {} provides a theme "
                "with the same name".format(theme.name, theme.dist.key))

        elif theme.name in themes:
            multiple_packages = [themes[theme.name].dist.key, theme.dist.key]
            log.warning("The theme %s is provided by the Python packages "
                        "'%s'. The one in %s will be used.",
                        theme.name, ','.join(multiple_packages), theme.dist.key)

        themes[theme.name] = theme

    return themes


def get_theme_names():
    """Return a list of all installed themes by name."""

    return get_themes().keys()


def dirname_to_title(dirname):
    """ Return a page tile obtained from a directory name. """
    title = dirname
    title = title.replace('-', ' ').replace('_', ' ')
    # Capitalize if the dirname was all lowercase, otherwise leave it as-is.
    if title.lower() == title:
        title = title.capitalize()

    return title


def get_markdown_title(markdown_src):
    """
    Get the title of a Markdown document. The title in this case is considered
    to be a H1 that occurs before any other content in the document.
    The procedure is then to iterate through the lines, stopping at the first
    non-whitespace content. If it is a title, return that, otherwise return
    None.
    """

    lines = markdown_src.replace('\r\n', '\n').replace('\r', '\n').split('\n')
    while lines:
        line = lines.pop(0).strip()
        if not line.strip():
            continue
        if not line.startswith('# '):
            return
        return line.lstrip('# ')


def find_or_create_node(branch, key):
    """
    Given a list, look for dictionary with a key matching key and return it's
    value. If it doesn't exist, create it with the value of an empty list and
    return that.
    """

    for node in branch:
        if not isinstance(node, dict):
            continue

        if key in node:
            return node[key]

    new_branch = []
    node = {key: new_branch}
    branch.append(node)
    return new_branch


def nest_paths(paths):
    """
    Given a list of paths, convert them into a nested structure that will match
    the pages config.
    """
    nested = []

    for path in paths:

        if os.path.sep not in path:
            nested.append(path)
            continue

        directory, _ = os.path.split(path)
        parts = directory.split(os.path.sep)

        branch = nested
        for part in parts:
            part = dirname_to_title(part)
            branch = find_or_create_node(branch, part)

        branch.append(path)

    return nested


class WarningFilter(logging.Filter):
    """ Counts all WARNING level log messages. """
    count = 0

    def filter(self, record):
        if record.levelno == logging.WARNING:
            self.count += 1
        return True


# A global instance to use throughout package
warning_filter = WarningFilter()

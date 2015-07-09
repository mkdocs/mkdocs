import os
import posixpath

MARKDOWN_EXTENSIONS = (
    '.markdown',
    '.mdown',
    '.mkdn',
    '.mkd',
    '.md',
)


def get_output_path(path):
    """
    Given an input file path, determine the corresponding output file path.
    """
    root, extension = os.path.splitext(os.path.basename(path))
    if extension.lower() in MARKDOWN_EXTENSIONS:
        if root in ('index', 'README'):
            directory = os.path.dirname(path)
        else:
            directory = os.path.splitext(path)[0]
        return os.path.join(directory, 'index.html')
    return path


def get_output_url(path, use_directory_urls=True):
    """
    Given a filepath determine the URL it should be mapped to.
    """
    url = '/' + path.replace(os.path.sep, '/')
    if use_directory_urls and url.endswith('/index.html'):
        return url[:-len('index.html')]
    return url


def get_relative_url(to_path, from_path, use_directory_urls=True):
    """
    Given two input files determine the relative URL path linking from
    one to the other.
    """
    if getattr(to_path, 'is_page', False):
        to_path = to_path.file.input_path

    to_url = get_output_url(get_output_path(to_path), use_directory_urls)
    from_url = get_output_url(get_output_path(from_path), use_directory_urls)
    return posixpath.relpath(to_url, from_url)


def is_active(item, current_page):
    """
    Return True if the navigation item is active, given the current page.
    """
    node = current_page
    while node is not None:
        if node is item:
            return True
        node = node.parent
    return False

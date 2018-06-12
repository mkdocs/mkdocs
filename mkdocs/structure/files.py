import fnmatch
import os
import shutil
import logging
import pathlib2 as pathlib
from functools import cmp_to_key

from mkdocs import utils


log = logging.getLogger(__name__)


class Files(object):
    """ A collection of File objects. """
    def __init__(self, files):
        self._files = files
        self.src_paths = {file.src_path: file for file in files}

    def __iter__(self):
        return iter(self._files)

    def __len__(self):
        return len(self._files)

    def __contains__(self, path):
        if not isinstance(path, pathlib.PurePath):
            path = pathlib.PurePath(path)
        return path in self.src_paths

    def get_file_from_path(self, path):
        """ Return a File instance with File.src_path equal to path. """
        if not isinstance(path, pathlib.PurePath):
            path = pathlib.PurePath(path)
        return self.src_paths.get(path)

    def append(self, file):
        """ Append file to Files collection. """
        self._files.append(file)
        self.src_paths[file.src_path] = file

    def copy_static_files(self, dirty=False):
        """ Copy static files from source to destination. """
        for file in self:
            if not file.is_documentation_page():
                file.copy_file(dirty)

    def documentation_pages(self):
        """ Return iterable of all Markdown page file objects. """
        return [file for file in self if file.is_documentation_page()]

    def static_pages(self):
        """ Return iterable of all static page file objects. """
        return [file for file in self if file.is_static_page()]

    def media_files(self):
        """ Return iterable of all file objects which are not documentation or static pages. """
        return [file for file in self if file.is_media_file()]

    def javascript_files(self):
        """ Return iterable of all javascript file objects. """
        return [file for file in self if file.is_javascript()]

    def css_files(self):
        """ Return iterable of all CSS file objects. """
        return [file for file in self if file.is_css()]

    def add_files_from_theme(self, env, config):
        """ Retrieve static files from Jinja environment and add to collection. """
        def filter(name):
            patterns = ['.*', '*.py', '*.pyc', '*.html', 'mkdocs_theme.yml']
            patterns.extend(config['theme'].static_templates)
            for pattern in patterns:
                if fnmatch.fnmatch(name, pattern):
                    return False
            return True
        for path in env.list_templates(filter_func=filter):
            for dir in config['theme'].dirs:
                # Find the first theme dir which contains path
                if pathlib.Path(dir, path).is_file():
                    self.append(File(path, dir, config['site_dir'], config['use_directory_urls']))
                    break


class File(object):
    """
    A MkDocs File object.

    Points to the source and destination locations of a file.

    The `path` argument must be a path that exists relative to `src_dir`.

    The `src_dir` and `dest_dir` must be absolute paths on the local file system.

    The `use_directory_urls` argument controls how destination paths are generated. If `False`, a Markdown file is
    mapped to an HTML file of the same name (the file extension is changed to `.html`). If True, a Markdown file is
    mapped to an HTML index file (`index.html`) nested in a directory using the "name" of the file in `path`. The
    `use_directory_urls` argument has no effect on non-Markdown files.

    File objects have the following properties, which are represented as pathlib objects (except for `url`):

    File.src_path
        The pure path of the source file relative to the source directory.

    File.abs_src_path
        The absolute concrete path of the source file.

    File.dest_path
        The pure path of the destination file relative to the destination directory.

    File.abs_dest_path
        The absolute concrete path of the destination file.

    File.url
        The url of the destination file relative to the destination directory as a string.
    """
    def __init__(self, path, src_dir, dest_dir, use_directory_urls):
        self.page = None
        self.src_path = pathlib.PurePath(path)
        self.abs_src_path = pathlib.Path(src_dir, self.src_path)
        self.name = 'index' if self.src_path.stem in ('index', 'README') else self.src_path.stem
        self.dest_path = self._get_dest_path(use_directory_urls)
        self.abs_dest_path = pathlib.Path(dest_dir, self.dest_path)

        if use_directory_urls and self.dest_path.name == 'index.html':
            self.url = self.dest_path.parent.as_posix()
            if self.url != '.':
                self.url += '/'
        else:
            self.url = self.dest_path.as_posix()

    def __eq__(self, other):

        def sub_dict(d):
            return dict((key, value) for key, value in d.items() if key in ['src_path', 'abs_src_path', 'url'])

        return (isinstance(other, self.__class__) and sub_dict(self.__dict__) == sub_dict(other.__dict__))

    def __ne__(self, other):
        return not self.__eq__(other)

    def _get_dest_path(self, use_directory_urls):
        """ Map source document path to the destination path. """
        if self.is_documentation_page():
            if use_directory_urls:
                if self.src_path.stem in ('index', 'README'):
                    # index.md or README.md => index.html
                    return self.src_path.with_name('index.html')
                else:
                    # foo.md => foo/index.html
                    return pathlib.PurePath(self.src_path.parent, self.src_path.stem, 'index.html')
            else:
                # foo.md => foo.html
                return self.src_path.with_suffix('.html')
        return pathlib.PurePath(self.src_path)

    def url_relative_to(self, other):
        """ Return url for file relative to other file. """
        return utils.get_relative_url(self.url, other.url if isinstance(other, File) else other)

    def copy_file(self, dirty=False):
        """ Copy source file to destination, ensuring parent directories exist. """
        if dirty and self.is_modified():
            log.debug("Skip copying unmodified file: '{}'".format(self.src_path))
        else:
            log.debug("Copying media file: '{}'".format(self.src_path))
            self.abs_dest_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(utils.text_type(self.abs_src_path), utils.text_type(self.abs_dest_path))

    def is_modified(self):
        try:
            return self.abs_dest_path.stat().st_mtime < self.abs_src_path.stat().st_mtime
        except OSError:
            # abs_dest_path doesn't exit
            return True

    def is_documentation_page(self):
        """ Return True if file is a Markdown page. """
        return self.src_path.suffix in utils.markdown_extensions

    def is_static_page(self):
        """ Return True if file is a static page (html, xml, json). """
        return self.src_path.suffix in (
            '.html',
            '.htm',
            '.xml',
            '.json',
        )

    def is_media_file(self):
        """ Return True if file is not a documentation or static page. """
        return not (self.is_documentation_page() or self.is_static_page())

    def is_javascript(self):
        """ Return True if file is a JavaScript file. """
        return self.src_path.suffix in (
            '.js',
            '.javascript',
        )

    def is_css(self):
        """ Return True if file is a CSS file. """
        return self.src_path.suffix in (
            '.css',
        )


def get_files(config):
    """ Walk the `docs_dir` and return a Files collection. """
    files = []
    exclude = ['.*', '/templates']

    for source_dir, dirnames, filenames in os.walk(config['docs_dir'], followlinks=True):
        relative_dir = os.path.relpath(source_dir, config['docs_dir'])

        for dirname in list(dirnames):
            path = os.path.normpath(os.path.join(relative_dir, dirname))
            # Skip any excluded directories
            if _filter_paths(basename=dirname, path=path, is_dir=True, exclude=exclude):
                dirnames.remove(dirname)
        dirnames.sort()

        for filename in _sort_files(filenames):
            path = os.path.normpath(os.path.join(relative_dir, filename))
            # Skip any excluded files
            if _filter_paths(basename=filename, path=path, is_dir=False, exclude=exclude):
                continue
            files.append(File(path, config['docs_dir'], config['site_dir'], config['use_directory_urls']))

    return Files(files)


def _sort_files(filenames):
    """ Always sort `index` as first filename in list. """

    def compare(x, y):
        if x == y:
            return 0
        if os.path.splitext(y)[0] == 'index':
            return 1
        if os.path.splitext(x)[0] == 'index' or x < y:
            return -1
        return 1

    return sorted(filenames, key=cmp_to_key(compare))


def _filter_paths(basename, path, is_dir, exclude):
    """ .gitignore style file filtering. """
    for item in exclude:
        # Items ending in '/' apply only to directories.
        if item.endswith('/') and not is_dir:
            continue
        # Items starting with '/' apply to the whole path.
        # In any other cases just the basename is used.
        match = path if item.startswith('/') else basename
        if fnmatch.fnmatch(match, item.strip('/')):
            return True
    return False

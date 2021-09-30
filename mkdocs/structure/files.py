import fnmatch
import os
import logging
from urllib.parse import quote as urlquote

from mkdocs import utils


log = logging.getLogger(__name__)


class Files:
    """ A collection of File objects. """
    def __init__(self, files):
        self._files = files

    def __iter__(self):
        return iter(self._files)

    def __len__(self):
        return len(self._files)

    def __contains__(self, path):
        return path in self.src_paths

    @property
    def src_paths(self):
        return {file.src_path: file for file in self._files}

    def get_file_from_path(self, path):
        """ Return a File instance with File.src_path equal to path. """
        return self.src_paths.get(os.path.normpath(path))

    def append(self, file):
        """ Append file to Files collection. """
        self._files.append(file)

    def remove(self, file):
        """ Remove file from Files collection. """
        self._files.remove(file)

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
            # '.*' filters dot files/dirs at root level whereas '*/.*' filters nested levels
            patterns = ['.*', '*/.*', '*.py', '*.pyc', '*.html', '*readme*', 'mkdocs_theme.yml']
            # Exclude translation files
            patterns.append("locales/*")
            patterns.extend(f'*{x}' for x in utils.markdown_extensions)
            patterns.extend(config['theme'].static_templates)
            for pattern in patterns:
                if fnmatch.fnmatch(name.lower(), pattern):
                    return False
            return True
        for path in env.list_templates(filter_func=filter):
            # Theme files do not override docs_dir files
            path = os.path.normpath(path)
            if path not in self:
                for dir in config['theme'].dirs:
                    # Find the first theme dir which contains path
                    if os.path.isfile(os.path.join(dir, path)):
                        self.append(File(path, dir, config['site_dir'], config['use_directory_urls']))
                        break


class File:
    """
    A MkDocs File object.

    Points to the source and destination locations of a file.

    The `path` argument must be a path that exists relative to `src_dir`.

    The `src_dir` and `dest_dir` must be absolute paths on the local file system.

    The `use_directory_urls` argument controls how destination paths are generated. If `False`, a Markdown file is
    mapped to an HTML file of the same name (the file extension is changed to `.html`). If True, a Markdown file is
    mapped to an HTML index file (`index.html`) nested in a directory using the "name" of the file in `path`. The
    `use_directory_urls` argument has no effect on non-Markdown files.

    File objects have the following properties, which are Unicode strings:

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
        self.src_path = os.path.normpath(path)
        self.abs_src_path = os.path.normpath(os.path.join(src_dir, self.src_path))
        self.name = self._get_stem()
        self.dest_path = self._get_dest_path(use_directory_urls)
        self.abs_dest_path = os.path.normpath(os.path.join(dest_dir, self.dest_path))
        self.url = self._get_url(use_directory_urls)

    def __eq__(self, other):
        return (
            isinstance(other, self.__class__) and
            self.src_path == other.src_path and
            self.abs_src_path == other.abs_src_path and
            self.url == other.url
        )

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return "File(src_path='{}', dest_path='{}', name='{}', url='{}')".format(
            self.src_path, self.dest_path, self.name, self.url
        )

    def _get_stem(self):
        """ Return the name of the file without it's extension. """
        filename = os.path.basename(self.src_path)
        stem, ext = os.path.splitext(filename)
        return 'index' if stem in ('index', 'README') else stem

    def _get_dest_path(self, use_directory_urls):
        """ Return destination path based on source path. """
        if self.is_documentation_page():
            parent, filename = os.path.split(self.src_path)
            if not use_directory_urls or self.name == 'index':
                # index.md or README.md => index.html
                # foo.md => foo.html
                return os.path.join(parent, self.name + '.html')
            else:
                # foo.md => foo/index.html
                return os.path.join(parent, self.name, 'index.html')
        return self.src_path

    def _get_url(self, use_directory_urls):
        """ Return url based in destination path. """
        url = self.dest_path.replace(os.path.sep, '/')
        dirname, filename = os.path.split(url)
        if use_directory_urls and filename == 'index.html':
            if dirname == '':
                url = '.'
            else:
                url = dirname + '/'
        return urlquote(url)

    def url_relative_to(self, other):
        """ Return url for file relative to other file. """
        return utils.get_relative_url(self.url, other.url if isinstance(other, File) else other)

    def copy_file(self, dirty=False):
        """ Copy source file to destination, ensuring parent directories exist. """
        if dirty and not self.is_modified():
            log.debug(f"Skip copying unmodified file: '{self.src_path}'")
        else:
            log.debug(f"Copying media file: '{self.src_path}'")
            utils.copy_file(self.abs_src_path, self.abs_dest_path)

    def is_modified(self):
        if os.path.isfile(self.abs_dest_path):
            return os.path.getmtime(self.abs_dest_path) < os.path.getmtime(self.abs_src_path)
        return True

    def is_documentation_page(self):
        """ Return True if file is a Markdown page. """
        return os.path.splitext(self.src_path)[1] in utils.markdown_extensions

    def is_static_page(self):
        """ Return True if file is a static page (html, xml, json). """
        return os.path.splitext(self.src_path)[1] in (
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
        return os.path.splitext(self.src_path)[1] in (
            '.js',
            '.javascript',
        )

    def is_css(self):
        """ Return True if file is a CSS file. """
        return os.path.splitext(self.src_path)[1] in (
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
            # Skip README.md if an index file also exists in dir
            if filename.lower() == 'readme.md' and 'index.md' in filenames:
                log.warning(f"Both index.md and readme.md found. Skipping readme.md from {source_dir}")
                continue
            files.append(File(path, config['docs_dir'], config['site_dir'], config['use_directory_urls']))

    return Files(files)


def _sort_files(filenames):
    """ Always sort `index` or `README` as first filename in list. """

    def key(f):
        if os.path.splitext(f)[0] in ['index', 'README']:
            return (0,)
        return (1, f)

    return sorted(filenames, key=key)


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

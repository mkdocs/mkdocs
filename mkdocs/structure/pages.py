# coding: utf-8

from __future__ import unicode_literals

import os
import io
import datetime
import logging

import markdown
from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor
from markdown.util import AMP_SUBSTITUTE

from mkdocs.structure.toc import get_toc
from mkdocs.utils import meta, urlparse, urlunparse, urljoin, get_markdown_title
from mkdocs.exceptions import MarkdownNotFound

log = logging.getLogger(__name__)


class Page(object):
    def __init__(self, title, file, config):
        file.page = self
        self.file = file
        self.title = title

        # Navigation attributes
        self.parent = None
        self.children = None
        self.previous_page = None
        self.next_page = None
        self.active = False

        self.is_section = False
        self.is_page = True
        self.is_link = False

        # Support SOURCE_DATE_EPOCH environment variable for "reproducible" builds.
        # See https://reproducible-builds.org/specs/source-date-epoch/
        if 'SOURCE_DATE_EPOCH' in os.environ:
            self.update_date = datetime.datetime.utcfromtimestamp(
                int(os.environ['SOURCE_DATE_EPOCH'])
            ).strftime("%Y-%m-%d")
        else:
            self.update_date = datetime.datetime.now().strftime("%Y-%m-%d")

        self._set_canonical_url(config.get('site_url', None))
        self._set_edit_url(config.get('repo_url', None), config.get('edit_uri', None))

        # Placeholders to be filled in later in the build process.
        self.markdown = None
        self.content = None
        self.toc = []
        self.meta = {}

    def __eq__(self, other):

        def sub_dict(d):
            return dict((key, value) for key, value in d.items() if key in ['title', 'file'])

        return (isinstance(other, self.__class__) and sub_dict(self.__dict__) == sub_dict(other.__dict__))

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        title = "'{}'".format(self.title) if (self.title is not None) else '[blank]'
        return "Page(title={}, url='{}')".format(title, self.abs_url or self.file.url)

    def _indent_print(self, depth=0):
        return '{}{}'.format('    ' * depth, repr(self))

    def _get_active(self):
        """ Return active status of page. """
        return self.__active

    def _set_active(self, value):
        """ Set active status of page and ancestors. """
        self.__active = bool(value)
        if self.parent is not None:
            self.parent.active = bool(value)

    active = property(_get_active, _set_active)

    @property
    def is_index(self):
        return self.file.name == 'index'

    @property
    def is_top_level(self):
        return self.parent is None

    @property
    def is_homepage(self):
        return self.is_top_level and self.is_index

    @property
    def url(self):
        return '' if self.file.url == '.' else self.file.url

    @property
    def ancestors(self):
        if self.parent is None:
            return []
        return [self.parent] + self.parent.ancestors

    def _set_canonical_url(self, base):
        if base:
            if not base.endswith('/'):
                base += '/'
            self.canonical_url = urljoin(base, self.url)
            self.abs_url = urlparse(self.canonical_url).path
        else:
            self.canonical_url = None
            self.abs_url = None

    def _set_edit_url(self, repo_url, edit_uri):
        if repo_url and edit_uri:
            src_path = self.file.src_path.replace('\\', '/')
            self.edit_url = urljoin(repo_url, edit_uri + src_path)
        else:
            self.edit_url = None

    def read_source(self, config):
        source = config['plugins'].run_event('page_read_source', None, config=config, page=self)
        if source is None:
            try:
                with io.open(self.file.abs_src_path, 'r', encoding='utf-8-sig', errors='strict') as f:
                    source = f.read()
            except IOError:
                log.error('File not found: {}'.format(self.file.src_path))
                raise
            except ValueError:
                log.error('Encoding error reading file: {}'.format(self.file.src_path))
                raise

        self.markdown, self.meta = meta.get_data(source)
        self._set_title()

    def _set_title(self):
        """
        Set the title for a Markdown document.

        Check these in order and use the first that returns a valid title:
        - value provided on init (passed in from config)
        - value of metadata 'title'
        - content of the first H1 in Markdown content
        - convert filename to title
        """
        if self.title is not None:
            return

        if 'title' in self.meta:
            self.title = self.meta['title']
            return

        title = get_markdown_title(self.markdown)

        if title is None:
            if self.is_homepage:
                title = 'Home'
            else:
                title = self.file.name.replace('-', ' ').replace('_', ' ')
                # Capitalize if the filename was all lowercase, otherwise leave it as-is.
                if title.lower() == title:
                    title = title.capitalize()

        self.title = title

    def render(self, config, files):
        """
        Convert the Markdown source file to HTML as per the config.
        """

        extensions = [
            _RelativePathExtension(self.file, files, config['strict'])
        ] + config['markdown_extensions']

        md = markdown.Markdown(
            extensions=extensions,
            extension_configs=config['mdx_configs'] or {}
        )
        self.content = md.convert(self.markdown)
        self.toc = get_toc(getattr(md, 'toc', ''))


class _RelativePathTreeprocessor(Treeprocessor):
    def __init__(self, file, files, strict):
        self.file = file
        self.files = files
        self.strict = strict

    def run(self, root):
        """
        Update urls on anchors and images to make them relative

        Iterates through the full document tree looking for specific
        tags and then makes them relative based on the site navigation
        """
        for element in root.iter():
            if element.tag == 'a':
                key = 'href'
            elif element.tag == 'img':
                key = 'src'
            else:
                continue

            url = element.get(key)
            new_url = self.path_to_url(url)
            element.set(key, new_url)

        return root

    def path_to_url(self, url):
        scheme, netloc, path, params, query, fragment = urlparse(url)

        if scheme or netloc or not path or AMP_SUBSTITUTE in url or '.' not in os.path.split(path)[-1]:
            # Ignore URLs unless they are a relative link to a source file.
            # AMP_SUBSTITUTE is used internally by Markdown only for email.
            # No '.' in the last part of a path indicates path does not point to a file.
            return url

        # Determine the filepath of the target.
        target_path = os.path.join(os.path.dirname(self.file.src_path), path)
        target_path = os.path.normpath(target_path).lstrip(os.sep)

        # Validate that the target exists in files collection.
        if target_path not in self.files:
            msg = (
                "Documentation file '{}' contains a link to '{}' which does not exist "
                "in the documentation directory.".format(self.file.src_path, target_path)
            )
            # In strict mode raise an error at this point.
            if self.strict:
                raise MarkdownNotFound(msg)
            # Otherwise, when strict mode isn't enabled, log a warning
            # to the user and leave the URL as it is.
            log.warning(msg)
            return url
        target_file = self.files.get_file_from_path(target_path)
        path = target_file.url_relative_to(self.file)
        components = (scheme, netloc, path, params, query, fragment)
        return urlunparse(components)


class _RelativePathExtension(Extension):
    """
    The Extension class is what we pass to markdown, it then
    registers the Treeprocessor.
    """

    def __init__(self, file, files, strict):
        self.file = file
        self.files = files
        self.strict = strict

    def extendMarkdown(self, md, md_globals):
        relpath = _RelativePathTreeprocessor(self.file, self.files, self.strict)
        md.treeprocessors.add("relpath", relpath, "_end")

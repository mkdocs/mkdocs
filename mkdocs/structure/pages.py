from __future__ import annotations

import copy
import logging
import os
import posixpath
import warnings
from typing import TYPE_CHECKING, Any, Callable, MutableMapping
from urllib.parse import unquote as urlunquote
from urllib.parse import urljoin, urlsplit, urlunsplit

import markdown
import markdown.extensions
import markdown.postprocessors
import markdown.treeprocessors
from markdown.util import AMP_SUBSTITUTE

from mkdocs.structure import StructureItem
from mkdocs.structure.toc import get_toc
from mkdocs.utils import get_build_date, get_markdown_title, meta, weak_property

if TYPE_CHECKING:
    from xml.etree import ElementTree as etree

    from mkdocs.config.defaults import MkDocsConfig
    from mkdocs.structure.files import File, Files
    from mkdocs.structure.toc import TableOfContents

_unescape: Callable[[str], str]
try:
    _unescape = markdown.treeprocessors.UnescapeTreeprocessor().unescape  # type: ignore
except AttributeError:
    _unescape = markdown.postprocessors.UnescapePostprocessor().run


log = logging.getLogger(__name__)


class Page(StructureItem):
    def __init__(self, title: str | None, file: File, config: MkDocsConfig) -> None:
        file.page = self
        self.file = file
        if title is not None:
            self.title = title

        # Navigation attributes
        self.children = None
        self.previous_page = None
        self.next_page = None
        self.active = False

        self.update_date = get_build_date()

        self._set_canonical_url(config.get('site_url', None))
        self._set_edit_url(
            config.get('repo_url', None), config.get('edit_uri'), config.get('edit_uri_template')
        )

        # Placeholders to be filled in later in the build process.
        self.markdown = None
        self._title_from_render: str | None = None
        self.content = None
        self.toc = []  # type: ignore
        self.meta = {}

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, self.__class__)
            and self.title == other.title
            and self.file == other.file
        )

    def __repr__(self):
        title = f"{self.title!r}" if self.title is not None else '[blank]'
        url = self.abs_url or self.file.url
        return f"Page(title={title}, url={url!r})"

    markdown: str | None
    """The original Markdown content from the file."""

    content: str | None
    """The rendered Markdown as HTML, this is the contents of the documentation."""

    toc: TableOfContents
    """An iterable object representing the Table of contents for a page. Each item in
    the `toc` is an [`AnchorLink`][mkdocs.structure.toc.AnchorLink]."""

    meta: MutableMapping[str, Any]
    """A mapping of the metadata included at the top of the markdown page."""

    @property
    def url(self) -> str:
        """The URL of the page relative to the MkDocs `site_dir`."""
        url = self.file.url
        if url in ('.', './'):
            return ''
        return url

    file: File
    """The documentation [`File`][mkdocs.structure.files.File] that the page is being rendered from."""

    abs_url: str | None
    """The absolute URL of the page from the server root as determined by the value
    assigned to the [site_url][] configuration setting. The value includes any
    subdirectory included in the `site_url`, but not the domain. [base_url][] should
    not be used with this variable."""

    canonical_url: str | None
    """The full, canonical URL to the current page as determined by the value assigned
    to the [site_url][] configuration setting. The value includes the domain and any
    subdirectory included in the `site_url`. [base_url][] should not be used with this
    variable."""

    @property
    def active(self) -> bool:
        """When `True`, indicates that this page is the currently viewed page. Defaults to `False`."""
        return self.__active

    @active.setter
    def active(self, value: bool):
        """Set active status of page and ancestors."""
        self.__active = bool(value)
        if self.parent is not None:
            self.parent.active = bool(value)

    @property
    def is_index(self) -> bool:
        return self.file.name == 'index'

    edit_url: str | None
    """The full URL to the source page in the source repository. Typically used to
    provide a link to edit the source page. [base_url][] should not be used with this
    variable."""

    @property
    def is_homepage(self) -> bool:
        """Evaluates to `True` for the homepage of the site and `False` for all other pages."""
        return self.is_top_level and self.is_index and self.file.url in ('.', './', 'index.html')

    previous_page: Page | None
    """The [page][mkdocs.structure.pages.Page] object for the previous page or `None`.
    The value will be `None` if the current page is the first item in the site navigation
    or if the current page is not included in the navigation at all."""

    next_page: Page | None
    """The [page][mkdocs.structure.pages.Page] object for the next page or `None`.
    The value will be `None` if the current page is the last item in the site navigation
    or if the current page is not included in the navigation at all."""

    children: None = None
    """Pages do not contain children and the attribute is always `None`."""

    is_section: bool = False
    """Indicates that the navigation object is a "section" object. Always `False` for page objects."""

    is_page: bool = True
    """Indicates that the navigation object is a "page" object. Always `True` for page objects."""

    is_link: bool = False
    """Indicates that the navigation object is a "link" object. Always `False` for page objects."""

    def _set_canonical_url(self, base: str | None) -> None:
        if base:
            if not base.endswith('/'):
                base += '/'
            self.canonical_url = canonical_url = urljoin(base, self.url)
            self.abs_url = urlsplit(canonical_url).path
        else:
            self.canonical_url = None
            self.abs_url = None

    def _set_edit_url(
        self,
        repo_url: str | None,
        edit_uri: str | None = None,
        edit_uri_template: str | None = None,
    ) -> None:
        if edit_uri or edit_uri_template:
            src_uri = self.file.src_uri
            if edit_uri_template:
                noext = posixpath.splitext(src_uri)[0]
                edit_uri = edit_uri_template.format(path=src_uri, path_noext=noext)
            else:
                assert edit_uri is not None and edit_uri.endswith('/')
                edit_uri += src_uri
            if repo_url:
                # Ensure urljoin behavior is correct
                if not edit_uri.startswith(('?', '#')) and not repo_url.endswith('/'):
                    repo_url += '/'
            else:
                try:
                    parsed_url = urlsplit(edit_uri)
                    if not parsed_url.scheme or not parsed_url.netloc:
                        log.warning(
                            f"edit_uri: {edit_uri!r} is not a valid URL, it should include the http:// (scheme)"
                        )
                except ValueError as e:
                    log.warning(f"edit_uri: {edit_uri!r} is not a valid URL: {e}")

            self.edit_url = urljoin(repo_url or '', edit_uri)
        else:
            self.edit_url = None

    def read_source(self, config: MkDocsConfig) -> None:
        source = config.plugins.on_page_read_source(page=self, config=config)
        if source is None:
            try:
                with open(self.file.abs_src_path, encoding='utf-8-sig', errors='strict') as f:
                    source = f.read()
            except OSError:
                log.error(f'File not found: {self.file.src_path}')
                raise
            except ValueError:
                log.error(f'Encoding error reading file: {self.file.src_path}')
                raise

        self.markdown, self.meta = meta.get_data(source)

    def _set_title(self) -> None:
        warnings.warn(
            "_set_title is no longer used in MkDocs and will be removed soon.", DeprecationWarning
        )

    @weak_property
    def title(self) -> str | None:  # type: ignore[override]
        """
        Returns the title for the current page.

        Before calling `read_source()`, this value is empty. It can also be updated by `render()`.

        Check these in order and use the first that returns a valid title:
        - value provided on init (passed in from config)
        - value of metadata 'title'
        - content of the first H1 in Markdown content
        - convert filename to title
        """
        if self.markdown is None:
            return None

        if 'title' in self.meta:
            return self.meta['title']

        if self._title_from_render:
            return self._title_from_render
        elif self.content is None:  # Preserve legacy behavior only for edge cases in plugins.
            title_from_md = get_markdown_title(self.markdown)
            if title_from_md is not None:
                return title_from_md

        if self.is_homepage:
            return 'Home'

        title = self.file.name.replace('-', ' ').replace('_', ' ')
        # Capitalize if the filename was all lowercase, otherwise leave it as-is.
        if title.lower() == title:
            title = title.capitalize()
        return title

    def render(self, config: MkDocsConfig, files: Files) -> None:
        """
        Convert the Markdown source file to HTML as per the config.
        """
        if self.markdown is None:
            raise RuntimeError("`markdown` field hasn't been set (via `read_source`)")

        relative_path_extension = _RelativePathExtension(self.file, files)
        extract_title_extension = _ExtractTitleExtension()
        md = markdown.Markdown(
            extensions=[
                relative_path_extension,
                extract_title_extension,
                *config['markdown_extensions'],
            ],
            extension_configs=config['mdx_configs'] or {},
        )
        self.content = md.convert(self.markdown)
        self.toc = get_toc(getattr(md, 'toc_tokens', []))
        self._title_from_render = extract_title_extension.title


class _RelativePathTreeprocessor(markdown.treeprocessors.Treeprocessor):
    def __init__(self, file: File, files: Files) -> None:
        self.file = file
        self.files = files

    def run(self, root: etree.Element) -> etree.Element:
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
            assert url is not None
            new_url = self.path_to_url(url)
            element.set(key, new_url)

        return root

    def path_to_url(self, url: str) -> str:
        scheme, netloc, path, query, fragment = urlsplit(url)

        if (
            scheme
            or netloc
            or not path
            or url.startswith('/')
            or url.startswith('\\')
            or AMP_SUBSTITUTE in url
            or '.' not in os.path.split(path)[-1]
        ):
            # Ignore URLs unless they are a relative link to a source file.
            # AMP_SUBSTITUTE is used internally by Markdown only for email.
            # No '.' in the last part of a path indicates path does not point to a file.
            return url

        # Determine the filepath of the target.
        target_uri = posixpath.join(posixpath.dirname(self.file.src_uri), urlunquote(path))
        target_uri = posixpath.normpath(target_uri).lstrip('/')

        # Validate that the target exists in files collection.
        target_file = self.files.get_file_from_path(target_uri)
        if target_file is None:
            log.warning(
                f"Documentation file '{self.file.src_uri}' contains a link to "
                f"'{target_uri}' which is not found in the documentation files."
            )
            return url
        if target_file.inclusion.is_excluded():
            log.info(
                f"Documentation file '{self.file.src_uri}' contains a link to "
                f"'{target_uri}' which is excluded from the built site."
            )
        path = target_file.url_relative_to(self.file)
        components = (scheme, netloc, path, query, fragment)
        return urlunsplit(components)


class _RelativePathExtension(markdown.extensions.Extension):
    """
    The Extension class is what we pass to markdown, it then
    registers the Treeprocessor.
    """

    def __init__(self, file: File, files: Files) -> None:
        self.file = file
        self.files = files

    def extendMarkdown(self, md: markdown.Markdown) -> None:
        relpath = _RelativePathTreeprocessor(self.file, self.files)
        md.treeprocessors.register(relpath, "relpath", 0)


class _ExtractTitleExtension(markdown.extensions.Extension):
    def __init__(self) -> None:
        self.title: str | None = None

    def extendMarkdown(self, md: markdown.Markdown) -> None:
        md.treeprocessors.register(
            _ExtractTitleTreeprocessor(self),
            "mkdocs_extract_title",
            priority=1,  # Close to the end.
        )


class _ExtractTitleTreeprocessor(markdown.treeprocessors.Treeprocessor):
    def __init__(self, ext: _ExtractTitleExtension) -> None:
        self.ext = ext

    def run(self, root: etree.Element) -> etree.Element:
        for el in root:
            if el.tag == 'h1':
                # Drop anchorlink from the element, if present.
                if len(el) > 0 and el[-1].tag == 'a' and not (el.tail or '').strip():
                    el = copy.copy(el)
                    del el[-1]
                # Extract the text only, recursively.
                self.ext.title = _unescape(''.join(el.itertext()))
            break
        return root

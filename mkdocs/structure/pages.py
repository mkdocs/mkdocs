from mkdocs.compat import urlparse, urlunparse
from mkdocs.structure.toc import get_toc

from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor
from markdown.util import AMP_SUBSTITUTE
import markdown
import io
import os


class Page(object):
    def __init__(self, title, filepath):
        self.title = title
        self.file = None

        # Navigation attributes
        self.parent = None
        self.previous = None
        self.next = None

        self.is_section = False
        self.is_page = True

        # Build attributes
        self.markdown = None
        self.html = None
        self.meta = {}
        self.toc = []

        # '_filepath' is only used temporarily, when a page is first
        # created based on the 'pages' configuration.
        # The '.file' attribute should be used as the public API.
        self._filepath = filepath

    def build(self, md):
        input_filepath = self.file.full_input_path
        self.markdown = io.open(input_filepath, 'r', encoding='utf-8').read()
        self.html = md.convert(self.markdown)
        self.meta = getattr(md, 'Meta', {})
        self.toc = get_toc(getattr(md, 'toc', ''))
        if self.title is None:
            self.title = self.get_default_title()

    def get_default_title(self):
        # Determine the title based on the first item in the table of contents.
        if self.toc:
            return self.toc[0].title

        # Failing that, determine the title based on the filename.
        title = self.file.root.replace('-', ' ').replace('_', ' ')
        if title.lower() == title:
            # Capitalize if the filename was all lowercase.
            title = title.capitalize()
        return title


def build_pages(files):
    pages = []
    for file in files.documentation_pages():
        md = markdown.Markdown(
            extensions=[
                _RelativePathExtension(file, files, strict=False),
                'meta', 'toc', 'tables', 'fenced_code'
            ],
        )
        file.page.build(md)
    return pages


def _path_to_url(url, file, files, strict):
    scheme, netloc, path, params, query, fragment = urlparse(url)

    if scheme or netloc or not path or AMP_SUBSTITUTE in url:
        # Ignore URLs unless they are a relative link to a source file.
        # AMP_SUBSTITUTE is used internally by Markdown only for email.
        return url

    target_path = os.path.join(os.path.dirname(file.input_path), path)
    target_path = os.path.normpath(target_path).lstrip('/')

    # Validate that the target exists.
    if target_path not in files.input_paths:
        # TODO: This should be a warning.
        # TODO: We could rephrase this for img links:
        #       'contains an image link'
        # TODO: We could rephrase this for non-markdown targets:
        #       'does not exist in either the docs or theme directories'
        print (
            "Documentation file '%s' contains a link to '%s' which "
            "does not exist in the docs directory."
            % (file.input_path, target_path)
        )

    # TODO rewrite the URL.

    fragments = (scheme, netloc, path, params, query, fragment)
    url = urlunparse(fragments)
    return url


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
            new_url = _path_to_url(url, self.file, self.files, self.strict)
            element.set(key, new_url)

        return root


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

"""
# Relative Path Markdown Extension

During the MkDocs build we rewrite URLs that link to local
Markdown or media files. Using the following pages configuration
we can look at how the output is changed.

    pages:
    - ['index.md']
    - ['tutorial/install.md']
    - ['tutorial/intro.md']

## Markdown URLs

When linking from `install.md` to `intro.md` the link would
simply be `[intro](intro.md)`. However, when we build
`install.md` we place it in a directory to create nicer URLs.
This means that the path to `intro.md` becomes `../intro/`

## Media URLs

To make it easier to work with media files and store them all
under one directory we re-write those to all be based on the
root. So, with the following markdown to add an image.

    ![The initial MkDocs layout](img/initial-layout.png)

The output would depend on the location of the Markdown file it
was added too.

Source file         | Generated Path    | Image Path                   |
------------------- | ----------------- | ---------------------------- |
index.md            | /                 | ./img/initial-layout.png     |
tutorial/install.md | tutorial/install/ | ../img/initial-layout.png    |
tutorial/intro.md   | tutorial/intro/   | ../../img/initial-layout.png |

"""

from __future__ import unicode_literals

import logging
import os

from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor
from markdown.util import AMP_SUBSTITUTE

from mkdocs import utils
from mkdocs.exceptions import MarkdownNotFound

log = logging.getLogger(__name__)


def path_to_url(url, nav, strict):

    scheme, netloc, path, params, query, fragment = (
        utils.urlparse(url))

    if scheme or netloc or not path or AMP_SUBSTITUTE in url:
        # Ignore URLs unless they are a relative link to a markdown file.
        # AMP_SUBSTITUTE is used internally by Markdown only for email,which is
        # not a relative link. As urlparse errors on them, skip explicitly
        return url

    if nav and not utils.is_markdown_file(path):
        path = utils.create_relative_media_url(nav, path)
    elif nav:
        # If the site navigation has been provided, then validate
        # the internal hyperlink, making sure the target actually exists.
        target_file = nav.file_context.make_absolute(path)

        if target_file.startswith(os.path.sep):
            target_file = target_file[1:]

        if target_file not in nav.source_files:
            source_file = nav.file_context.current_file
            msg = (
                'The page "%s" contained a hyperlink to "%s" which '
                'is not listed in the "pages" configuration.'
            ) % (source_file, target_file)

            # In strict mode raise an error at this point.
            if strict:
                raise MarkdownNotFound(msg)
            # Otherwise, when strict mode isn't enabled, log a warning
            # to the user and leave the URL as it is.
            log.warning(msg)
            return url
        path = utils.get_url_path(target_file, nav.use_directory_urls)
        path = nav.url_context.make_relative(path)
    else:
        path = utils.get_url_path(path).lstrip('/')

    # Convert the .md hyperlink to a relative hyperlink to the HTML page.
    fragments = (scheme, netloc, path, params, query, fragment)
    url = utils.urlunparse(fragments)
    return url


class RelativePathTreeprocessor(Treeprocessor):

    def __init__(self, site_navigation, strict):
        self.site_navigation = site_navigation
        self.strict = strict

    def run(self, root):
        """Update urls on anchors and images to make them relative

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
            new_url = path_to_url(url, self.site_navigation, self.strict)
            element.set(key, new_url)

        return root


class RelativePathExtension(Extension):
    """
    The Extension class is what we pass to markdown, it then
    registers the Treeprocessor.
    """

    def __init__(self, site_navigation, strict):
        self.site_navigation = site_navigation
        self.strict = strict

    def extendMarkdown(self, md, md_globals):
        relpath = RelativePathTreeprocessor(self.site_navigation, self.strict)
        md.treeprocessors.add("relpath", relpath, "_end")

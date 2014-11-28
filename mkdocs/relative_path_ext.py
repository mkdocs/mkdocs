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
from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor

from mkdocs import utils
from mkdocs.compat import urlparse, urlunparse


def _iter(node):
    # TODO: Remove when dropping Python 2.6. Replace this
    # function call with note.iter()
    return [node] + node.findall('.//*')


def path_to_url(url, nav):
    scheme, netloc, path, query, query, fragment = urlparse(url)

    if scheme or netloc or not path:
        # Ignore URLs unless they are a relative link to a markdown file.
        return url

    if nav and not utils.is_markdown_file(path):
        path = utils.create_media_urls(nav, [path])[0]
    elif nav:
        # If the site navigation has been provided, then validate
        # the internal hyperlink, making sure the target actually exists.
        target_file = nav.file_context.make_absolute(path)
        if target_file not in nav.source_files:
            source_file = nav.file_context.current_file
            msg = (
                'The page "%s" contained a hyperlink to "%s" which '
                'is not listed in the "pages" configuration.'
            )
            assert False, msg % (source_file, target_file)
        path = utils.get_url_path(target_file, nav.use_directory_urls)
        path = nav.url_context.make_relative(path)
    else:
        path = utils.get_url_path(path).lstrip('/')

    # Convert the .md hyperlink to a relative hyperlink to the HTML page.
    url = urlunparse((scheme, netloc, path, query, query, fragment))
    return url


class RelativePathTreeprocessor(Treeprocessor):

    def __init__(self, site_navigation):
        self.site_navigation = site_navigation

    def run(self, root):
        """Update urls on anchors and images to make them relative

        Iterates through the full document tree looking for specific
        tags and then makes them relative based on the site navigation
        """

        for element in _iter(root):

            if element.tag == 'a':
                key = 'href'
            elif element.tag == 'img':
                key = 'src'
            else:
                continue

            url = element.get(key)
            new_url = path_to_url(url, self.site_navigation)
            element.set(key, new_url)

        return root


class RelativePathExtension(Extension):
    """
    The Extension class is what we pass to markdown, it then
    registers the Treeprocessor.
    """

    def __init__(self, site_navigation):
        self.site_navigation = site_navigation

    def extendMarkdown(self, md, md_globals):
        relpath = RelativePathTreeprocessor(self.site_navigation)
        md.treeprocessors.add("relpath", relpath, "_end")

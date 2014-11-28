from markdown.treeprocessors import Treeprocessor
from markdown.extensions import Extension

from mkdocs.compat import urlparse, urlunparse
from mkdocs import utils


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

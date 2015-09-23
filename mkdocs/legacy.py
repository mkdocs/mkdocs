from __future__ import unicode_literals
import logging

from mkdocs import utils
from mkdocs.exceptions import ConfigurationError

log = logging.getLogger(__name__)


def pages_compat_shim(original_pages):
    """
    Support legacy pages configuration

    Re-write the pages config fron MkDocs <=0.12 to match the
    new nested structure added in 0.13.

    Given a pages configuration in the old style of:

        pages:
        - ['index.md', 'Home']
        - ['user-guide/writing-your-docs.md', 'User Guide']
        - ['user-guide/styling-your-docs.md', 'User Guide']
        - ['about/license.md', 'About', 'License']
        - ['about/release-notes.md', 'About']
        - ['help/contributing.md', 'Help', 'Contributing']
        - ['support.md']
        - ['cli.md', 'CLI Guide']

    Rewrite it to look like:

        pages:
        - Home: index.md
        - User Guide:
            - user-guide/writing-your-docs.md
            - user-guide/styling-your-docs.md
        - About:
            - License: about/license.md
            - about/release-notes.md
        - Help:
            - Contributing: about/contributing.md
        - support.md
        - CLI Guide: cli.md

    TODO: Remove in 1.0
    """

    log.warning("The pages config in the mkdocs.yml uses the deprecated "
                "structure. This will be removed in the next release of "
                "MkDocs. See for details on updating: "
                "http://www.mkdocs.org/about/release-notes/")

    new_pages = []

    for config_line in original_pages:

        if isinstance(config_line, utils.string_types):
            config_line = [config_line, ]

        if len(config_line) not in (1, 2, 3):
            msg = (
                "Line in 'page' config contained {0} items. In Line {1}. "
                "Expected 1, 2 or 3 strings.".format(
                    config_line, len(config_line))
            )
            raise ConfigurationError(msg)

        # First we need to pad out the config line as it could contain
        # 1-3 items.
        path, category, title = (list(config_line) + [None, None])[:3]

        if len(new_pages) > 0:
            # Get the previous top-level page so we can see if the category
            # matches up with the one we have now.
            prev_cat, subpages = next(iter(new_pages[-1].items()))
        else:
            # We are on the first page
            prev_cat, subpages = None, []

        # If the category is different, add a new top level category. If the
        # previous category is None, the it's another top level one too.
        if prev_cat is None or prev_cat != category:
            subpages = []
            new_pages.append({category: subpages})

        # Add the current page to the determined category.
        subpages.append({title: path})

    # We need to do a bit of cleaning up to match the new structure. In the
    # above example, pages can either be `- file.md` or `- Title: file.md`.
    # For pages without a title we currently have `- None: file.md` - so we
    # need to remove those Nones by changing from a dict to just a string with
    # the path.
    for i, category in enumerate(new_pages):

        # Categories are a dictionary with one key as the name and the value
        # is a list of pages. So, grab that from the dict.
        category, pages = next(iter(category.items()))

        # If we only have one page, then we can assume it is a top level
        # category and no further nesting is required unless that single page
        # has a title itself,
        if len(pages) == 1:
            title, path = pages.pop().popitem()
            # If we have a title, it should be a sub page
            if title is not None:
                pages.append({title: path})
            # if we have a category, but no title it should be a top-level page
            elif category is not None:
                new_pages[i] = {category: path}
            # if we have no category or title, it must be a top level page with
            # an atomatic title.
            else:
                new_pages[i] = path
        else:
            # We have more than one page, so the category is valid. We just
            # need to iterate through and convert any {None: path} dicts to
            # be just the path string.
            for j, page in enumerate(pages):
                title, path = page.popitem()
                if title:
                    pages[j] = {title: path}
                else:
                    pages[j] = path

    return new_pages

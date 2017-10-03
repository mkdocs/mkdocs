# coding: utf-8

from __future__ import unicode_literals

import json
from mkdocs import utils

try:                                    # pragma: no cover
    from html.parser import HTMLParser  # noqa
except ImportError:                     # pragma: no cover
    from HTMLParser import HTMLParser   # noqa


class SearchIndex(object):
    """
    Search index is a collection of pages and sections (heading
    tags and their following content are sections).
    """

    def __init__(self):
        self._entries = []

    def _find_toc_by_id(self, toc, id_):
        """
        Given a table of contents and HTML ID, iterate through
        and return the matched item in the TOC.
        """
        for toc_item in toc:
            if toc_item.url[1:] == id_:
                return toc_item
            toc_item_r = self._find_toc_by_id(toc_item.children, id_)
            if toc_item_r is not None:
                return toc_item_r

    def _add_entry(self, title, text, loc):
        """
        A simple wrapper to add an entry and ensure the contents
        is UTF8 encoded.
        """
        self._entries.append({
            'title': title,
            'text': utils.text_type(text.strip().encode('utf-8'), encoding='utf-8'),
            'location': loc
        })

    def add_entry_from_context(self, page):
        """
        Create a set of entries in the index for a page. One for
        the page itself and then one for each of its' heading
        tags.
        """

        # Create the content parser and feed in the HTML for the
        # full page. This handles all the parsing and prepares
        # us to iterate through it.
        parser = ContentParser()
        parser.feed(page.content)
        parser.close()

        # Get the absolute URL for the page, this is then
        # prepended to the urls of the sections
        abs_url = page.abs_url

        # Create an entry for the full page.
        self._add_entry(
            title=page.title,
            text=self.strip_tags(page.content).rstrip('\n'),
            loc=abs_url
        )

        for section in parser.data:
            self.create_entry_for_section(section, page.toc, abs_url)

    def create_entry_for_section(self, section, toc, abs_url):
        """
        Given a section on the page, the table of contents and
        the absolute url for the page create an entry in the
        index
        """

        toc_item = self._find_toc_by_id(toc, section.id)

        if toc_item is not None:
            self._add_entry(
                title=toc_item.title,
                text=u" ".join(section.text),
                loc=abs_url + toc_item.url
            )

    def generate_search_index(self):
        """python to json conversion"""
        page_dicts = {
            'docs': self._entries,
        }
        return json.dumps(page_dicts, sort_keys=True, indent=4)

    def strip_tags(self, html):
        """strip html tags from data"""
        s = HTMLStripper()
        s.feed(html)
        return s.get_data()


class HTMLStripper(HTMLParser):
    """
    A simple HTML parser that stores all of the data within tags
    but ignores the tags themselves and thus strips them from the
    content.
    """

    def __init__(self, *args, **kwargs):
        # HTMLParser is a old-style class in Python 2, so
        # super() wont work here.
        HTMLParser.__init__(self, *args, **kwargs)

        self.data = []

    def handle_data(self, d):
        """
        Called for the text contents of each tag.
        """
        self.data.append(d)

    def get_data(self):
        return '\n'.join(self.data)


class ContentSection(object):
    """
    Used by the ContentParser class to capture the information we
    need when it is parsing the HMTL.
    """

    def __init__(self, text=None, id_=None, title=None):
        self.text = text or []
        self.id = id_
        self.title = title

    def __eq__(self, other):
        return all([
            self.text == other.text,
            self.id == other.id,
            self.title == other.title
        ])


class ContentParser(HTMLParser):
    """
    Given a block of HTML, group the content under the preceding
    heading tags which can then be used for creating an index
    for that section.
    """

    def __init__(self, *args, **kwargs):

        # HTMLParser is a old-style class in Python 2, so
        # super() wont work here.
        HTMLParser.__init__(self, *args, **kwargs)

        self.data = []
        self.section = None
        self.is_header_tag = False

    def handle_starttag(self, tag, attrs):
        """Called at the start of every HTML tag."""

        # We only care about the opening tag for headings.
        if tag not in (["h%d" % x for x in range(1, 7)]):
            return

        # We are dealing with a new header, create a new section
        # for it and assign the ID if it has one.
        self.is_header_tag = True
        self.section = ContentSection()
        self.data.append(self.section)

        for attr in attrs:
            if attr[0] == "id":
                self.section.id = attr[1]

    def handle_endtag(self, tag):
        """Called at the end of every HTML tag."""

        # We only care about the opening tag for headings.
        if tag not in (["h%d" % x for x in range(1, 7)]):
            return

        self.is_header_tag = False

    def handle_data(self, data):
        """
        Called for the text contents of each tag.
        """

        if self.section is None:
            # This means we have some content at the start of the
            # HTML before we reach a heading tag. We don't actually
            # care about that content as it will be added to the
            # overall page entry in the search. So just skip it.
            return

        # If this is a header, then the data is the title.
        # Otherwise it is content of something under that header
        # section.
        if self.is_header_tag:
            self.section.title = data
        else:
            self.section.text.append(data.rstrip('\n'))

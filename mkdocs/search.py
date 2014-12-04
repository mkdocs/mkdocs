from __future__ import unicode_literals

from mkdocs.compat import HTMLParser, unicode
import json


class SearchIndex(object):
    """
    Data holder for the search index.
    """

    def __init__(self):
        self.pages = []

    def add_entry_from_context(self, page, content, nav, toc):
        """add entry based on predetermined properties"""

        # create parser for analysing content
        # we parse the content since the toc dont have the data
        # and we need to use toc urls
        parser = ContentParser()
        parser.feed(content)

        abs_url = nav.url_context.make_relative(page.abs_url)

        # create entry for page
        self.create_entry(
            title=page.title,
            text=self.strip_tags(content).rstrip('\n'),
            tags="",
            loc=abs_url
        )

        # check all found sections against toc, match on id
        for section in parser.data:
            # toc h1
            for toc_item in toc:
                # dont check sub sections if found
                if toc_item.url[1:] == section.id and len(section.text) > 0:
                    # create entry
                    self.create_entry(
                        title=toc_item.title,
                        text=u" ".join(section.text),
                        tags="",
                        loc=abs_url + toc_item.url
                    )
                # not found, check h2
                else:
                    # toc h2
                    for toc_sub_item in toc_item.children:
                        if toc_sub_item.url[1:] == section.id and len(section.text) > 0:
                            # create entry
                            self.create_entry(
                                title=toc_sub_item.title,
                                text=u" ".join(section.text),
                                tags="",
                                loc=abs_url + toc_sub_item.url
                            )

    def create_entry(self, title, text, tags, loc):
        """create an index entry"""
        self.pages.append(dict(
            title=title,
            text=unicode(text.strip().encode('utf-8'), encoding='utf-8'),
            tags=tags,
            loc=loc
        ))

    def generate_search_index(self):
        """python to json conversion"""
        page_dicts = {
            'pages': self.pages,
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


class ContentSection():
    """
    Used by the ContentParser class to capture the information we
    need when it is parsing the HMTL.
    """

    def __init__(self):
        self.text = []
        self.id = None
        self.title = None


class ContentParser(HTMLParser):
    """
    Given a block of HTML, group the content under the preceding
    H1 or H2 tags which can then be used for creating an index
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

        # We only care about the opening tag for H1 and H2.
        if tag not in ("h1", "h2"):
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

        # We only care about the opening tag for H1 and H2.
        if tag not in ("h1", "h2"):
            return

        self.is_header_tag = False

    def handle_data(self, data):
        """
        Called for the text contents of each tag.
        """

        if self.section is None:
            # This means we have some content at the start of the
            # HTML before we reach a H1 or H2. We don't actually
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

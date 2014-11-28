from __future__ import unicode_literals

from mkdocs.compat import HTMLParser, unicode
import json


class SearchIndex(object):
    """
    Data holder for the search index.
    """

    def __init__(self):
        self.pages = []

    def add_entry_from_context(self, page, content, nav, toc, meta, config):
        """add entry based on predetermined properties"""

        # create parser for analysing content
        # we parse the content since the toc dont have the data
        # and we need to use toc urls
        parser = ContentParser()
        parser.feed(content)

        # create entry for page
        self.create_entry(
            title=page.title,
            text=self.strip_tags(content).rstrip('\n'),
            tags="",
            loc=page.abs_url
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
                        loc=page.abs_url + toc_item.url
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
                                loc=page.abs_url + toc_sub_item.url
                            )

    def create_entry(self, title, text, tags, loc):
        """create an index entry"""
        entry = SearchEntry(
            title=title,
            text=unicode(text.strip().encode('utf-8'), encoding='utf-8'),
            tags=tags,
            loc=loc
        )
        self.pages.append(entry)

    def generate_search_index(self):
        """python to json conversion"""
        page_dicts = {
            'pages': [p.to_dict() for p in self.pages],
        }
        return json.dumps(page_dicts, sort_keys=True, indent=4)

    def strip_tags(self, html):
        """strip html tags from data"""
        s = MLStripper()
        s.feed(html)
        return s.get_data()


class SearchEntry(object):
    """data container for a index entry"""

    def __init__(self, title, text, tags, loc):
        self.title = title
        self.text = text
        self.tags = tags
        self.loc = loc

    def to_dict(self):
        return {
            'title': self.title,
            'text': self.text,
            'tags': self.tags,
            'loc': self.loc,
        }


class MLStripper(HTMLParser):
    """class for stripping html tags"""

    def __init__(self):
        self.reset()
        self.fed = []
        self.strict = False
        self.convert_charrefs = True

    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        return ''.join(self.fed)


class ContentParser(HTMLParser):
    """class for parsing html-sections"""
    def __init__(self):
        HTMLParser.__init__(self)

        self.data = []
        self.section = ""
        self.is_header_tag = False

    def handle_starttag(self, tag, attrs):
        """hook - tag start"""
        if tag in ("h1", "h2"):
            self.is_header_tag = True
            self.section = ContentSection()
            for attr in attrs:
                if attr[0] == "id":
                    self.section.id = attr[1]

    def handle_endtag(self, tag):
        """hook - tag end"""
        if tag in ("h1", "h2"):
            self.is_header_tag = False
            self.data.append(self.section)

    def handle_data(self, data):
        """hook - data"""
        if self.is_header_tag:
            self.section.title = data
        else:
            self.section.text.append(data.rstrip('\n'))


class ContentSection():
    """content-holder for html-sections"""

    def __init__(self):
        self.text = []
        self.id = ""
        self.title = ""

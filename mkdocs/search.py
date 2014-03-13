from pprint import pprint
from HTMLParser import HTMLParser
import json
import re
from HTMLParser import HTMLParser

class SearchIndex(object):
    def __init__(self):
        self.pages = []


    def addEntryFromContext(self, page, content, nav, toc, meta, config):

        parser = ContentParser()
        parser.feed(content)

        self.createEntry(
            title=page.title,
            text=self.strip_tags(content).rstrip('\n'),
            tags="",
            loc=page.abs_url
        )

        for section in parser.data:
            for toc_item in toc:
                if toc_item.url[1:] == section.id and len(section.text) > 0:
                    self.createEntry(
                        title=toc_item.title,
                        text=" ".join(section.text),
                        tags="",
                        loc=page.abs_url[:-1] + toc_item.url
                    )
                else:
                    for toc_sub_item in toc_item.children:
                        if toc_sub_item.url[1:] == section.id and len(section.text) > 0:
                            self.createEntry(
                                title=toc_sub_item.title,
                                text=" ".join(section.text),
                                tags="",
                                loc=page.abs_url[:-1] + toc_sub_item.url
                            )

    def createEntry(self, title,text,tags,loc):
        entry = SearchEntry(
            title=title,
            text=text.strip().encode('utf-8'),
            tags=tags,
            loc=loc
        )
        self.pages.append(entry)

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def generate_search_index(self):
        s = self.to_json()
        return s

    def strip_tags(self,html):
        s = MLStripper()
        s.feed(html)
        return s.get_data()

class SearchEntry(object):
    def __init__(self, title, text, tags, loc):
        self.title = title
        self.text = text
        self.tags = tags
        self.loc = loc

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

class ContentParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)

        self.data = []
        self.section = ""
        self.is_header_tag = False

    def handle_starttag(self, tag, attrs):
        if tag in ("h1","h2"):
            self.is_header_tag = True
            self.section = ContentSection()
            for attr in attrs:
                if attr[0] == "id":
                    self.section.id = attr[1]

    def handle_endtag(self, tag):
        if tag in ("h1","h2"):
            self.is_header_tag = False
            self.data.append(self.section)

    def handle_data(self, data):
        if self.is_header_tag:
            self.section.title = data
        else:
            self.section.text.append(data.rstrip('\n'))


class ContentSection():
     def __init__(self):
        self.text = []
        self.id = ""
        self.title = ""
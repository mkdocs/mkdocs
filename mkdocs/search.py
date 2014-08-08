from pprint import pprint
from HTMLParser import HTMLParser
import json
import re
from HTMLParser import HTMLParser

#dataholder for index
class SearchIndex(object):
    def __init__(self):
        self.pages = []

    #add entry based on predetermined properties
    def addEntryFromContext(self, page, content, nav, toc, meta, config):

        #create parser for analysing content
        #we parse the content since the toc dont have the data
        #and we need to use toc urls
        parser = ContentParser()
        parser.feed(content)

        #create entry for page
        self.createEntry(
            title=page.title,
            text=self.strip_tags(content).rstrip('\n'),
            tags="",
            loc=page.abs_url
        )

        #check all found sections against toc, match on id
        for section in parser.data:
            #toc h1
            for toc_item in toc:
                #dont check sub sections if found
                if toc_item.url[1:] == section.id and len(section.text) > 0:
                    #create entry
                    self.createEntry(
                        title=toc_item.title,
                        text=" ".join(section.text),
                        tags="",
                        loc=page.abs_url[:-1] + toc_item.url
                    )
                #not fund, check h2
                else:
                    #toc h2
                    for toc_sub_item in toc_item.children:
                        if toc_sub_item.url[1:] == section.id and len(section.text) > 0:
                            #create entry
                            self.createEntry(
                                title=toc_sub_item.title,
                                text=" ".join(section.text),
                                tags="",
                                loc=page.abs_url[:-1] + toc_sub_item.url
                            )

    #create a index entry
    def createEntry(self, title,text,tags,loc):
        entry = SearchEntry(
            title=title,
            text=text.strip().encode('utf-8'),
            tags=tags,
            loc=loc
        )
        self.pages.append(entry)

    #python to JSON conversion
    def generate_search_index(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    #strip html tags from data
    def strip_tags(self,html):
        s = MLStripper()
        s.feed(html)
        return s.get_data()

#data container for a index entry
class SearchEntry(object):
    def __init__(self, title, text, tags, loc):
        self.title = title
        self.text = text
        self.tags = tags
        self.loc = loc

#class for stripping html tags
class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

#class for parsing html-sections
class ContentParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)

        self.data = []
        self.section = ""
        self.is_header_tag = False

    #hook - tag start
    def handle_starttag(self, tag, attrs):
        if tag in ("h1","h2"):
            self.is_header_tag = True
            self.section = ContentSection()
            for attr in attrs:
                if attr[0] == "id":
                    self.section.id = attr[1]

    #hook - tag end
    def handle_endtag(self, tag):
        if tag in ("h1","h2"):
            self.is_header_tag = False
            self.data.append(self.section)

    #hook - data
    def handle_data(self, data):
        if self.is_header_tag:
            self.section.title = data
        else:
            self.section.text.append(data.rstrip('\n'))

#content-holder for html-sections
class ContentSection():
     def __init__(self):
        self.text = []
        self.id = ""
        self.title = ""
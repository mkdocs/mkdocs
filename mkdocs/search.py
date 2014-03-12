from pprint import pprint
from HTMLParser import HTMLParser
import json


class SearchIndex(object):
    def __init__(self):
        self.pages = []

        print 'create search index'



    def addEntryFromContext(self, page, content, nav, toc, meta, config):
        print "addEntryFromContext"
        #pprint (vars(page))
        #print page
        #for toc_item in toc:
        #    print toc_item.content
        entry = SearchEntry(
            title=page.title,
            text=self.strip_tags(content).encode('utf-8'),
            tags="",
            loc=page.abs_url
        )

        self.pages.append(entry)

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def generate_search_index(self):
        s = self.to_json()
        print s
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

        #print 'create search entry '+self.text


class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)




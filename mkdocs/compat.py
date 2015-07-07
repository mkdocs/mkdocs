import sys


PY3 = sys.version_info[0] == 3

if PY3:
    string_types = (str,)
    text_type = str
else:
    string_types = (basestring,)
    text_type = unicode

try:
    from html.parser import HTMLParser
except ImportError:
    from HTMLParser import HTMLParser

try:
    from urllib.parse import urlparse, urlunparse
except ImportError:
    from urlparse import urlparse, urlunparse

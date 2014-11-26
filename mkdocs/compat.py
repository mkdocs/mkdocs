# coding: utf-8
# flake8: noqa
"""Python 2/3 compatibility module."""

import sys

PY2 = sys.version_info < (3, )

if PY2:
    from HTMLParser import HTMLParser
    from urlparse import urljoin, urlparse, urlunparse
    import SimpleHTTPServer as httpserver
    import SocketServer as socketserver
    import urllib

    urlunquote = urllib.unquote

    from itertools import izip as zip
    unicode = unicode

else:  # PY3
    from html.parser import HTMLParser
    from urllib.parse import (urljoin, urlparse, urlunparse,
                              unquote as urlunquote)
    import http.server as httpserver
    import socketserver

    zip = zip

    unicode = str

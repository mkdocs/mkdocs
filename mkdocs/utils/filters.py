import json

import markupsafe

try:
    from jinja2 import pass_context as contextfilter
except ImportError:
    from jinja2 import contextfilter

from mkdocs.utils import normalize_url


def tojson(obj, **kwargs):
    return markupsafe.Markup(json.dumps(obj, **kwargs))


@contextfilter
def url_filter(context, value):
    """ A Template filter to normalize URLs. """
    return normalize_url(value, page=context['page'], base=context['base_url'])

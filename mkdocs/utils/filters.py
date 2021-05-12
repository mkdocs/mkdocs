import json

import jinja2
import markupsafe

from mkdocs.utils import normalize_url


def tojson(obj, **kwargs):
    return markupsafe.Markup(json.dumps(obj, **kwargs))


@jinja2.contextfilter
def url_filter(context, value):
    """ A Template filter to normalize URLs. """
    return normalize_url(value, page=context['page'], base=context['base_url'])

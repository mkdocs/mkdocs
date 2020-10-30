import json
import jinja2

from mkdocs.utils import normalize_url


def tojson(obj, **kwargs):
    return jinja2.Markup(json.dumps(obj, **kwargs))


@jinja2.contextfilter
def url_filter(context, value):
    """
    A Template filter to normalize URLs.

    value of a path to file ending with a dot "." is undefined behaviour.
    """

    url = normalize_url(value, page=context['page'], base=context['base_url'])
    return (
        url if context['config']['use_directory_urls']       else  # noqa: E272
        # given: using file urls
        url if not url[:1] == url[-1:] == '.'                else  # noqa: E272
        # when: url is relative to a directory missing a file
        # then: append /index.html to make it an url to the index file
        url + "/index.html"
    )

import jinja2

from mkdocs.utils import normalize_url


jinja2_version_info = tuple(
    int(n) for n in jinja2.__version__.split('.') if n.isdigit()
)

pass_context_decorator = jinja2.contextfilter if jinja2_version_info < (3,) else jinja2.pass_context

@pass_context_decorator
def url_filter(context, value):
    """ A Template filter to normalize URLs. """
    return normalize_url(value, page=context['page'], base=context['base_url'])

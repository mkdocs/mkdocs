import json
import jinja2


def tojson(obj, **kwargs):
    return jinja2.Markup(json.dumps(obj, **kwargs))

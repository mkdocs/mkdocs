from __future__ import unicode_literals
import textwrap
import markdown

from mkdocs import toc, config


def dedent(text):
    return textwrap.dedent(text).strip()


def markdown_to_toc(markdown_source):
    md = markdown.Markdown(extensions=['toc'])
    md.convert(markdown_source)
    toc_output = md.toc
    return toc.TableOfContents(toc_output)


def load_config(cfg=None):
    """ Helper to build a simple config for testing. """
    cfg = cfg or {}
    if 'site_name' not in cfg:
        cfg['site_name'] = 'Example'
    conf = config.Config(schema=config.DEFAULT_SCHEMA)
    conf.load_dict(cfg)

    errors_warnings = conf.validate()
    assert(errors_warnings == ([], [])), errors_warnings
    return conf

from __future__ import unicode_literals
import textwrap
import markdown
import os

from mkdocs import toc
from mkdocs import config


def dedent(text):
    return textwrap.dedent(text).strip()


def markdown_to_toc(markdown_source):
    md = markdown.Markdown(extensions=['toc'])
    md.convert(markdown_source)
    toc_output = md.toc
    return toc.TableOfContents(toc_output)


def load_config(**cfg):
    """ Helper to build a simple config for testing. """
    path_base = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), 'integration', 'minimal'
    )
    cfg = cfg or {}
    if 'site_name' not in cfg:
        cfg['site_name'] = 'Example'
    if 'config_file_path' not in cfg:
        cfg['config_file_path'] = os.path.join(path_base, 'mkdocs.yml')
    if 'docs_dir' not in cfg:
        # Point to an actual dir to avoid a 'does not exist' error on validation.
        cfg['docs_dir'] = os.path.join(path_base, 'docs')
    conf = config.Config(schema=config.DEFAULT_SCHEMA)
    conf.load_dict(cfg)

    errors_warnings = conf.validate()
    assert(errors_warnings == ([], [])), errors_warnings
    return conf

import logging
import os

from mkdocs import exceptions
from mkdocs import utils
from mkdocs.config import base, validators

DEFAULT_CONFIG = {

    # The title to use for the documentation
    'site_name': validators.Type(str, required=True),

    'pages': validators.Pages(),

    'site_url': validators.URL(),
    'site_description': validators.Type(str),
    'site_author': validators.Type(str),
    'site_favicon': validators.Type(str),

    'theme': validators.Theme(default='mkdocs'),
    'docs_dir': validators.Dir(default='docs', exists=True),
    'site_dir': validators.Dir(default='site'),
    'theme_dir': validators.ThemeDir(exists=True),

    'copyright': validators.Type(str),
    'google_analytics': validators.Type(list, length=2),

    # The address on which to serve the livereloading docs server.
    'dev_addr': validators.Type(str, default='127.0.0.1:8000'),

    # If `True`, use `<page_name>/index.hmtl` style files with hyperlinks to the directory.
    # If `False`, use `<page_name>.html style file with hyperlinks to the file.
    # True generates nicer URLs, but False is useful if browsing the output on a filesystem.
    'use_directory_urls': validators.Type(bool, default=True),

    # Specify a link to the project source repo to be included
    # in the documentation pages.
    'repo_url': validators.RepoURL(),

    # A name to use for the link to the project source repo.
    # Default: If repo_url is unset then None, otherwise
    # "GitHub" or "Bitbucket" for known url or Hostname for unknown urls.
    'repo_name': validators.Type(str),

    # Specify which css or javascript files from the docs
    # directionary should be additionally included in the site.
    # Default: List of all .css and .js files in the docs dir.
    'extra_css': validators.Extras(file_match=utils.is_css_file),
    'extra_javascript': validators.Extras(file_match=utils.is_javascript_file),
    'extra_templates': validators.Extras(file_match=utils.is_template_file),

    # Determine if the site should include the nav and next/prev elements.
    # Default: True if the site has more than one page, False otherwise.
    'include_nav': validators.NumPages(),
    'include_next_prev': validators.NumPages(),

    # PyMarkdown extension names.
    'markdown_extensions': validators.Type((list, dict)),

    # enabling strict mode causes MkDocs to stop the build when a problem is
    # encountered rather than display an error.
    'strict': validators.Type(bool, default=False)
}

log = logging.getLogger(__name__)


def load_config(config_file=None, **kwargs):

    for key, value in kwargs.items():
        if value is None:
            kwargs.pop(key)

    if config_file is None:
        config_file = 'mkdocs.yml'
        if os.path.exists(config_file):
            config_file = open(config_file, 'rb')
        else:
            raise exceptions.ConfigurationError(
                "Config file '{0}' does not exist.".format(config_file))

    config = base.Config(schema=DEFAULT_CONFIG)
    config.load_file(config_file)
    config.load_dict(kwargs)

    print config.keys()

    errors = config.validate()

    if len(errors) > 0:
        for error in errors:
            log.error(error)
        raise exceptions.ConfigurationError()

    print '---'
    for key, value in sorted(config.items()):
        print key, '\t\t', value
    print '---'

    return config

# coding: utf-8

import os
import yaml
import urlparse
from mkdocs import utils


DEFAULT_CONFIG = {
    'site_name': None,
    'pages': None,

    'site_url': None,
    'site_description': None,
    'site_author': None,
    'site_favicon': None,

    'theme': 'mkdocs',
    'docs_dir': 'docs',
    'site_dir': 'site',
    'theme_dir': None,

    'dev_addr': '127.0.0.1:8000',
    'use_direcory_urls': True,

    'repo_url': None,
    'repo_name': None,

    'extra_css': None,
    'extra_javascript': None,

    # These are not yet supported...
    'include_search': False,
    'include_404': False,
    'include_sitemap': False
}


def load_config(filename='mkdocs.yml', options=None):
    options = options or {}
    if 'config' in options:
        filename = options['config']
    assert os.path.exists(filename), "Config file '%s' does not exist." % filename

    user_config = yaml.load(open(filename, 'r'))
    user_config.update(options)
    return validate_config(user_config)


def validate_config(user_config):
    config = DEFAULT_CONFIG.copy()
    config.update(user_config)

    assert config['site_name'], "Config must contain 'site_name' setting."

    # If not specified, then the 'pages' config simply includes all
    # markdown files in the docs dir, without generating any header items
    # for them.
    pages = []
    extra_css = []
    extra_javascript = []
    for (dirpath, dirnames, filenames) in os.walk(config['docs_dir']):
        for filename in sorted(filenames):
            fullpath = os.path.join(dirpath, filename)
            relpath = os.path.relpath(fullpath, config['docs_dir'])

            if utils.is_markdown_file(filename):
                # index pages should always be the first listed page.
                if os.path.splitext(relpath)[0] == 'index':
                    pages.insert(0, relpath)
                else:
                    pages.append(relpath)
            elif utils.is_css_file(filename):
                extra_css.append(relpath)
            elif utils.is_javascript_file(filename):
                extra_javascript.append(relpath)

    if config['pages'] is None:
        config['pages'] = pages

    if config['extra_css'] is None:
        config['extra_css'] = extra_css

    if config['extra_javascript'] is None:
        config['extra_javascript'] = extra_javascript

    if config['theme_dir'] is None:
        package_dir = os.path.dirname(__file__)
        config['theme_dir'] = os.path.join(package_dir, 'themes', config['theme'])

    if config['repo_url'] is not None and config['repo_name'] is None:
        repo_host = urlparse.urlparse(config['repo_url']).netloc.lower()
        if repo_host == 'github.com':
            config['repo_name'] = 'GitHub'
        elif repo_host == 'bitbucket.com':
            config['repo_name'] = 'Bitbucket'
        else:
            config['repo_name'] = repo_host.split('.')[0].title()

    return config

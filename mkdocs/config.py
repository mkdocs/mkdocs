#coding: utf-8

import os
import yaml


DEFAULT_CONFIG = {
    'site_name': None,
    'pages': None,

    'site_url': None,
    'site_description': None,
    'site_author': None,
    'site_favicon': None,

    'theme': 'bootstrap',
    'docs_dir': 'docs',
    'site_dir': 'site',
    'theme_dir': None,

    'dev_addr': '127.0.0.1:8000',
    'use_direcory_urls': True
}


def load_config(filename='mkdocs.yml', options=None):
    options = options or {}
    assert os.path.exists(filename), "Config file '%s' does not exist." % filename

    user_config = yaml.load(open(filename, 'r'))
    config = DEFAULT_CONFIG.copy()
    config.update(user_config)
    config.update(options)

    assert config['site_name'], "Config must contain 'site_name' setting."
    assert config['pages'], "Config must contain 'pages' setting."

    if not config['theme_dir']:
        package_dir = os.path.dirname(__file__)
        config['theme_dir'] = os.path.join(package_dir, 'themes', config['theme'])

    return config

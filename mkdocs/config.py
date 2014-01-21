#coding: utf-8

import os
import yaml


DEFAULT_CONFIG = {
    'project_name': None,
    'pages': None,
    'base_url': '',

    'theme': 'bootstrap',

    'docs_dir': 'docs',
    'build_dir': 'build',
    'theme_dir': None,

    'dev_addr': '127.0.0.1:8000',
    'local_files': False
}


def load_config(filename='mkdocs.yaml', options=None):
    options = options or {}
    assert os.path.exists(filename), "Config file '%s' does not exist." % filename

    user_config = yaml.load(open(filename, 'r'))
    config = DEFAULT_CONFIG.copy()
    config.update(user_config)
    config.update(options)

    assert config['project_name'], "Config must contain 'project_name' setting."
    assert config['pages'], "Config must contain 'pages' setting."

    if not config['theme_dir']:
        package_dir = os.path.dirname(__file__)
        config['theme_dir'] = os.path.join(package_dir, 'themes', config['theme'])

    if config['local_files']:
        build_dir = os.path.join(os.getcwd(), config['build_dir'])
        build_path = build_dir.replace(os.path.pathsep, '/')
        config['base_url'] = 'file://%s' % build_path

    return config

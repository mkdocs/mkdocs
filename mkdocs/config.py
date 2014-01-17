#coding: utf-8

import os
import yaml


def load_config():
    config = {
        'theme': 'plain',
        'local_port': 8000,
        'local_host': '0.0.0.0'
    }
    user_config = yaml.load(open('mkdocs.yaml', 'r'))
    config.update(user_config)

    assert 'project_name' in config, "Config must contain 'project_name:'"
    assert 'pages' in config, "Config must contain 'pages:'"

    if 'theme_dir' not in config:
        package_dir = os.path.dirname(__file__)
        config['theme_dir'] = os.path.join(package_dir, 'themes', config['theme'])

    # For preview builds only...
    # TODO: Remove this.
    config['base_url'] = ''
    config['suffix'] = '.html'
    return config

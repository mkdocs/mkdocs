#!/usr/bin/env python

import os
import tempfile
import unittest
from tempfile import TemporaryDirectory

import mkdocs
from mkdocs import config
from mkdocs.config import config_options
from mkdocs.exceptions import ConfigurationError
from mkdocs.tests.base import dedent


class ConfigTests(unittest.TestCase):
    def test_missing_config_file(self):

        def load_missing_config():
            config.load_config(config_file='bad_filename.yaml')
        self.assertRaises(ConfigurationError, load_missing_config)

    def test_missing_site_name(self):
        c = config.Config(schema=config.DEFAULT_SCHEMA)
        c.load_dict({})
        errors, warnings = c.validate()
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0][0], 'site_name')
        self.assertEqual(str(errors[0][1]), 'Required configuration not provided.')

        self.assertEqual(len(warnings), 0)

    def test_empty_config(self):
        def load_empty_config():
            config.load_config(config_file='/dev/null')
        self.assertRaises(ConfigurationError, load_empty_config)

    def test_nonexistant_config(self):
        def load_empty_config():
            config.load_config(config_file='/path/that/is/not/real')
        self.assertRaises(ConfigurationError, load_empty_config)

    def test_invalid_config(self):
        file_contents = dedent("""
        - ['index.md', 'Introduction']
        - ['index.md', 'Introduction']
        - ['index.md', 'Introduction']
        """)
        config_file = tempfile.NamedTemporaryFile('w', delete=False)
        try:
            config_file.write(file_contents)
            config_file.flush()
            config_file.close()

            self.assertRaises(
                ConfigurationError,
                config.load_config, config_file=open(config_file.name, 'rb')
            )
        finally:
            os.remove(config_file.name)

    def test_config_option(self):
        """
        Users can explicitly set the config file using the '--config' option.
        Allows users to specify a config other than the default `mkdocs.yml`.
        """
        expected_result = {
            'site_name': 'Example',
            'pages': [
                {'Introduction': 'index.md'}
            ],
        }
        file_contents = dedent("""
        site_name: Example
        pages:
        - 'Introduction': 'index.md'
        """)
        with TemporaryDirectory() as temp_path:
            os.mkdir(os.path.join(temp_path, 'docs'))
            config_path = os.path.join(temp_path, 'mkdocs.yml')
            config_file = open(config_path, 'w')

            config_file.write(file_contents)
            config_file.flush()
            config_file.close()

            result = config.load_config(config_file=config_file.name)
            self.assertEqual(result['site_name'], expected_result['site_name'])
            self.assertEqual(result['pages'], expected_result['pages'])

    def test_theme(self):
        with TemporaryDirectory() as mytheme, TemporaryDirectory() as custom:
            configs = [
                dict(),  # default theme
                {"theme": "readthedocs"},  # builtin theme
                {"theme": {'name': 'readthedocs'}},  # builtin as complex
                {"theme": {'name': None, 'custom_dir': mytheme}},  # custom only as complex
                {"theme": {'name': 'readthedocs', 'custom_dir': custom}},  # builtin and custom as complex
                {  # user defined variables
                    'theme': {
                        'name': 'mkdocs',
                        'static_templates': ['foo.html'],
                        'show_sidebar': False,
                        'some_var': 'bar'
                    }
                }
            ]

            mkdocs_dir = os.path.abspath(os.path.dirname(mkdocs.__file__))
            mkdocs_templates_dir = os.path.join(mkdocs_dir, 'templates')
            theme_dir = os.path.abspath(os.path.join(mkdocs_dir, 'themes'))

            results = (
                {
                    'dirs': [os.path.join(theme_dir, 'mkdocs'), mkdocs_templates_dir],
                    'static_templates': ['404.html', 'sitemap.xml'],
                    'vars': {
                        'include_search_page': False,
                        'search_index_only': False,
                        'highlightjs': True,
                        'hljs_style': 'github',
                        'hljs_languages': [],
                        'navigation_depth': 2,
                        'nav_style': 'primary',
                        'shortcuts': {'help': 191, 'next': 78, 'previous': 80, 'search': 83}
                    }
                }, {
                    'dirs': [os.path.join(theme_dir, 'readthedocs'), mkdocs_templates_dir],
                    'static_templates': ['404.html', 'sitemap.xml'],
                    'vars': {
                        'include_search_page': True,
                        'search_index_only': False,
                        'highlightjs': True,
                        'hljs_languages': [],
                        'include_homepage_in_sidebar': True,
                        'prev_next_buttons_location': 'bottom',
                        'navigation_depth': 4,
                        'sticky_navigation': True,
                        'titles_only': False,
                        'collapse_navigation': True
                    }
                }, {
                    'dirs': [os.path.join(theme_dir, 'readthedocs'), mkdocs_templates_dir],
                    'static_templates': ['404.html', 'sitemap.xml'],
                    'vars': {
                        'include_search_page': True,
                        'search_index_only': False,
                        'highlightjs': True,
                        'hljs_languages': [],
                        'include_homepage_in_sidebar': True,
                        'prev_next_buttons_location': 'bottom',
                        'navigation_depth': 4,
                        'sticky_navigation': True,
                        'titles_only': False,
                        'collapse_navigation': True
                    }
                }, {
                    'dirs': [mytheme, mkdocs_templates_dir],
                    'static_templates': ['sitemap.xml'],
                    'vars': {}
                }, {
                    'dirs': [custom, os.path.join(theme_dir, 'readthedocs'), mkdocs_templates_dir],
                    'static_templates': ['404.html', 'sitemap.xml'],
                    'vars': {
                        'include_search_page': True,
                        'search_index_only': False,
                        'highlightjs': True,
                        'hljs_languages': [],
                        'include_homepage_in_sidebar': True,
                        'prev_next_buttons_location': 'bottom',
                        'navigation_depth': 4,
                        'sticky_navigation': True,
                        'titles_only': False,
                        'collapse_navigation': True
                    }
                }, {
                    'dirs': [os.path.join(theme_dir, 'mkdocs'), mkdocs_templates_dir],
                    'static_templates': ['404.html', 'sitemap.xml', 'foo.html'],
                    'vars': {
                        'show_sidebar': False,
                        'some_var': 'bar',
                        'include_search_page': False,
                        'search_index_only': False,
                        'highlightjs': True,
                        'hljs_style': 'github',
                        'hljs_languages': [],
                        'navigation_depth': 2,
                        'nav_style': 'primary',
                        'shortcuts': {'help': 191, 'next': 78, 'previous': 80, 'search': 83}
                    }
                }
            )

            for config_contents, result in zip(configs, results):

                c = config.Config(schema=(('theme', config_options.Theme(default='mkdocs')),))
                c.load_dict(config_contents)
                errors, warnings = c.validate()
                self.assertEqual(len(errors), 0)
                self.assertEqual(c['theme'].dirs, result['dirs'])
                self.assertEqual(c['theme'].static_templates, set(result['static_templates']))
                self.assertEqual({k: c['theme'][k] for k in iter(c['theme'])}, result['vars'])

    def test_empty_nav(self):
        conf = config.Config(schema=config.DEFAULT_SCHEMA)
        conf.load_dict({
            'site_name': 'Example',
            'config_file_path': os.path.join(os.path.abspath('.'), 'mkdocs.yml')
        })
        conf.validate()
        self.assertEqual(conf['nav'], None)

    def test_copy_pages_to_nav(self):
        # TODO: remove this when pages config setting is fully deprecated.
        conf = config.Config(schema=config.DEFAULT_SCHEMA)
        conf.load_dict({
            'site_name': 'Example',
            'pages': ['index.md', 'about.md'],
            'config_file_path': os.path.join(os.path.abspath('.'), 'mkdocs.yml')
        })
        conf.validate()
        self.assertEqual(conf['nav'], ['index.md', 'about.md'])

    def test_dont_overwrite_nav_with_pages(self):
        # TODO: remove this when pages config setting is fully deprecated.
        conf = config.Config(schema=config.DEFAULT_SCHEMA)
        conf.load_dict({
            'site_name': 'Example',
            'pages': ['index.md', 'about.md'],
            'nav': ['foo.md', 'bar.md'],
            'config_file_path': os.path.join(os.path.abspath('.'), 'mkdocs.yml')
        })
        conf.validate()
        self.assertEqual(conf['nav'], ['foo.md', 'bar.md'])

    def test_doc_dir_in_site_dir(self):

        j = os.path.join

        test_configs = (
            {'docs_dir': j('site', 'docs'), 'site_dir': 'site'},
            {'docs_dir': 'docs', 'site_dir': '.'},
            {'docs_dir': '.', 'site_dir': '.'},
            {'docs_dir': 'docs', 'site_dir': ''},
            {'docs_dir': '', 'site_dir': ''},
            {'docs_dir': 'docs', 'site_dir': 'docs'},
        )

        conf = {
            'config_file_path': j(os.path.abspath('..'), 'mkdocs.yml')
        }

        for test_config in test_configs:

            patch = conf.copy()
            patch.update(test_config)

            # Same as the default schema, but don't verify the docs_dir exists.
            c = config.Config(schema=(
                ('docs_dir', config_options.Dir(default='docs')),
                ('site_dir', config_options.SiteDir(default='site')),
                ('config_file_path', config_options.Type(str))
            ))
            c.load_dict(patch)

            errors, warnings = c.validate()

            self.assertEqual(len(errors), 1)
            self.assertEqual(warnings, [])

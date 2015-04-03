#!/usr/bin/env python
# coding: utf-8

import filecmp
import os
import shutil
import tempfile
import unittest
import zipfile

import mock

from mkdocs import config
from mkdocs.compat import PY2, zip
from mkdocs.exceptions import ConfigurationError
from mkdocs.tests.base import dedent


def ensure_utf(string):
    return string.encode('utf-8') if PY2 else string


def _create_mock_theme_zip(theme_dir, theme):
    theme_path = os.path.join(theme_dir, theme)

    tmp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(tmp_dir, 'yeti.zip')
    zip_file = zipfile.ZipFile(zip_path, 'w')

    for root, dirs, files in os.walk(theme_path):
        for f in files:
            arcname = "{0}/{1}".format(root.replace(theme_path, ''), f)
            zip_file.write(os.path.join(root, f), arcname=arcname)
    zip_file.close()
    return open(zip_path, 'rb')


class ConfigTests(unittest.TestCase):

    def setUp(self):
        super(ConfigTests, self).setUp()

        self.themes_dir = os.path.join(os.path.dirname(__file__), '../themes/')

    def test_missing_config_file(self):

        def load_missing_config():
            options = {'config': 'bad_filename.yaml'}
            config.load_config(options=options)
        self.assertRaises(ConfigurationError, load_missing_config)

    def test_missing_site_name(self):
        def load_missing_site_name():
            config.validate_config({})
        self.assertRaises(ConfigurationError, load_missing_site_name)

    def test_empty_config(self):
        def load_empty_config():
            config.load_config(filename='/dev/null')
        self.assertRaises(ConfigurationError, load_empty_config)

    def test_config_option(self):
        """
        Users can explicitly set the config file using the '--config' option.
        Allows users to specify a config other than the default `mkdocs.yml`.
        """
        expected_result = {
            'site_name': 'Example',
            'pages': [
                ['index.md', 'Introduction']
            ],
        }
        file_contents = dedent("""
        site_name: Example
        pages:
        - ['index.md', 'Introduction']
        """)
        config_file = tempfile.NamedTemporaryFile('w', delete=False)
        try:
            config_file.write(ensure_utf(file_contents))
            config_file.flush()
            options = {'config': config_file.name}
            result = config.load_config(options=options)
            self.assertEqual(result['site_name'], expected_result['site_name'])
            self.assertEqual(result['pages'], expected_result['pages'])
            config_file.close()
        finally:
            os.remove(config_file.name)

    def test_theme(self):

        base_config = dedent("""
        site_name: Example
        pages:
        - ['index.md', 'Introduction']
        %s
        """)

        configs = [
            "site_name: Example",  # default theme
            "theme: readthedocs",  # builtin theme
            "theme_dir: mytheme",  # custom only
            "theme: cosmo\ntheme_dir: custom"  # builtin and custom
        ]

        abs_path = os.path.abspath(os.path.dirname(__file__))
        theme_dir = os.path.abspath(os.path.join(abs_path, '..', 'themes'))

        results = (
            [os.path.join(theme_dir, 'mkdocs'), ],
            [os.path.join(theme_dir, 'readthedocs'), ],
            ['mytheme', ],
            ['custom', os.path.join(theme_dir, 'cosmo'), ],
        )

        for config_contents, expected_result in zip(configs, results):
            try:
                config_file = tempfile.NamedTemporaryFile('w', delete=False)
                config_file.write(ensure_utf(base_config % config_contents))
                config_file.flush()
                options = {'config': config_file.name}
                result = config.load_config(options=options)
                self.assertEqual(result['theme_dir'], expected_result)
            finally:
                try:
                    config_file.close()
                    os.remove(config_file.name)
                except:
                    # This failed on Windows for some reason?
                    pass

    @mock.patch('mkdocs.utils.urlopen')
    def test_install_theme(self, mock_urlopen):

        theme_path = os.path.join(self.themes_dir, 'yeti')
        tmp_dir = tempfile.mkdtemp()
        zip_file = _create_mock_theme_zip(self.themes_dir, "yeti")
        mock_urlopen.return_value = zip_file

        config.install_theme('https://fake-url.com', tmp_dir)
        self.assertTrue(os.path.exists, os.path.join(tmp_dir, 'yeti'))
        c = filecmp.dircmp(os.path.join(tmp_dir, 'yeti'), theme_path)
        self.assertEqual(c.left_only, [])
        self.assertEqual(c.right_only, [])

    def test_default_pages(self):
        tmp_dir = tempfile.mkdtemp()
        try:
            open(os.path.join(tmp_dir, 'index.md'), 'w').close()
            open(os.path.join(tmp_dir, 'about.md'), 'w').close()
            conf = config.validate_config({
                'site_name': 'Example',
                'docs_dir': tmp_dir
            })
            self.assertEqual(conf['pages'], ['index.md', 'about.md'])
        finally:
            shutil.rmtree(tmp_dir)

    def test_doc_dir_in_site_dir(self):

        j = os.path.join

        test_configs = (
            {'docs_dir': 'docs', 'site_dir': j('docs', 'site')},
            {'docs_dir': j('site', 'docs'), 'site_dir': 'site'},
            {'docs_dir': 'docs', 'site_dir': '.'},
            {'docs_dir': '.', 'site_dir': 'site'},
            {'docs_dir': '.', 'site_dir': '.'},
            {'docs_dir': 'docs', 'site_dir': ''},
            {'docs_dir': '', 'site_dir': 'site'},
            {'docs_dir': '', 'site_dir': ''},
            {'docs_dir': j('..', 'mkdocs', 'docs'), 'site_dir': 'docs'},
        )

        conf = {
            'site_name': 'Example',
        }

        for test_config in test_configs:

            c = conf.copy()
            c.update(test_config)
            self.assertRaises(ConfigurationError, config.validate_config, c)

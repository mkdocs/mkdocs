#!/usr/bin/env python
# coding: utf-8

import unittest

from mkdocs import nav, utils


class UtilsTests(unittest.TestCase):
    def test_html_path(self):
        expected_results = {
            'index.md': 'index.html',
            'api-guide.md': 'api-guide/index.html',
            'api-guide/index.md': 'api-guide/index.html',
            'api-guide/testing.md': 'api-guide/testing/index.html',
        }
        for file_path, expected_html_path in expected_results.items():
            html_path = utils.get_html_path(file_path)
            self.assertEqual(html_path, expected_html_path)

    def test_url_path(self):
        expected_results = {
            'index.md': '/',
            'api-guide.md': '/api-guide/',
            'api-guide/index.md': '/api-guide/',
            'api-guide/testing.md': '/api-guide/testing/',
        }
        for file_path, expected_html_path in expected_results.items():
            html_path = utils.get_url_path(file_path)
            self.assertEqual(html_path, expected_html_path)

    def test_is_markdown_file(self):
        expected_results = {
            'index.md': True,
            'index.MARKDOWN': True,
            'index.txt': False,
            'indexmd': False
        }
        for path, expected_result in expected_results.items():
            is_markdown = utils.is_markdown_file(path)
            self.assertEqual(is_markdown, expected_result)

    def test_is_html_file(self):
        expected_results = {
            'index.htm': True,
            'index.HTML': True,
            'index.txt': False,
            'indexhtml': False
        }
        for path, expected_result in expected_results.items():
            is_html = utils.is_html_file(path)
            self.assertEqual(is_html, expected_result)

    def test_create_media_urls(self):
        pages = [
            ('index.md', 'Home'),
            ('about.md', 'About')
        ]
        expected_results = {
            'https://media.cdn.org/jquery.js': 'https://media.cdn.org/jquery.js',
            'http://media.cdn.org/jquery.js': 'http://media.cdn.org/jquery.js',
            '//media.cdn.org/jquery.js': '//media.cdn.org/jquery.js',
            'media.cdn.org/jquery.js': './media.cdn.org/jquery.js',
            'local/file/jquery.js': './local/file/jquery.js',
        }
        site_navigation = nav.SiteNavigation(pages)
        for path, expected_result in expected_results.items():
            urls = utils.create_media_urls(site_navigation, [path])
            self.assertEqual(urls[0], expected_result)

    def test_yaml_load(self):
        try:
            from collections import OrderedDict
        except ImportError:
            # Don't test if can't import OrderdDict
            # Exception can be removed when Py26 support is removed
            return

        yaml_text = '''
test:
    key1: 1
    key2: 2
    key3: 3
    key4: 4
    key5: 5
    key5: 6
    key3: 7
'''
        self.assertEqual(
            utils.yaml_load(yaml_text),
            OrderedDict([('test', OrderedDict([('key1', 1), ('key2', 2), ('key3', 7),
                                               ('key4', 4), ('key5', 6)]))])
        )

    def test_reduce_list(self):
        self.assertEqual(
            utils.reduce_list([1, 2, 3, 4, 5, 5, 2, 4, 6, 7, 8]),
            [1, 2, 3, 4, 5, 6, 7, 8]
        )

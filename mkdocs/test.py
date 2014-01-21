#!/usr/bin/env python
# coding: utf-8

from mkdocs import utils
import unittest


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


if __name__ == '__main__':
    unittest.main()
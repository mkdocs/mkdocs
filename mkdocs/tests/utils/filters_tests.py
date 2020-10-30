#!/usr/bin/env python


import unittest

from mkdocs.utils import filters


class UtilsTests(unittest.TestCase):
    def test_url_filter_empty_base_url(self):
        """ test concatenation has very little normalization effects (empty base_url) """
        context = {"page": None, "base_url": "", "config": {"use_directory_urls": False}}

        # key is value
        expected_results = {
            '': './index.html',
            '.': './index.html',
            './': './',
            './.': '././index.html',
            '..': '../index.html',
            '../.': '.././index.html',
            '../..': '../../index.html',
            './..': './../index.html',
            '/..': '/..',
            'api-guide': 'api-guide',
            'api-guide/': 'api-guide/',
            'api-guide/.': 'api-guide/.',
            'api-guide/..': 'api-guide/..',
            'api-guide/index.html': 'api-guide/index.html',
            'api-guide/testing.html': 'api-guide/testing.html',
        }

        for value, expected_url in expected_results.items():
            actual_url = filters.url_filter(context, value)
            self.assertEqual(expected_url, actual_url, "value: '{}'".format(value))

    def test_url_filter_empty_base_url_use_directory_urls(self):
        """ test concatenation has very little normalization effects (empty base_url with directory urls) """
        context = {"page": None, "base_url": "", "config": {"use_directory_urls": True}}
        # key is value
        expected_results = {
            '': '.',                # the only url normalization is empty to single dot "" -> "."
            '.': '.',
            './': './',
            './.': './.',
            '..': '..',
            '../.': '../.',
            '../..': '../..',
            './..': './..',
            '/..': '/..',
            'api-guide': 'api-guide',
            'api-guide/': 'api-guide/',
            'api-guide/.': 'api-guide/.',
            'api-guide/..': 'api-guide/..',
            'api-guide/index.html': 'api-guide/index.html',
            'api-guide/testing.html': 'api-guide/testing.html',
        }
        for value, expected_url in expected_results.items():
            actual_url = filters.url_filter(context, value)
            self.assertEqual(expected_url, actual_url, "value: '{}'".format(value))

    def test_url_filter_empty_but_base_url(self):
        """ test concatenation has very little normalization effects (empty value) """
        context = {"page": None, "base_url": "", "config": {"use_directory_urls": False}}

        value = ""

        # key is base_url
        expected_results = {
            '':       './index.html',
            'major':  'major/.',     # url normalization append slash to non-empty base, empty to single dot "" -> "."
            'major/': 'major/.',     # always adding the dot (compare with empty base_url)
            '.': '././index.html',
            './': '././index.html',
            '/': '/.',
            '..': '.././index.html',
            '../.': '../././index.html',
            '../..': '../.././index.html',
            './..': './.././index.html',
            '/..': '/../.',
            'api-guide/.': 'api-guide/./.',
            'api-guide/..': 'api-guide/../.',
            'api-guide/index.html': 'api-guide/index.html/.',
            'api-guide/testing.html': 'api-guide/testing.html/.',
            'https://www.mkdocs.org/': "https://www.mkdocs.org/.",
            'https://www.mkdocs.org/.': "https://www.mkdocs.org/./.",
            'https://www.mkdocs.org/../.': "https://www.mkdocs.org/.././.",
            'https://www.mkdocs.org/../..': "https://www.mkdocs.org/../../.",
            'https://www.mkdocs.org/../': "https://www.mkdocs.org/../.",
            'https://www.mkdocs.org/index.html': "https://www.mkdocs.org/index.html/.",
            'https://www.mkdocs.org/testing.html': "https://www.mkdocs.org/testing.html/.",
        }

        for context["base_url"], expected_url in expected_results.items():
            actual_url = filters.url_filter(context, value)
            self.assertEqual(expected_url, actual_url, "base_url: '{}'".format(context["base_url"]))

    def test_url_filter_empty_but_base_url_use_directory_urls(self):
        """ test concatenation has very little normalization effects (empty value with directory urls) """
        context = {"page": None, "base_url": "", "config": {"use_directory_urls": True}}

        value = ""

        # key is base_url
        expected_results = {
            '':       '.',           # url normalization empty to single dot "" -> "."
            'major':  'major/.',     # url normalization append slash to non-empty base, empty to single dot "" -> "."
            'major/': 'major/.',     # always adding the dot (compare with empty base_url)
            '.': './.',
            './': './.',
            '/': '/.',
            '..': '../.',
            '../.': '.././.',
            '../..': '../../.',
            './..': './../.',
            '/..': '/../.',
            'api-guide/.': 'api-guide/./.',
            'api-guide/..': 'api-guide/../.',
            'api-guide/index.html': 'api-guide/index.html/.',
            'api-guide/testing.html': 'api-guide/testing.html/.',
            'https://www.mkdocs.org/': "https://www.mkdocs.org/.",
            'https://www.mkdocs.org/.': "https://www.mkdocs.org/./.",
            'https://www.mkdocs.org/../.': "https://www.mkdocs.org/.././.",
            'https://www.mkdocs.org/../..': "https://www.mkdocs.org/../../.",
            'https://www.mkdocs.org/../': "https://www.mkdocs.org/../.",
        }

        for context["base_url"], expected_url in expected_results.items():
            actual_url = filters.url_filter(context, value)
            self.assertEqual(expected_url, actual_url, "base_url: '{}'".format(context["base_url"]))

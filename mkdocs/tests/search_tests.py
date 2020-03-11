#!/usr/bin/env python

import unittest
from unittest import mock
import json

from mkdocs.structure.files import File
from mkdocs.structure.pages import Page
from mkdocs.structure.toc import get_toc
from mkdocs.contrib import search
from mkdocs.contrib.search import search_index
from mkdocs.config.config_options import ValidationError
from mkdocs.tests.base import dedent, get_markdown_toc, load_config


def strip_whitespace(string):
    return string.replace("\n", "").replace(" ", "")


class SearchConfigTests(unittest.TestCase):

    def test_lang_default(self):
        option = search.LangOption(default=['en'])
        value = option.validate(None)
        self.assertEqual(['en'], value)

    def test_lang_str(self):
        option = search.LangOption()
        value = option.validate('en')
        self.assertEqual(['en'], value)

    def test_lang_list(self):
        option = search.LangOption()
        value = option.validate(['en'])
        self.assertEqual(['en'], value)

    def test_lang_multi_list(self):
        option = search.LangOption()
        value = option.validate(['en', 'es', 'fr'])
        self.assertEqual(['en', 'es', 'fr'], value)

    def test_lang_bad_type(self):
        option = search.LangOption()
        self.assertRaises(ValidationError, option.validate, {})

    def test_lang_bad_code(self):
        option = search.LangOption()
        self.assertRaises(ValidationError, option.validate, ['foo'])

    def test_lang_good_and_bad_code(self):
        option = search.LangOption()
        self.assertRaises(ValidationError, option.validate, ['en', 'foo'])


class SearchPluginTests(unittest.TestCase):

    def test_plugin_config_defaults(self):
        expected = {
            'lang': ['en'],
            'separator': r'[\s\-]+',
            'min_search_length': 3,
            'prebuild_index': False
        }
        plugin = search.SearchPlugin()
        errors, warnings = plugin.load_config({})
        self.assertEqual(plugin.config, expected)
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])

    def test_plugin_config_lang(self):
        expected = {
            'lang': ['es'],
            'separator': r'[\s\-]+',
            'min_search_length': 3,
            'prebuild_index': False
        }
        plugin = search.SearchPlugin()
        errors, warnings = plugin.load_config({'lang': 'es'})
        self.assertEqual(plugin.config, expected)
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])

    def test_plugin_config_separator(self):
        expected = {
            'lang': ['en'],
            'separator': r'[\s\-\.]+',
            'min_search_length': 3,
            'prebuild_index': False
        }
        plugin = search.SearchPlugin()
        errors, warnings = plugin.load_config({'separator': r'[\s\-\.]+'})
        self.assertEqual(plugin.config, expected)
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])

    def test_plugin_config_min_search_length(self):
        expected = {
            'lang': ['en'],
            'separator': r'[\s\-]+',
            'min_search_length': 2,
            'prebuild_index': False
        }
        plugin = search.SearchPlugin()
        errors, warnings = plugin.load_config({'min_search_length': 2})
        self.assertEqual(plugin.config, expected)
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])

    def test_plugin_config_prebuild_index(self):
        expected = {
            'lang': ['en'],
            'separator': r'[\s\-]+',
            'min_search_length': 3,
            'prebuild_index': True
        }
        plugin = search.SearchPlugin()
        errors, warnings = plugin.load_config({'prebuild_index': True})
        self.assertEqual(plugin.config, expected)
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])

    def test_event_on_config_defaults(self):
        plugin = search.SearchPlugin()
        plugin.load_config({})
        result = plugin.on_config(load_config(theme='mkdocs', extra_javascript=[]))
        self.assertFalse(result['theme']['search_index_only'])
        self.assertFalse(result['theme']['include_search_page'])
        self.assertEqual(result['theme'].static_templates, {'404.html', 'sitemap.xml'})
        self.assertEqual(len(result['theme'].dirs), 3)
        self.assertEqual(result['extra_javascript'], ['search/main.js'])

    def test_event_on_config_include_search_page(self):
        plugin = search.SearchPlugin()
        plugin.load_config({})
        config = load_config(theme={'name': 'mkdocs', 'include_search_page': True}, extra_javascript=[])
        result = plugin.on_config(config)
        self.assertFalse(result['theme']['search_index_only'])
        self.assertTrue(result['theme']['include_search_page'])
        self.assertEqual(result['theme'].static_templates, {'404.html', 'sitemap.xml', 'search.html'})
        self.assertEqual(len(result['theme'].dirs), 3)
        self.assertEqual(result['extra_javascript'], ['search/main.js'])

    def test_event_on_config_search_index_only(self):
        plugin = search.SearchPlugin()
        plugin.load_config({})
        config = load_config(theme={'name': 'mkdocs', 'search_index_only': True}, extra_javascript=[])
        result = plugin.on_config(config)
        self.assertTrue(result['theme']['search_index_only'])
        self.assertFalse(result['theme']['include_search_page'])
        self.assertEqual(result['theme'].static_templates, {'404.html', 'sitemap.xml'})
        self.assertEqual(len(result['theme'].dirs), 2)
        self.assertEqual(len(result['extra_javascript']), 0)

    @mock.patch('mkdocs.utils.write_file', autospec=True)
    @mock.patch('mkdocs.utils.copy_file', autospec=True)
    def test_event_on_post_build_defaults(self, mock_copy_file, mock_write_file):
        plugin = search.SearchPlugin()
        plugin.load_config({})
        config = load_config(theme='mkdocs')
        plugin.on_pre_build(config)
        plugin.on_post_build(config)
        self.assertEqual(mock_copy_file.call_count, 0)
        self.assertEqual(mock_write_file.call_count, 1)

    @mock.patch('mkdocs.utils.write_file', autospec=True)
    @mock.patch('mkdocs.utils.copy_file', autospec=True)
    def test_event_on_post_build_single_lang(self, mock_copy_file, mock_write_file):
        plugin = search.SearchPlugin()
        plugin.load_config({'lang': ['es']})
        config = load_config(theme='mkdocs')
        plugin.on_pre_build(config)
        plugin.on_post_build(config)
        self.assertEqual(mock_copy_file.call_count, 2)
        self.assertEqual(mock_write_file.call_count, 1)

    @mock.patch('mkdocs.utils.write_file', autospec=True)
    @mock.patch('mkdocs.utils.copy_file', autospec=True)
    def test_event_on_post_build_multi_lang(self, mock_copy_file, mock_write_file):
        plugin = search.SearchPlugin()
        plugin.load_config({'lang': ['es', 'fr']})
        config = load_config(theme='mkdocs')
        plugin.on_pre_build(config)
        plugin.on_post_build(config)
        self.assertEqual(mock_copy_file.call_count, 4)
        self.assertEqual(mock_write_file.call_count, 1)

    @mock.patch('mkdocs.utils.write_file', autospec=True)
    @mock.patch('mkdocs.utils.copy_file', autospec=True)
    def test_event_on_post_build_search_index_only(self, mock_copy_file, mock_write_file):
        plugin = search.SearchPlugin()
        plugin.load_config({'lang': ['es']})
        config = load_config(theme={'name': 'mkdocs', 'search_index_only': True})
        plugin.on_pre_build(config)
        plugin.on_post_build(config)
        self.assertEqual(mock_copy_file.call_count, 0)
        self.assertEqual(mock_write_file.call_count, 1)


class SearchIndexTests(unittest.TestCase):

    def test_html_stripper(self):

        stripper = search_index.HTMLStripper()

        stripper.feed("<h1>Testing</h1><p>Content</p>")

        self.assertEqual(stripper.data, ["Testing", "Content"])

    def test_content_parser(self):

        parser = search_index.ContentParser()

        parser.feed('<h1 id="title">Title</h1>TEST')
        parser.close()

        self.assertEqual(parser.data, [search_index.ContentSection(
            text=["TEST"],
            id_="title",
            title="Title"
        )])

    def test_content_parser_no_id(self):

        parser = search_index.ContentParser()

        parser.feed("<h1>Title</h1>TEST")
        parser.close()

        self.assertEqual(parser.data, [search_index.ContentSection(
            text=["TEST"],
            id_=None,
            title="Title"
        )])

    def test_content_parser_content_before_header(self):

        parser = search_index.ContentParser()

        parser.feed("Content Before H1 <h1>Title</h1>TEST")
        parser.close()

        self.assertEqual(parser.data, [search_index.ContentSection(
            text=["TEST"],
            id_=None,
            title="Title"
        )])

    def test_content_parser_no_sections(self):

        parser = search_index.ContentParser()

        parser.feed("No H1 or H2<span>Title</span>TEST")

        self.assertEqual(parser.data, [])

    def test_find_toc_by_id(self):
        """
        Test finding the relevant TOC item by the tag ID.
        """

        index = search_index.SearchIndex()

        md = dedent("""
        # Heading 1
        ## Heading 2
        ### Heading 3
        """)
        toc = get_toc(get_markdown_toc(md))

        toc_item = index._find_toc_by_id(toc, "heading-1")
        self.assertEqual(toc_item.url, "#heading-1")
        self.assertEqual(toc_item.title, "Heading 1")

        toc_item2 = index._find_toc_by_id(toc, "heading-2")
        self.assertEqual(toc_item2.url, "#heading-2")
        self.assertEqual(toc_item2.title, "Heading 2")

        toc_item3 = index._find_toc_by_id(toc, "heading-3")
        self.assertEqual(toc_item3.url, "#heading-3")
        self.assertEqual(toc_item3.title, "Heading 3")

    def test_create_search_index(self):

        html_content = """
        <h1 id="heading-1">Heading 1</h1>
        <p>Content 1</p>
        <h2 id="heading-2">Heading 2</h1>
        <p>Content 2</p>
        <h3 id="heading-3">Heading 3</h1>
        <p>Content 3</p>
        """

        cfg = load_config()
        pages = [
            Page('Home', File('index.md',  cfg['docs_dir'], cfg['site_dir'], cfg['use_directory_urls']), cfg),
            Page('About', File('about.md',  cfg['docs_dir'], cfg['site_dir'], cfg['use_directory_urls']), cfg)
        ]

        md = dedent("""
        # Heading 1
        ## Heading 2
        ### Heading 3
        """)
        toc = get_toc(get_markdown_toc(md))

        full_content = ''.join("""Heading{0}Content{0}""".format(i) for i in range(1, 4))

        for page in pages:
            # Fake page.read_source() and page.render()
            page.markdown = md
            page.toc = toc
            page.content = html_content

            index = search_index.SearchIndex()
            index.add_entry_from_context(page)

            self.assertEqual(len(index._entries), 4)

            loc = page.url

            self.assertEqual(index._entries[0]['title'], page.title)
            self.assertEqual(strip_whitespace(index._entries[0]['text']), full_content)
            self.assertEqual(index._entries[0]['location'], loc)

            self.assertEqual(index._entries[1]['title'], "Heading 1")
            self.assertEqual(index._entries[1]['text'], "Content 1")
            self.assertEqual(index._entries[1]['location'], "{}#heading-1".format(loc))

            self.assertEqual(index._entries[2]['title'], "Heading 2")
            self.assertEqual(strip_whitespace(index._entries[2]['text']), "Content2")
            self.assertEqual(index._entries[2]['location'], "{}#heading-2".format(loc))

            self.assertEqual(index._entries[3]['title'], "Heading 3")
            self.assertEqual(strip_whitespace(index._entries[3]['text']), "Content3")
            self.assertEqual(index._entries[3]['location'], "{}#heading-3".format(loc))

    @mock.patch('subprocess.Popen', autospec=True)
    def test_prebuild_index(self, mock_popen):
        # See https://stackoverflow.com/a/36501078/866026
        mock_popen.return_value = mock.Mock()
        mock_popen_obj = mock_popen.return_value
        mock_popen_obj.communicate.return_value = ('{"mock": "index"}', None)
        mock_popen_obj.returncode = 0

        index = search_index.SearchIndex(prebuild_index=True)
        expected = {
            'docs': [],
            'config': {'prebuild_index': True},
            'index': {'mock': 'index'}
        }
        result = json.loads(index.generate_search_index())
        self.assertEqual(mock_popen.call_count, 1)
        self.assertEqual(mock_popen_obj.communicate.call_count, 1)
        self.assertEqual(result, expected)

    @mock.patch('subprocess.Popen', autospec=True)
    def test_prebuild_index_returns_error(self, mock_popen):
        # See https://stackoverflow.com/a/36501078/866026
        mock_popen.return_value = mock.Mock()
        mock_popen_obj = mock_popen.return_value
        mock_popen_obj.communicate.return_value = ('', 'Some Error')
        mock_popen_obj.returncode = 0

        index = search_index.SearchIndex(prebuild_index=True)
        expected = {
            'docs': [],
            'config': {'prebuild_index': True}
        }
        result = json.loads(index.generate_search_index())
        self.assertEqual(mock_popen.call_count, 1)
        self.assertEqual(mock_popen_obj.communicate.call_count, 1)
        self.assertEqual(result, expected)

    @mock.patch('subprocess.Popen', autospec=True)
    def test_prebuild_index_raises_ioerror(self, mock_popen):
        # See https://stackoverflow.com/a/36501078/866026
        mock_popen.return_value = mock.Mock()
        mock_popen_obj = mock_popen.return_value
        mock_popen_obj.communicate.side_effect = OSError
        mock_popen_obj.returncode = 1

        index = search_index.SearchIndex(prebuild_index=True)
        expected = {
            'docs': [],
            'config': {'prebuild_index': True}
        }
        result = json.loads(index.generate_search_index())
        self.assertEqual(mock_popen.call_count, 1)
        self.assertEqual(mock_popen_obj.communicate.call_count, 1)
        self.assertEqual(result, expected)

    @mock.patch('subprocess.Popen', autospec=True, side_effect=OSError)
    def test_prebuild_index_raises_oserror(self, mock_popen):
        # See https://stackoverflow.com/a/36501078/866026
        mock_popen.return_value = mock.Mock()
        mock_popen_obj = mock_popen.return_value
        mock_popen_obj.communicate.return_value = ('', '')
        mock_popen_obj.returncode = 0

        index = search_index.SearchIndex(prebuild_index=True)
        expected = {
            'docs': [],
            'config': {'prebuild_index': True}
        }
        result = json.loads(index.generate_search_index())
        self.assertEqual(mock_popen.call_count, 1)
        self.assertEqual(mock_popen_obj.communicate.call_count, 0)
        self.assertEqual(result, expected)

    @mock.patch('subprocess.Popen', autospec=True)
    def test_prebuild_index_false(self, mock_popen):
        # See https://stackoverflow.com/a/36501078/866026
        mock_popen.return_value = mock.Mock()
        mock_popen_obj = mock_popen.return_value
        mock_popen_obj.communicate.return_value = ('', '')
        mock_popen_obj.returncode = 0

        index = search_index.SearchIndex(prebuild_index=False)
        expected = {
            'docs': [],
            'config': {'prebuild_index': False}
        }
        result = json.loads(index.generate_search_index())
        self.assertEqual(mock_popen.call_count, 0)
        self.assertEqual(mock_popen_obj.communicate.call_count, 0)
        self.assertEqual(result, expected)

    @mock.patch('mkdocs.contrib.search.search_index.lunr', autospec=True)
    def test_prebuild_index_python(self, mock_lunr):
        mock_lunr.return_value.serialize.return_value = {'mock': 'index'}
        index = search_index.SearchIndex(prebuild_index='python', lang='en')
        expected = {
            'docs': [],
            'config': {'prebuild_index': 'python', 'lang': 'en'},
            'index': {'mock': 'index'}
        }
        result = json.loads(index.generate_search_index())
        self.assertEqual(mock_lunr.call_count, 1)
        self.assertEqual(result, expected)

    @mock.patch('subprocess.Popen', autospec=True)
    def test_prebuild_index_node(self, mock_popen):
        # See https://stackoverflow.com/a/36501078/866026
        mock_popen.return_value = mock.Mock()
        mock_popen_obj = mock_popen.return_value
        mock_popen_obj.communicate.return_value = ('{"mock": "index"}', None)
        mock_popen_obj.returncode = 0

        index = search_index.SearchIndex(prebuild_index='node')
        expected = {
            'docs': [],
            'config': {'prebuild_index': 'node'},
            'index': {'mock': 'index'}
        }
        result = json.loads(index.generate_search_index())
        self.assertEqual(mock_popen.call_count, 1)
        self.assertEqual(mock_popen_obj.communicate.call_count, 1)
        self.assertEqual(result, expected)

import unittest
import os
import sys
from unittest import mock
from tempfile import TemporaryDirectory

from mkdocs.structure.pages import Page
from mkdocs.structure.files import File, Files
from mkdocs.tests.base import load_config, dedent


class PageTests(unittest.TestCase):

    DOCS_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), '../integration/subpages/docs')

    def test_homepage(self):
        cfg = load_config(docs_dir=self.DOCS_DIR)
        fl = File('index.md', cfg['docs_dir'], cfg['site_dir'], cfg['use_directory_urls'])
        self.assertIsNone(fl.page)
        pg = Page('Foo', fl, cfg)
        self.assertEqual(fl.page, pg)
        self.assertEqual(pg.url, '')
        self.assertEqual(pg.abs_url, None)
        self.assertEqual(pg.canonical_url, None)
        self.assertEqual(pg.edit_url, None)
        self.assertEqual(pg.file, fl)
        self.assertEqual(pg.content, None)
        self.assertTrue(pg.is_homepage)
        self.assertTrue(pg.is_index)
        self.assertTrue(pg.is_page)
        self.assertFalse(pg.is_section)
        self.assertTrue(pg.is_top_level)
        self.assertEqual(pg.markdown, None)
        self.assertEqual(pg.meta, {})
        self.assertEqual(pg.next_page, None)
        self.assertEqual(pg.parent, None)
        self.assertEqual(pg.previous_page, None)
        self.assertEqual(pg.title, 'Foo')
        self.assertEqual(pg.toc, [])

    def test_nested_index_page(self):
        cfg = load_config(docs_dir=self.DOCS_DIR)
        fl = File('sub1/index.md', cfg['docs_dir'], cfg['site_dir'], cfg['use_directory_urls'])
        pg = Page('Foo', fl, cfg)
        pg.parent = 'foo'
        self.assertEqual(pg.url, 'sub1/')
        self.assertEqual(pg.abs_url, None)
        self.assertEqual(pg.canonical_url, None)
        self.assertEqual(pg.edit_url, None)
        self.assertEqual(pg.file, fl)
        self.assertEqual(pg.content, None)
        self.assertFalse(pg.is_homepage)
        self.assertTrue(pg.is_index)
        self.assertTrue(pg.is_page)
        self.assertFalse(pg.is_section)
        self.assertFalse(pg.is_top_level)
        self.assertEqual(pg.markdown, None)
        self.assertEqual(pg.meta, {})
        self.assertEqual(pg.next_page, None)
        self.assertEqual(pg.parent, 'foo')
        self.assertEqual(pg.previous_page, None)
        self.assertEqual(pg.title, 'Foo')
        self.assertEqual(pg.toc, [])

    def test_nested_index_page_no_parent(self):
        cfg = load_config(docs_dir=self.DOCS_DIR)
        fl = File('sub1/index.md', cfg['docs_dir'], cfg['site_dir'], cfg['use_directory_urls'])
        pg = Page('Foo', fl, cfg)
        pg.parent = None  # non-homepage at nav root level; see #1919.
        self.assertEqual(pg.url, 'sub1/')
        self.assertEqual(pg.abs_url, None)
        self.assertEqual(pg.canonical_url, None)
        self.assertEqual(pg.edit_url, None)
        self.assertEqual(pg.file, fl)
        self.assertEqual(pg.content, None)
        self.assertFalse(pg.is_homepage)
        self.assertTrue(pg.is_index)
        self.assertTrue(pg.is_page)
        self.assertFalse(pg.is_section)
        self.assertTrue(pg.is_top_level)
        self.assertEqual(pg.markdown, None)
        self.assertEqual(pg.meta, {})
        self.assertEqual(pg.next_page, None)
        self.assertEqual(pg.parent, None)
        self.assertEqual(pg.previous_page, None)
        self.assertEqual(pg.title, 'Foo')
        self.assertEqual(pg.toc, [])

    def test_nested_index_page_no_parent_no_directory_urls(self):
        cfg = load_config(docs_dir=self.DOCS_DIR, use_directory_urls=False)
        fl = File('sub1/index.md', cfg['docs_dir'], cfg['site_dir'], cfg['use_directory_urls'])
        pg = Page('Foo', fl, cfg)
        pg.parent = None  # non-homepage at nav root level; see #1919.
        self.assertEqual(pg.url, 'sub1/index.html')
        self.assertEqual(pg.abs_url, None)
        self.assertEqual(pg.canonical_url, None)
        self.assertEqual(pg.edit_url, None)
        self.assertEqual(pg.file, fl)
        self.assertEqual(pg.content, None)
        self.assertFalse(pg.is_homepage)
        self.assertTrue(pg.is_index)
        self.assertTrue(pg.is_page)
        self.assertFalse(pg.is_section)
        self.assertTrue(pg.is_top_level)
        self.assertEqual(pg.markdown, None)
        self.assertEqual(pg.meta, {})
        self.assertEqual(pg.next_page, None)
        self.assertEqual(pg.parent, None)
        self.assertEqual(pg.previous_page, None)
        self.assertEqual(pg.title, 'Foo')
        self.assertEqual(pg.toc, [])

    def test_nested_nonindex_page(self):
        cfg = load_config(docs_dir=self.DOCS_DIR)
        fl = File('sub1/non-index.md', cfg['docs_dir'], cfg['site_dir'], cfg['use_directory_urls'])
        pg = Page('Foo', fl, cfg)
        pg.parent = 'foo'
        self.assertEqual(pg.url, 'sub1/non-index/')
        self.assertEqual(pg.abs_url, None)
        self.assertEqual(pg.canonical_url, None)
        self.assertEqual(pg.edit_url, None)
        self.assertEqual(pg.file, fl)
        self.assertEqual(pg.content, None)
        self.assertFalse(pg.is_homepage)
        self.assertFalse(pg.is_index)
        self.assertTrue(pg.is_page)
        self.assertFalse(pg.is_section)
        self.assertFalse(pg.is_top_level)
        self.assertEqual(pg.markdown, None)
        self.assertEqual(pg.meta, {})
        self.assertEqual(pg.next_page, None)
        self.assertEqual(pg.parent, 'foo')
        self.assertEqual(pg.previous_page, None)
        self.assertEqual(pg.title, 'Foo')
        self.assertEqual(pg.toc, [])

    def test_page_defaults(self):
        cfg = load_config()
        fl = File('testing.md', cfg['docs_dir'], cfg['site_dir'], cfg['use_directory_urls'])
        pg = Page('Foo', fl, cfg)
        self.assertRegex(pg.update_date, r'\d{4}-\d{2}-\d{2}')
        self.assertEqual(pg.url, 'testing/')
        self.assertEqual(pg.abs_url, None)
        self.assertEqual(pg.canonical_url, None)
        self.assertEqual(pg.edit_url, None)
        self.assertEqual(pg.file, fl)
        self.assertEqual(pg.content, None)
        self.assertFalse(pg.is_homepage)
        self.assertFalse(pg.is_index)
        self.assertTrue(pg.is_page)
        self.assertFalse(pg.is_section)
        self.assertTrue(pg.is_top_level)
        self.assertEqual(pg.markdown, None)
        self.assertEqual(pg.meta, {})
        self.assertEqual(pg.next_page, None)
        self.assertEqual(pg.parent, None)
        self.assertEqual(pg.previous_page, None)
        self.assertEqual(pg.title, 'Foo')
        self.assertEqual(pg.toc, [])

    def test_page_no_directory_url(self):
        cfg = load_config(use_directory_urls=False)
        fl = File('testing.md', cfg['docs_dir'], cfg['site_dir'], cfg['use_directory_urls'])
        pg = Page('Foo', fl, cfg)
        self.assertEqual(pg.url, 'testing.html')
        self.assertEqual(pg.abs_url, None)
        self.assertEqual(pg.canonical_url, None)
        self.assertEqual(pg.edit_url, None)
        self.assertEqual(pg.file, fl)
        self.assertEqual(pg.content, None)
        self.assertFalse(pg.is_homepage)
        self.assertFalse(pg.is_index)
        self.assertTrue(pg.is_page)
        self.assertFalse(pg.is_section)
        self.assertTrue(pg.is_top_level)
        self.assertEqual(pg.markdown, None)
        self.assertEqual(pg.meta, {})
        self.assertEqual(pg.next_page, None)
        self.assertEqual(pg.parent, None)
        self.assertEqual(pg.previous_page, None)
        self.assertEqual(pg.title, 'Foo')
        self.assertEqual(pg.toc, [])

    def test_page_canonical_url(self):
        cfg = load_config(site_url='http://example.com')
        fl = File('testing.md', cfg['docs_dir'], cfg['site_dir'], cfg['use_directory_urls'])
        pg = Page('Foo', fl, cfg)
        self.assertEqual(pg.url, 'testing/')
        self.assertEqual(pg.abs_url, '/testing/')
        self.assertEqual(pg.canonical_url, 'http://example.com/testing/')
        self.assertEqual(pg.edit_url, None)
        self.assertEqual(pg.file, fl)
        self.assertEqual(pg.content, None)
        self.assertFalse(pg.is_homepage)
        self.assertFalse(pg.is_index)
        self.assertTrue(pg.is_page)
        self.assertFalse(pg.is_section)
        self.assertTrue(pg.is_top_level)
        self.assertEqual(pg.markdown, None)
        self.assertEqual(pg.meta, {})
        self.assertEqual(pg.next_page, None)
        self.assertEqual(pg.parent, None)
        self.assertEqual(pg.previous_page, None)
        self.assertEqual(pg.title, 'Foo')
        self.assertEqual(pg.toc, [])

    def test_page_canonical_url_nested(self):
        cfg = load_config(site_url='http://example.com/foo/')
        fl = File('testing.md', cfg['docs_dir'], cfg['site_dir'], cfg['use_directory_urls'])
        pg = Page('Foo', fl, cfg)
        self.assertEqual(pg.url, 'testing/')
        self.assertEqual(pg.abs_url, '/foo/testing/')
        self.assertEqual(pg.canonical_url, 'http://example.com/foo/testing/')
        self.assertEqual(pg.edit_url, None)
        self.assertEqual(pg.file, fl)
        self.assertEqual(pg.content, None)
        self.assertFalse(pg.is_homepage)
        self.assertFalse(pg.is_index)
        self.assertTrue(pg.is_page)
        self.assertFalse(pg.is_section)
        self.assertTrue(pg.is_top_level)
        self.assertEqual(pg.markdown, None)
        self.assertEqual(pg.meta, {})
        self.assertEqual(pg.next_page, None)
        self.assertEqual(pg.parent, None)
        self.assertEqual(pg.previous_page, None)
        self.assertEqual(pg.title, 'Foo')
        self.assertEqual(pg.toc, [])

    def test_page_canonical_url_nested_no_slash(self):
        cfg = load_config(site_url='http://example.com/foo')
        fl = File('testing.md', cfg['docs_dir'], cfg['site_dir'], cfg['use_directory_urls'])
        pg = Page('Foo', fl, cfg)
        self.assertEqual(pg.url, 'testing/')
        self.assertEqual(pg.abs_url, '/foo/testing/')
        self.assertEqual(pg.canonical_url, 'http://example.com/foo/testing/')
        self.assertEqual(pg.edit_url, None)
        self.assertEqual(pg.file, fl)
        self.assertEqual(pg.content, None)
        self.assertFalse(pg.is_homepage)
        self.assertFalse(pg.is_index)
        self.assertTrue(pg.is_page)
        self.assertFalse(pg.is_section)
        self.assertTrue(pg.is_top_level)
        self.assertEqual(pg.markdown, None)
        self.assertEqual(pg.meta, {})
        self.assertEqual(pg.next_page, None)
        self.assertEqual(pg.parent, None)
        self.assertEqual(pg.previous_page, None)
        self.assertEqual(pg.title, 'Foo')
        self.assertEqual(pg.toc, [])

    def test_predefined_page_title(self):
        cfg = load_config()
        fl = File('testing.md', cfg['docs_dir'], cfg['site_dir'], cfg['use_directory_urls'])
        pg = Page('Page Title', fl, cfg)
        pg.read_source(cfg)
        self.assertEqual(pg.url, 'testing/')
        self.assertEqual(pg.abs_url, None)
        self.assertEqual(pg.canonical_url, None)
        self.assertEqual(pg.edit_url, None)
        self.assertEqual(pg.file, fl)
        self.assertEqual(pg.content, None)
        self.assertFalse(pg.is_homepage)
        self.assertFalse(pg.is_index)
        self.assertTrue(pg.is_page)
        self.assertFalse(pg.is_section)
        self.assertTrue(pg.is_top_level)
        self.assertTrue(pg.markdown.startswith('# Welcome to MkDocs\n'))
        self.assertEqual(pg.meta, {})
        self.assertEqual(pg.next_page, None)
        self.assertEqual(pg.parent, None)
        self.assertEqual(pg.previous_page, None)
        self.assertEqual(pg.title, 'Page Title')
        self.assertEqual(pg.toc, [])

    def test_page_title_from_markdown(self):
        cfg = load_config()
        fl = File('testing.md', cfg['docs_dir'], cfg['site_dir'], cfg['use_directory_urls'])
        pg = Page(None, fl, cfg)
        pg.read_source(cfg)
        self.assertEqual(pg.url, 'testing/')
        self.assertEqual(pg.abs_url, None)
        self.assertEqual(pg.canonical_url, None)
        self.assertEqual(pg.edit_url, None)
        self.assertEqual(pg.file, fl)
        self.assertEqual(pg.content, None)
        self.assertFalse(pg.is_homepage)
        self.assertFalse(pg.is_index)
        self.assertTrue(pg.is_page)
        self.assertFalse(pg.is_section)
        self.assertTrue(pg.is_top_level)
        self.assertTrue(pg.markdown.startswith('# Welcome to MkDocs\n'))
        self.assertEqual(pg.meta, {})
        self.assertEqual(pg.next_page, None)
        self.assertEqual(pg.parent, None)
        self.assertEqual(pg.previous_page, None)
        self.assertEqual(pg.title, 'Welcome to MkDocs')
        self.assertEqual(pg.toc, [])

    def test_page_title_from_meta(self):
        cfg = load_config(docs_dir=self.DOCS_DIR)
        fl = File('metadata.md', cfg['docs_dir'], cfg['site_dir'], cfg['use_directory_urls'])
        pg = Page(None, fl, cfg)
        pg.read_source(cfg)
        self.assertEqual(pg.url, 'metadata/')
        self.assertEqual(pg.abs_url, None)
        self.assertEqual(pg.canonical_url, None)
        self.assertEqual(pg.edit_url, None)
        self.assertEqual(pg.file, fl)
        self.assertEqual(pg.content, None)
        self.assertFalse(pg.is_homepage)
        self.assertFalse(pg.is_index)
        self.assertTrue(pg.is_page)
        self.assertFalse(pg.is_section)
        self.assertTrue(pg.is_top_level)
        self.assertTrue(pg.markdown.startswith('# Welcome to MkDocs\n'))
        self.assertEqual(pg.meta, {'title': 'A Page Title'})
        self.assertEqual(pg.next_page, None)
        self.assertEqual(pg.parent, None)
        self.assertEqual(pg.previous_page, None)
        self.assertEqual(pg.title, 'A Page Title')
        self.assertEqual(pg.toc, [])

    def test_page_title_from_filename(self):
        cfg = load_config(docs_dir=self.DOCS_DIR)
        fl = File('page-title.md', cfg['docs_dir'], cfg['site_dir'], cfg['use_directory_urls'])
        pg = Page(None, fl, cfg)
        pg.read_source(cfg)
        self.assertEqual(pg.url, 'page-title/')
        self.assertEqual(pg.abs_url, None)
        self.assertEqual(pg.canonical_url, None)
        self.assertEqual(pg.edit_url, None)
        self.assertEqual(pg.file, fl)
        self.assertEqual(pg.content, None)
        self.assertFalse(pg.is_homepage)
        self.assertFalse(pg.is_index)
        self.assertTrue(pg.is_page)
        self.assertFalse(pg.is_section)
        self.assertTrue(pg.is_top_level)
        self.assertTrue(pg.markdown.startswith('Page content.\n'))
        self.assertEqual(pg.meta, {})
        self.assertEqual(pg.next_page, None)
        self.assertEqual(pg.parent, None)
        self.assertEqual(pg.previous_page, None)
        self.assertEqual(pg.title, 'Page title')
        self.assertEqual(pg.toc, [])

    def test_page_title_from_capitalized_filename(self):
        cfg = load_config(docs_dir=self.DOCS_DIR)
        fl = File('pageTitle.md', cfg['docs_dir'], cfg['site_dir'], cfg['use_directory_urls'])
        pg = Page(None, fl, cfg)
        pg.read_source(cfg)
        self.assertEqual(pg.url, 'pageTitle/')
        self.assertEqual(pg.abs_url, None)
        self.assertEqual(pg.canonical_url, None)
        self.assertEqual(pg.edit_url, None)
        self.assertEqual(pg.file, fl)
        self.assertEqual(pg.content, None)
        self.assertFalse(pg.is_homepage)
        self.assertFalse(pg.is_index)
        self.assertTrue(pg.is_page)
        self.assertFalse(pg.is_section)
        self.assertTrue(pg.is_top_level)
        self.assertTrue(pg.markdown.startswith('Page content.\n'))
        self.assertEqual(pg.meta, {})
        self.assertEqual(pg.next_page, None)
        self.assertEqual(pg.parent, None)
        self.assertEqual(pg.previous_page, None)
        self.assertEqual(pg.title, 'pageTitle')
        self.assertEqual(pg.toc, [])

    def test_page_title_from_homepage_filename(self):
        cfg = load_config(docs_dir=self.DOCS_DIR)
        fl = File('index.md', cfg['docs_dir'], cfg['site_dir'], cfg['use_directory_urls'])
        pg = Page(None, fl, cfg)
        pg.read_source(cfg)
        self.assertEqual(pg.url, '')
        self.assertEqual(pg.abs_url, None)
        self.assertEqual(pg.canonical_url, None)
        self.assertEqual(pg.edit_url, None)
        self.assertEqual(pg.file, fl)
        self.assertEqual(pg.content, None)
        self.assertTrue(pg.is_homepage)
        self.assertTrue(pg.is_index)
        self.assertTrue(pg.is_page)
        self.assertFalse(pg.is_section)
        self.assertTrue(pg.is_top_level)
        self.assertTrue(pg.markdown.startswith('## Test'))
        self.assertEqual(pg.meta, {})
        self.assertEqual(pg.next_page, None)
        self.assertEqual(pg.parent, None)
        self.assertEqual(pg.previous_page, None)
        self.assertEqual(pg.title, 'Home')
        self.assertEqual(pg.toc, [])

    def test_page_eq(self):
        cfg = load_config()
        fl = File('testing.md', cfg['docs_dir'], cfg['site_dir'], cfg['use_directory_urls'])
        pg = Page('Foo', fl, cfg)
        self.assertTrue(pg == Page('Foo', fl, cfg))

    def test_page_ne(self):
        cfg = load_config()
        f1 = File('testing.md', cfg['docs_dir'], cfg['site_dir'], cfg['use_directory_urls'])
        f2 = File('index.md', cfg['docs_dir'], cfg['site_dir'], cfg['use_directory_urls'])
        pg = Page('Foo', f1, cfg)
        # Different Title
        self.assertTrue(pg != Page('Bar', f1, cfg))
        # Different File
        self.assertTrue(pg != Page('Foo', f2, cfg))

    def test_BOM(self):
        md_src = '# An UTF-8 encoded file with a BOM'
        with TemporaryDirectory() as docs_dir:
            # We don't use mkdocs.tests.base.tempdir decorator here due to uniqueness of this test.
            cfg = load_config(docs_dir=docs_dir)
            fl = File('index.md', cfg['docs_dir'], cfg['site_dir'], cfg['use_directory_urls'])
            pg = Page(None, fl, cfg)
            # Create an UTF-8 Encoded file with BOM (as Microsoft editors do). See #1186
            with open(fl.abs_src_path, 'w', encoding='utf-8-sig') as f:
                f.write(md_src)
            # Now read the file.
            pg.read_source(cfg)
            # Ensure the BOM (`\ufeff`) is removed
            self.assertNotIn('\ufeff', pg.markdown)
            self.assertEqual(pg.markdown, md_src)
            self.assertEqual(pg.meta, {})

    def test_page_edit_url(self):
        configs = [
            {
                'repo_url': 'http://github.com/mkdocs/mkdocs'
            },
            {
                'repo_url': 'https://github.com/mkdocs/mkdocs/'
            }, {
                'repo_url': 'http://example.com'
            }, {
                'repo_url': 'http://example.com',
                'edit_uri': 'edit/master'
            }, {
                'repo_url': 'http://example.com',
                'edit_uri': '/edit/master'
            }, {
                'repo_url': 'http://example.com/foo/',
                'edit_uri': '/edit/master/'
            }, {
                'repo_url': 'http://example.com/foo',
                'edit_uri': '/edit/master/'
            }, {
                'repo_url': 'http://example.com/foo/',
                'edit_uri': '/edit/master'
            }, {
                'repo_url': 'http://example.com/foo/',
                'edit_uri': 'edit/master/'
            }, {
                'repo_url': 'http://example.com/foo',
                'edit_uri': 'edit/master/'
            }, {
                'repo_url': 'http://example.com',
                'edit_uri': '?query=edit/master'
            }, {
                'repo_url': 'http://example.com/',
                'edit_uri': '?query=edit/master/'
            }, {
                'repo_url': 'http://example.com',
                'edit_uri': '#edit/master'
            }, {
                'repo_url': 'http://example.com/',
                'edit_uri': '#edit/master/'
            }, {
                'repo_url': 'http://example.com',
                'edit_uri': ''  # Set to blank value
            }, {
                # Nothing defined
            }
        ]

        expected = [
            'http://github.com/mkdocs/mkdocs/edit/master/docs/testing.md',
            'https://github.com/mkdocs/mkdocs/edit/master/docs/testing.md',
            None,
            'http://example.com/edit/master/testing.md',
            'http://example.com/edit/master/testing.md',
            'http://example.com/edit/master/testing.md',
            'http://example.com/edit/master/testing.md',
            'http://example.com/edit/master/testing.md',
            'http://example.com/foo/edit/master/testing.md',
            'http://example.com/foo/edit/master/testing.md',
            'http://example.com?query=edit/master/testing.md',
            'http://example.com/?query=edit/master/testing.md',
            'http://example.com#edit/master/testing.md',
            'http://example.com/#edit/master/testing.md',
            None,
            None
        ]

        for i, c in enumerate(configs):
            cfg = load_config(**c)
            fl = File('testing.md', cfg['docs_dir'], cfg['site_dir'], cfg['use_directory_urls'])
            pg = Page('Foo', fl, cfg)
            self.assertEqual(pg.url, 'testing/')
            self.assertEqual(pg.edit_url, expected[i])

    def test_nested_page_edit_url(self):
        configs = [
            {
                'repo_url': 'http://github.com/mkdocs/mkdocs'
            },
            {
                'repo_url': 'https://github.com/mkdocs/mkdocs/'
            }, {
                'repo_url': 'http://example.com'
            }, {
                'repo_url': 'http://example.com',
                'edit_uri': 'edit/master'
            }, {
                'repo_url': 'http://example.com',
                'edit_uri': '/edit/master'
            }, {
                'repo_url': 'http://example.com/foo/',
                'edit_uri': '/edit/master/'
            }, {
                'repo_url': 'http://example.com/foo',
                'edit_uri': '/edit/master/'
            }, {
                'repo_url': 'http://example.com/foo/',
                'edit_uri': '/edit/master'
            }, {
                'repo_url': 'http://example.com/foo/',
                'edit_uri': 'edit/master/'
            }, {
                'repo_url': 'http://example.com/foo',
                'edit_uri': 'edit/master/'
            }, {
                'repo_url': 'http://example.com',
                'edit_uri': '?query=edit/master'
            }, {
                'repo_url': 'http://example.com/',
                'edit_uri': '?query=edit/master/'
            }, {
                'repo_url': 'http://example.com',
                'edit_uri': '#edit/master'
            }, {
                'repo_url': 'http://example.com/',
                'edit_uri': '#edit/master/'
            }
        ]

        expected = [
            'http://github.com/mkdocs/mkdocs/edit/master/docs/sub1/non-index.md',
            'https://github.com/mkdocs/mkdocs/edit/master/docs/sub1/non-index.md',
            None,
            'http://example.com/edit/master/sub1/non-index.md',
            'http://example.com/edit/master/sub1/non-index.md',
            'http://example.com/edit/master/sub1/non-index.md',
            'http://example.com/edit/master/sub1/non-index.md',
            'http://example.com/edit/master/sub1/non-index.md',
            'http://example.com/foo/edit/master/sub1/non-index.md',
            'http://example.com/foo/edit/master/sub1/non-index.md',
            'http://example.com?query=edit/master/sub1/non-index.md',
            'http://example.com/?query=edit/master/sub1/non-index.md',
            'http://example.com#edit/master/sub1/non-index.md',
            'http://example.com/#edit/master/sub1/non-index.md'
        ]

        for i, c in enumerate(configs):
            c['docs_dir'] = self.DOCS_DIR
            cfg = load_config(**c)
            fl = File('sub1/non-index.md', cfg['docs_dir'], cfg['site_dir'], cfg['use_directory_urls'])
            pg = Page('Foo', fl, cfg)
            self.assertEqual(pg.url, 'sub1/non-index/')
            self.assertEqual(pg.edit_url, expected[i])

    @unittest.skipUnless(sys.platform.startswith("win"), "requires Windows")
    def test_nested_page_edit_url_windows(self):
        configs = [
            {
                'repo_url': 'http://github.com/mkdocs/mkdocs'
            },
            {
                'repo_url': 'https://github.com/mkdocs/mkdocs/'
            }, {
                'repo_url': 'http://example.com'
            }, {
                'repo_url': 'http://example.com',
                'edit_uri': 'edit/master'
            }, {
                'repo_url': 'http://example.com',
                'edit_uri': '/edit/master'
            }, {
                'repo_url': 'http://example.com/foo/',
                'edit_uri': '/edit/master/'
            }, {
                'repo_url': 'http://example.com/foo',
                'edit_uri': '/edit/master/'
            }, {
                'repo_url': 'http://example.com/foo/',
                'edit_uri': '/edit/master'
            }, {
                'repo_url': 'http://example.com/foo/',
                'edit_uri': 'edit/master/'
            }, {
                'repo_url': 'http://example.com/foo',
                'edit_uri': 'edit/master/'
            }, {
                'repo_url': 'http://example.com',
                'edit_uri': '?query=edit/master'
            }, {
                'repo_url': 'http://example.com/',
                'edit_uri': '?query=edit/master/'
            }, {
                'repo_url': 'http://example.com',
                'edit_uri': '#edit/master'
            }, {
                'repo_url': 'http://example.com/',
                'edit_uri': '#edit/master/'
            }
        ]

        expected = [
            'http://github.com/mkdocs/mkdocs/edit/master/docs/sub1/non-index.md',
            'https://github.com/mkdocs/mkdocs/edit/master/docs/sub1/non-index.md',
            None,
            'http://example.com/edit/master/sub1/non-index.md',
            'http://example.com/edit/master/sub1/non-index.md',
            'http://example.com/edit/master/sub1/non-index.md',
            'http://example.com/edit/master/sub1/non-index.md',
            'http://example.com/edit/master/sub1/non-index.md',
            'http://example.com/foo/edit/master/sub1/non-index.md',
            'http://example.com/foo/edit/master/sub1/non-index.md',
            'http://example.com?query=edit/master/sub1/non-index.md',
            'http://example.com/?query=edit/master/sub1/non-index.md',
            'http://example.com#edit/master/sub1/non-index.md',
            'http://example.com/#edit/master/sub1/non-index.md'
        ]

        for i, c in enumerate(configs):
            c['docs_dir'] = self.DOCS_DIR
            cfg = load_config(**c)
            fl = File('sub1\\non-index.md', cfg['docs_dir'], cfg['site_dir'], cfg['use_directory_urls'])
            pg = Page('Foo', fl, cfg)
            self.assertEqual(pg.url, 'sub1/non-index/')
            self.assertEqual(pg.edit_url, expected[i])

    def test_page_render(self):
        cfg = load_config()
        fl = File('testing.md', cfg['docs_dir'], cfg['site_dir'], cfg['use_directory_urls'])
        pg = Page('Foo', fl, cfg)
        pg.read_source(cfg)
        self.assertEqual(pg.content, None)
        self.assertEqual(pg.toc, [])
        pg.render(cfg, [fl])
        self.assertTrue(pg.content.startswith(
            '<h1 id="welcome-to-mkdocs">Welcome to MkDocs</h1>\n'
        ))
        self.assertEqual(str(pg.toc).strip(), dedent("""
            Welcome to MkDocs - #welcome-to-mkdocs
                Commands - #commands
                Project layout - #project-layout
        """))

    def test_missing_page(self):
        cfg = load_config()
        fl = File('missing.md', cfg['docs_dir'], cfg['site_dir'], cfg['use_directory_urls'])
        pg = Page('Foo', fl, cfg)
        self.assertRaises(OSError, pg.read_source, cfg)


class SourceDateEpochTests(unittest.TestCase):

    def setUp(self):
        self.default = os.environ.get('SOURCE_DATE_EPOCH', None)
        os.environ['SOURCE_DATE_EPOCH'] = '0'

    def test_source_date_epoch(self):
        cfg = load_config()
        fl = File('testing.md', cfg['docs_dir'], cfg['site_dir'], cfg['use_directory_urls'])
        pg = Page('Foo', fl, cfg)
        self.assertEqual(pg.update_date, '1970-01-01')

    def tearDown(self):
        if self.default is not None:
            os.environ['SOURCE_DATE_EPOCH'] = self.default
        else:
            del os.environ['SOURCE_DATE_EPOCH']


class RelativePathExtensionTests(unittest.TestCase):

    DOCS_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), '../integration/subpages/docs')

    def get_rendered_result(self, files):
        cfg = load_config(docs_dir=self.DOCS_DIR)
        fs = []
        for f in files:
            fs.append(File(f.replace('/', os.sep), cfg['docs_dir'], cfg['site_dir'], cfg['use_directory_urls']))
        pg = Page('Foo', fs[0], cfg)
        pg.read_source(cfg)
        pg.render(cfg, Files(fs))
        return pg.content

    @mock.patch('mkdocs.structure.pages.open', mock.mock_open(read_data='[link](non-index.md)'))
    def test_relative_html_link(self):
        self.assertEqual(
            self.get_rendered_result(['index.md', 'non-index.md']),
            '<p><a href="non-index/">link</a></p>'  # No trailing /
        )

    @mock.patch('mkdocs.structure.pages.open', mock.mock_open(read_data='[link](index.md)'))
    def test_relative_html_link_index(self):
        self.assertEqual(
            self.get_rendered_result(['non-index.md', 'index.md']),
            '<p><a href="..">link</a></p>'
        )

    @mock.patch('mkdocs.structure.pages.open', mock.mock_open(read_data='[link](sub2/index.md)'))
    def test_relative_html_link_sub_index(self):
        self.assertEqual(
            self.get_rendered_result(['index.md', 'sub2/index.md']),
            '<p><a href="sub2/">link</a></p>'  # No trailing /
        )

    @mock.patch('mkdocs.structure.pages.open', mock.mock_open(read_data='[link](sub2/non-index.md)'))
    def test_relative_html_link_sub_page(self):
        self.assertEqual(
            self.get_rendered_result(['index.md', 'sub2/non-index.md']),
            '<p><a href="sub2/non-index/">link</a></p>'  # No trailing /
        )

    @mock.patch('mkdocs.structure.pages.open', mock.mock_open(read_data='[link](file%20name.md)'))
    def test_relative_html_link_with_encoded_space(self):
        self.assertEqual(
            self.get_rendered_result(['index.md', 'file name.md']),
            '<p><a href="file%20name/">link</a></p>'
        )

    @mock.patch('mkdocs.structure.pages.open', mock.mock_open(read_data='[link](file name.md)'))
    def test_relative_html_link_with_unencoded_space(self):
        self.assertEqual(
            self.get_rendered_result(['index.md', 'file name.md']),
            '<p><a href="file%20name/">link</a></p>'
        )

    @mock.patch('mkdocs.structure.pages.open', mock.mock_open(read_data='[link](../index.md)'))
    def test_relative_html_link_parent_index(self):
        self.assertEqual(
            self.get_rendered_result(['sub2/non-index.md', 'index.md']),
            '<p><a href="../..">link</a></p>'
        )

    @mock.patch('mkdocs.structure.pages.open', mock.mock_open(read_data='[link](non-index.md#hash)'))
    def test_relative_html_link_hash(self):
        self.assertEqual(
            self.get_rendered_result(['index.md', 'non-index.md']),
            '<p><a href="non-index/#hash">link</a></p>'
        )

    @mock.patch('mkdocs.structure.pages.open', mock.mock_open(read_data='[link](sub2/index.md#hash)'))
    def test_relative_html_link_sub_index_hash(self):
        self.assertEqual(
            self.get_rendered_result(['index.md', 'sub2/index.md']),
            '<p><a href="sub2/#hash">link</a></p>'
        )

    @mock.patch('mkdocs.structure.pages.open', mock.mock_open(read_data='[link](sub2/non-index.md#hash)'))
    def test_relative_html_link_sub_page_hash(self):
        self.assertEqual(
            self.get_rendered_result(['index.md', 'sub2/non-index.md']),
            '<p><a href="sub2/non-index/#hash">link</a></p>'
        )

    @mock.patch('mkdocs.structure.pages.open', mock.mock_open(read_data='[link](#hash)'))
    def test_relative_html_link_hash_only(self):
        self.assertEqual(
            self.get_rendered_result(['index.md']),
            '<p><a href="#hash">link</a></p>'
        )

    @mock.patch('mkdocs.structure.pages.open', mock.mock_open(read_data='![image](image.png)'))
    def test_relative_image_link_from_homepage(self):
        self.assertEqual(
            self.get_rendered_result(['index.md', 'image.png']),
            '<p><img alt="image" src="image.png" /></p>'  # no opening ./
        )

    @mock.patch('mkdocs.structure.pages.open', mock.mock_open(read_data='![image](../image.png)'))
    def test_relative_image_link_from_subpage(self):
        self.assertEqual(
            self.get_rendered_result(['sub2/non-index.md', 'image.png']),
            '<p><img alt="image" src="../../image.png" /></p>'
        )

    @mock.patch('mkdocs.structure.pages.open', mock.mock_open(read_data='![image](image.png)'))
    def test_relative_image_link_from_sibling(self):
        self.assertEqual(
            self.get_rendered_result(['non-index.md', 'image.png']),
            '<p><img alt="image" src="../image.png" /></p>'
        )

    @mock.patch('mkdocs.structure.pages.open', mock.mock_open(read_data='*__not__ a link*.'))
    def test_no_links(self):
        self.assertEqual(
            self.get_rendered_result(['index.md']),
            '<p><em><strong>not</strong> a link</em>.</p>'
        )

    @mock.patch('mkdocs.structure.pages.open', mock.mock_open(read_data='[link](non-existent.md)'))
    def test_bad_relative_html_link(self):
        with self.assertLogs('mkdocs', level='WARNING') as cm:
            self.assertEqual(
                self.get_rendered_result(['index.md']),
                '<p><a href="non-existent.md">link</a></p>'
            )
        self.assertEqual(
            cm.output,
            ["WARNING:mkdocs.structure.pages:Documentation file 'index.md' contains a link "
             "to 'non-existent.md' which is not found in the documentation files."]
        )

    @mock.patch('mkdocs.structure.pages.open', mock.mock_open(read_data='[external](http://example.com/index.md)'))
    def test_external_link(self):
        self.assertEqual(
            self.get_rendered_result(['index.md']),
            '<p><a href="http://example.com/index.md">external</a></p>'
        )

    @mock.patch('mkdocs.structure.pages.open', mock.mock_open(read_data='[absolute link](/path/to/file.md)'))
    def test_absolute_link(self):
        self.assertEqual(
            self.get_rendered_result(['index.md']),
            '<p><a href="/path/to/file.md">absolute link</a></p>'
        )

    @mock.patch('mkdocs.structure.pages.open', mock.mock_open(read_data='[absolute local path](\\image.png)'))
    def test_absolute_win_local_path(self):
        self.assertEqual(
            self.get_rendered_result(['index.md']),
            '<p><a href="\\image.png">absolute local path</a></p>'
        )

    @mock.patch('mkdocs.structure.pages.open', mock.mock_open(read_data='<mail@example.com>'))
    def test_email_link(self):
        self.assertEqual(
            self.get_rendered_result(['index.md']),
            # Markdown's default behavior is to obscure email addresses by entity-encoding them.
            # The following is equivalent to: '<p><a href="mailto:mail@example.com">mail@example.com</a></p>'
            '<p><a href="&#109;&#97;&#105;&#108;&#116;&#111;&#58;&#109;&#97;&#105;&#108;&#64;&#101;'
            '&#120;&#97;&#109;&#112;&#108;&#101;&#46;&#99;&#111;&#109;">&#109;&#97;&#105;&#108;&#64;'
            '&#101;&#120;&#97;&#109;&#112;&#108;&#101;&#46;&#99;&#111;&#109;</a></p>'
        )

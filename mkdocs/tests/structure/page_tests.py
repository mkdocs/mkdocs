from __future__ import annotations

import os
import sys
import textwrap
import unittest
from unittest import mock

import markdown

from mkdocs.config.defaults import MkDocsConfig
from mkdocs.structure.files import File, Files
from mkdocs.structure.pages import Page, _ExtractTitleTreeprocessor, _RelativePathTreeprocessor
from mkdocs.tests.base import dedent, tempdir

DOCS_DIR = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), '..', 'integration', 'subpages', 'docs'
)


def load_config(**cfg) -> MkDocsConfig:
    cfg.setdefault('site_name', 'Example')
    cfg.setdefault(
        'docs_dir',
        os.path.join(
            os.path.abspath(os.path.dirname(__file__)), '..', 'integration', 'minimal', 'docs'
        ),
    )
    conf = MkDocsConfig()
    conf.load_dict(cfg)
    errors_warnings = conf.validate()
    assert errors_warnings == ([], []), errors_warnings
    return conf


class PageTests(unittest.TestCase):
    def test_homepage(self):
        cfg = load_config(docs_dir=DOCS_DIR)
        fl = File('index.md', cfg.docs_dir, cfg.site_dir, cfg.use_directory_urls)
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
        cfg = load_config(docs_dir=DOCS_DIR)
        fl = File('sub1/index.md', cfg.docs_dir, cfg.site_dir, cfg.use_directory_urls)
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
        cfg = load_config(docs_dir=DOCS_DIR)
        fl = File('sub1/index.md', cfg.docs_dir, cfg.site_dir, cfg.use_directory_urls)
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
        cfg = load_config(docs_dir=DOCS_DIR, use_directory_urls=False)
        fl = File('sub1/index.md', cfg.docs_dir, cfg.site_dir, cfg.use_directory_urls)
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
        cfg = load_config(docs_dir=DOCS_DIR)
        fl = File('sub1/non-index.md', cfg.docs_dir, cfg.site_dir, cfg.use_directory_urls)
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
        fl = File('testing.md', cfg.docs_dir, cfg.site_dir, cfg.use_directory_urls)
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
        fl = File('testing.md', cfg.docs_dir, cfg.site_dir, cfg.use_directory_urls)
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
        fl = File('testing.md', cfg.docs_dir, cfg.site_dir, cfg.use_directory_urls)
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
        fl = File('testing.md', cfg.docs_dir, cfg.site_dir, cfg.use_directory_urls)
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
        fl = File('testing.md', cfg.docs_dir, cfg.site_dir, cfg.use_directory_urls)
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
        fl = File('testing.md', cfg.docs_dir, cfg.site_dir, cfg.use_directory_urls)
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
        fl = File('testing.md', cfg.docs_dir, cfg.site_dir, cfg.use_directory_urls)
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
        pg.render(cfg, Files([fl]))
        self.assertEqual(pg.title, 'Welcome to MkDocs')

    def _test_extract_title(self, content, expected, extensions={}):
        md = markdown.Markdown(extensions=list(extensions.keys()), extension_configs=extensions)
        extract_title_ext = _ExtractTitleTreeprocessor()
        extract_title_ext._register(md)
        md.convert(content)
        self.assertEqual(extract_title_ext.title, expected)

    _SETEXT_CONTENT = dedent(
        '''
        Welcome to MkDocs Setext
        ========================

        This tests extracting a setext style title.
        '''
    )

    def test_page_title_from_setext_markdown(self):
        self._test_extract_title(
            self._SETEXT_CONTENT,
            expected='Welcome to MkDocs Setext',
        )

    def test_page_title_from_markdown_with_email(self):
        self._test_extract_title(
            '''# <foo@example.org>''',
            expected='&#102;&#111;&#111;&#64;&#101;&#120;&#97;&#109;&#112;&#108;&#101;&#46;&#111;&#114;&#103;',
        )

    def test_page_title_from_markdown_stripped_anchorlinks(self):
        self._test_extract_title(
            self._SETEXT_CONTENT,
            extensions={'toc': {'permalink': '&'}},
            expected='Welcome to MkDocs Setext',
        )

    def test_page_title_from_markdown_strip_footnoteref(self):
        foootnotes = '''\n\n[^1]: foo\n[^2]: bar'''
        self._test_extract_title(
            '''# Header[^1] foo[^2] bar''' + foootnotes,
            extensions={'footnotes': {}},
            expected='Header foo bar',
        )
        self._test_extract_title(
            '''# *Header[^1]* *foo*[^2]''' + foootnotes,
            extensions={'footnotes': {}},
            expected='Header foo',
        )
        self._test_extract_title(
            '''# *Header[^1][^2]s''' + foootnotes,
            extensions={'footnotes': {}},
            expected='*Headers',
        )

    def test_page_title_from_markdown_strip_formatting(self):
        self._test_extract_title(
            '''# \\*Hello --- *beautiful* `wor<dl>`''',
            extensions={'smarty': {}},
            expected='*Hello &mdash; beautiful wor&lt;dl&gt;',
        )

    def test_page_title_from_markdown_html_entity(self):
        self._test_extract_title('''# Foo &lt; &amp; bar''', expected='Foo &lt; &amp; bar')
        self._test_extract_title('''# Foo > & bar''', expected='Foo &gt; &amp; bar')

    def test_page_title_from_markdown_strip_raw_html(self):
        self._test_extract_title('''# Hello <b>world</b>''', expected='Hello world')

    def test_page_title_from_markdown_strip_comments(self):
        self._test_extract_title('''# foo <!-- comment with <em> --> bar''', expected='foo bar')

    def test_page_title_from_markdown_strip_image(self):
        self._test_extract_title('''# Hi ![😄](hah.png)''', expected='Hi 😄')
        self._test_extract_title('''# Hi *-![😄](hah.png)-*''', expected='Hi -😄-')

    _ATTRLIST_CONTENT = dedent(
        '''
        # Welcome to MkDocs Attr { #welcome }

        This tests extracting the title, with enabled attr_list markdown_extension.
        '''
    )

    def test_page_title_from_markdown_stripped_attr_list(self):
        self._test_extract_title(
            self._ATTRLIST_CONTENT,
            extensions={'attr_list': {}},
            expected='Welcome to MkDocs Attr',
        )

    def test_page_title_from_markdown_preserved_attr_list(self):
        self._test_extract_title(
            self._ATTRLIST_CONTENT,
            expected='Welcome to MkDocs Attr { #welcome }',
        )

    def test_page_title_from_meta(self):
        cfg = load_config(docs_dir=DOCS_DIR)
        fl = File('metadata.md', cfg.docs_dir, cfg.site_dir, cfg.use_directory_urls)
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
        pg.render(cfg, Files([fl]))
        self.assertEqual(pg.title, 'A Page Title')

    def test_page_title_from_filename(self):
        cfg = load_config(docs_dir=DOCS_DIR)
        fl = File('page-title.md', cfg.docs_dir, cfg.site_dir, cfg.use_directory_urls)
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
        pg.render(cfg, Files([fl]))
        self.assertEqual(pg.title, 'Page title')

    def test_page_title_from_capitalized_filename(self):
        cfg = load_config(docs_dir=DOCS_DIR)
        fl = File('pageTitle.md', cfg.docs_dir, cfg.site_dir, cfg.use_directory_urls)
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

    def test_page_title_from_homepage_filename(self):
        cfg = load_config(docs_dir=DOCS_DIR)
        fl = File('index.md', cfg.docs_dir, cfg.site_dir, cfg.use_directory_urls)
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
        fl = File('testing.md', cfg.docs_dir, cfg.site_dir, cfg.use_directory_urls)
        pg = Page('Foo', fl, cfg)
        self.assertTrue(pg == Page('Foo', fl, cfg))

    def test_page_ne(self):
        cfg = load_config()
        f1 = File('testing.md', cfg.docs_dir, cfg.site_dir, cfg.use_directory_urls)
        f2 = File('index.md', cfg.docs_dir, cfg.site_dir, cfg.use_directory_urls)
        pg = Page('Foo', f1, cfg)
        # Different Title
        self.assertTrue(pg != Page('Bar', f1, cfg))
        # Different File
        self.assertTrue(pg != Page('Foo', f2, cfg))

    @tempdir()
    def test_BOM(self, docs_dir):
        md_src = '# An UTF-8 encoded file with a BOM'
        cfg = load_config(docs_dir=docs_dir)
        fl = File('index.md', cfg.docs_dir, cfg.site_dir, cfg.use_directory_urls)
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

    def test_page_edit_url(
        self, paths={'testing.md': 'testing/', 'sub1/non-index.md': 'sub1/non-index/'}
    ):
        for case in [
            dict(
                config={'repo_url': 'http://github.com/mkdocs/mkdocs'},
                edit_url='http://github.com/mkdocs/mkdocs/edit/master/docs/testing.md',
                edit_url2='http://github.com/mkdocs/mkdocs/edit/master/docs/sub1/non-index.md',
            ),
            dict(
                config={'repo_url': 'https://github.com/mkdocs/mkdocs/'},
                edit_url='https://github.com/mkdocs/mkdocs/edit/master/docs/testing.md',
                edit_url2='https://github.com/mkdocs/mkdocs/edit/master/docs/sub1/non-index.md',
            ),
            dict(
                config={'repo_url': 'http://example.com'},
                edit_url=None,
                edit_url2=None,
            ),
            dict(
                config={'repo_url': 'http://example.com', 'edit_uri': 'edit/master'},
                edit_url='http://example.com/edit/master/testing.md',
                edit_url2='http://example.com/edit/master/sub1/non-index.md',
            ),
            dict(
                config={'repo_url': 'http://example.com', 'edit_uri': '/edit/master'},
                edit_url='http://example.com/edit/master/testing.md',
                edit_url2='http://example.com/edit/master/sub1/non-index.md',
            ),
            dict(
                config={'repo_url': 'http://example.com/foo/', 'edit_uri': '/edit/master/'},
                edit_url='http://example.com/edit/master/testing.md',
                edit_url2='http://example.com/edit/master/sub1/non-index.md',
            ),
            dict(
                config={'repo_url': 'http://example.com/foo', 'edit_uri': '/edit/master/'},
                edit_url='http://example.com/edit/master/testing.md',
                edit_url2='http://example.com/edit/master/sub1/non-index.md',
            ),
            dict(
                config={'repo_url': 'http://example.com/foo/', 'edit_uri': '/edit/master'},
                edit_url='http://example.com/edit/master/testing.md',
                edit_url2='http://example.com/edit/master/sub1/non-index.md',
            ),
            dict(
                config={'repo_url': 'http://example.com/foo/', 'edit_uri': 'edit/master/'},
                edit_url='http://example.com/foo/edit/master/testing.md',
                edit_url2='http://example.com/foo/edit/master/sub1/non-index.md',
            ),
            dict(
                config={'repo_url': 'http://example.com/foo', 'edit_uri': 'edit/master/'},
                edit_url='http://example.com/foo/edit/master/testing.md',
                edit_url2='http://example.com/foo/edit/master/sub1/non-index.md',
            ),
            dict(
                config={'repo_url': 'http://example.com', 'edit_uri': '?query=edit/master'},
                edit_url='http://example.com?query=edit/master/testing.md',
                edit_url2='http://example.com?query=edit/master/sub1/non-index.md',
            ),
            dict(
                config={'repo_url': 'http://example.com/', 'edit_uri': '?query=edit/master/'},
                edit_url='http://example.com/?query=edit/master/testing.md',
                edit_url2='http://example.com/?query=edit/master/sub1/non-index.md',
            ),
            dict(
                config={'repo_url': 'http://example.com', 'edit_uri': '#edit/master'},
                edit_url='http://example.com#edit/master/testing.md',
                edit_url2='http://example.com#edit/master/sub1/non-index.md',
            ),
            dict(
                config={'repo_url': 'http://example.com/', 'edit_uri': '#edit/master/'},
                edit_url='http://example.com/#edit/master/testing.md',
                edit_url2='http://example.com/#edit/master/sub1/non-index.md',
            ),
            dict(
                config={'edit_uri': 'http://example.com/edit/master'},
                edit_url='http://example.com/edit/master/testing.md',
                edit_url2='http://example.com/edit/master/sub1/non-index.md',
            ),
            dict(
                config={'edit_uri_template': 'https://github.com/project/repo/wiki/{path_noext}'},
                edit_url='https://github.com/project/repo/wiki/testing',
                edit_url2='https://github.com/project/repo/wiki/sub1/non-index',
            ),
            dict(
                config={
                    'repo_url': 'https://github.com/project/repo/wiki',
                    'edit_uri_template': '{path_noext}/_edit',
                },
                edit_url='https://github.com/project/repo/wiki/testing/_edit',
                edit_url2='https://github.com/project/repo/wiki/sub1/non-index/_edit',
            ),
            dict(
                config={
                    'repo_url': 'https://gitlab.com/project/repo',
                    'edit_uri_template': '-/sse/master/docs%2F{path!q}',
                },
                edit_url='https://gitlab.com/project/repo/-/sse/master/docs%2Ftesting.md',
                edit_url2='https://gitlab.com/project/repo/-/sse/master/docs%2Fsub1%2Fnon-index.md',
            ),
            dict(
                config={
                    'repo_url': 'https://bitbucket.org/project/repo/',
                    'edit_uri_template': 'src/master/docs/{path}?mode=edit',
                },
                edit_url='https://bitbucket.org/project/repo/src/master/docs/testing.md?mode=edit',
                edit_url2='https://bitbucket.org/project/repo/src/master/docs/sub1/non-index.md?mode=edit',
            ),
            dict(
                config={
                    'repo_url': 'http://example.com',
                    'edit_uri': '',
                    'edit_uri_template': '',
                },  # Set to blank value
                edit_url=None,
                edit_url2=None,
            ),
            dict(config={}, edit_url=None, edit_url2=None),  # Nothing defined
        ]:
            for i, path in enumerate(paths, 1):
                edit_url_key = f'edit_url{i}' if i > 1 else 'edit_url'
                with self.subTest(case['config'], path=path):
                    cfg = load_config(**case['config'])
                    fl = File(path, cfg.docs_dir, cfg.site_dir, cfg.use_directory_urls)
                    pg = Page('Foo', fl, cfg)
                    self.assertEqual(pg.url, paths[path])
                    self.assertEqual(pg.edit_url, case[edit_url_key])

    @unittest.skipUnless(sys.platform.startswith("win"), "requires Windows")
    def test_page_edit_url_windows(self):
        self.test_page_edit_url(
            paths={'testing.md': 'testing/', 'sub1\\non-index.md': 'sub1/non-index/'}
        )

    def test_page_edit_url_warning(self):
        for case in [
            dict(
                config={'edit_uri': 'edit/master'},
                edit_url='edit/master/testing.md',
                warning="WARNING:mkdocs.structure.pages:edit_uri: "
                "'edit/master/testing.md' is not a valid URL, it should include the http:// (scheme)",
            ),
        ]:
            with self.subTest(case['config']):
                with self.assertLogs('mkdocs') as cm:
                    cfg = load_config(**case['config'])
                    fl = File('testing.md', cfg.docs_dir, cfg.site_dir, cfg.use_directory_urls)
                    pg = Page('Foo', fl, cfg)
                self.assertEqual(pg.url, 'testing/')
                self.assertEqual(pg.edit_url, case['edit_url'])
                self.assertEqual(cm.output, [case['warning']])

    def test_page_edit_url_custom_from_file(self):
        for case in [
            dict(
                edit_uri='hooks.py',
                expected_edit_url='https://github.com/mkdocs/mkdocs/edit/master/docs/hooks.py',
            ),
            dict(
                edit_uri='../scripts/hooks.py',
                expected_edit_url='https://github.com/mkdocs/mkdocs/edit/master/scripts/hooks.py',
            ),
            dict(edit_uri=None, expected_edit_url=None),
        ]:
            with self.subTest(case['edit_uri']):
                cfg = load_config(repo_url='https://github.com/mkdocs/mkdocs')
                fl = File('testing.md', cfg.docs_dir, cfg.site_dir, cfg.use_directory_urls)
                fl.edit_uri = case['edit_uri']
                pg = Page('Foo', fl, cfg)
                self.assertEqual(pg.url, 'testing/')
                self.assertEqual(pg.edit_url, case['expected_edit_url'])

    def test_page_render(self):
        cfg = load_config()
        fl = File('testing.md', cfg.docs_dir, cfg.site_dir, cfg.use_directory_urls)
        pg = Page('Foo', fl, cfg)
        pg.read_source(cfg)
        self.assertEqual(pg.content, None)
        self.assertEqual(pg.toc, [])
        pg.render(cfg, Files([fl]))
        self.assertTrue(
            pg.content.startswith('<h1 id="welcome-to-mkdocs">Welcome to MkDocs</h1>\n')
        )
        self.assertEqual(
            str(pg.toc).strip(),
            dedent(
                """
                Welcome to MkDocs - #welcome-to-mkdocs
                    Commands - #commands
                    Project layout - #project-layout
                """
            ),
        )

    def test_missing_page(self):
        cfg = load_config()
        fl = File('missing.md', cfg.docs_dir, cfg.site_dir, cfg.use_directory_urls)
        pg = Page('Foo', fl, cfg)
        with self.assertLogs('mkdocs') as cm:
            with self.assertRaises(OSError):
                pg.read_source(cfg)
        self.assertEqual(
            '\n'.join(cm.output), 'ERROR:mkdocs.structure.pages:File not found: missing.md'
        )


class SourceDateEpochTests(unittest.TestCase):
    def setUp(self):
        self.default = os.environ.get('SOURCE_DATE_EPOCH', None)
        os.environ['SOURCE_DATE_EPOCH'] = '0'

    def test_source_date_epoch(self):
        cfg = load_config()
        fl = File('testing.md', cfg.docs_dir, cfg.site_dir, cfg.use_directory_urls)
        pg = Page('Foo', fl, cfg)
        self.assertEqual(pg.update_date, '1970-01-01')

    def tearDown(self):
        if self.default is not None:
            os.environ['SOURCE_DATE_EPOCH'] = self.default
        else:
            del os.environ['SOURCE_DATE_EPOCH']


class RelativePathExtensionTests(unittest.TestCase):
    def get_rendered_result(
        self, *, content: str, files: list[str], logs: str = '', **kwargs
    ) -> str:
        cfg = load_config(docs_dir=DOCS_DIR, **kwargs)
        fs = [File(f, cfg.docs_dir, cfg.site_dir, cfg.use_directory_urls) for f in files]
        pg = Page('Foo', fs[0], cfg)

        with mock.patch('mkdocs.structure.files.open', mock.mock_open(read_data=content)):
            pg.read_source(cfg)
        if logs:
            with self.assertLogs('mkdocs.structure.pages') as cm:
                pg.render(cfg, Files(fs))
            msgs = [f'{r.levelname}:{r.message}' for r in cm.records]
            self.assertEqual('\n'.join(msgs), textwrap.dedent(logs).strip('\n'))
        elif sys.version_info >= (3, 10):
            with self.assertNoLogs('mkdocs.structure.pages'):
                pg.render(cfg, Files(fs))
        else:
            pg.render(cfg, Files(fs))

        assert pg.content is not None
        content = pg.content
        if content.startswith('<p>') and content.endswith('</p>'):
            content = content[3:-4]
        return content

    def test_relative_html_link(self):
        self.assertEqual(
            self.get_rendered_result(
                content='[link](non-index.md)', files=['index.md', 'non-index.md']
            ),
            '<a href="non-index/">link</a>',
        )
        self.assertEqual(
            self.get_rendered_result(
                use_directory_urls=False,
                content='[link](non-index.md)',
                files=['index.md', 'non-index.md'],
            ),
            '<a href="non-index.html">link</a>',
        )

    def test_relative_html_link_index(self):
        self.assertEqual(
            self.get_rendered_result(
                content='[link](index.md)', files=['non-index.md', 'index.md']
            ),
            '<a href="../">link</a>',
        )
        self.assertEqual(
            self.get_rendered_result(
                use_directory_urls=False,
                content='[link](index.md)',
                files=['non-index.md', 'index.md'],
            ),
            '<a href="index.html">link</a>',
        )

    def test_relative_html_link_sub_index(self):
        self.assertEqual(
            self.get_rendered_result(
                content='[link](sub2/index.md)', files=['index.md', 'sub2/index.md']
            ),
            '<a href="sub2/">link</a>',
        )
        self.assertEqual(
            self.get_rendered_result(
                use_directory_urls=False,
                content='[link](sub2/index.md)',
                files=['index.md', 'sub2/index.md'],
            ),
            '<a href="sub2/index.html">link</a>',
        )

    def test_relative_html_link_sub_page(self):
        self.assertEqual(
            self.get_rendered_result(
                content='[link](sub2/non-index.md)', files=['index.md', 'sub2/non-index.md']
            ),
            '<a href="sub2/non-index/">link</a>',
        )
        self.assertEqual(
            self.get_rendered_result(
                use_directory_urls=False,
                content='[link](sub2/non-index.md)',
                files=['index.md', 'sub2/non-index.md'],
            ),
            '<a href="sub2/non-index.html">link</a>',
        )

    def test_relative_doc_link_without_extension(self):
        self.assertEqual(
            self.get_rendered_result(
                use_directory_urls=False,
                content='[link](bar/Dockerfile)',
                files=['foo/bar.md', 'foo/bar/Dockerfile'],
            ),
            '<a href="bar/Dockerfile">link</a>',
        )
        self.assertEqual(
            self.get_rendered_result(
                content='[link](bar/Dockerfile)',
                files=['foo/bar.md', 'foo/bar/Dockerfile'],
            ),
            '<a href="Dockerfile">link</a>',
        )

    def test_relative_html_link_with_encoded_space(self):
        self.assertEqual(
            self.get_rendered_result(
                content='[link](file%20name.md)', files=['index.md', 'file name.md']
            ),
            '<a href="file%20name/">link</a>',
        )

    def test_relative_html_link_with_unencoded_space(self):
        self.assertEqual(
            self.get_rendered_result(
                use_directory_urls=False,
                content='[link](file name.md)',
                files=['index.md', 'file name.md'],
            ),
            '<a href="file%20name.html">link</a>',
        )

    def test_relative_html_link_parent_index(self):
        self.assertEqual(
            self.get_rendered_result(
                content='[link](../index.md)', files=['sub2/non-index.md', 'index.md']
            ),
            '<a href="../../">link</a>',
        )
        self.assertEqual(
            self.get_rendered_result(
                use_directory_urls=False,
                content='[link](../index.md)',
                files=['sub2/non-index.md', 'index.md'],
            ),
            '<a href="../index.html">link</a>',
        )

    def test_relative_html_link_hash(self):
        self.assertEqual(
            self.get_rendered_result(
                content='[link](non-index.md#hash)', files=['index.md', 'non-index.md']
            ),
            '<a href="non-index/#hash">link</a>',
        )

    def test_relative_html_link_sub_index_hash(self):
        self.assertEqual(
            self.get_rendered_result(
                content='[link](sub2/index.md#hash)', files=['index.md', 'sub2/index.md']
            ),
            '<a href="sub2/#hash">link</a>',
        )
        self.assertEqual(
            self.get_rendered_result(
                use_directory_urls=False,
                content='[link](sub2/index.md#hash)',
                files=['index.md', 'sub2/index.md'],
            ),
            '<a href="sub2/index.html#hash">link</a>',
        )

    def test_relative_html_link_sub_page_hash(self):
        self.assertEqual(
            self.get_rendered_result(
                content='[link](sub2/non-index.md#hash)', files=['index.md', 'sub2/non-index.md']
            ),
            '<a href="sub2/non-index/#hash">link</a>',
        )

    def test_relative_html_link_hash_only(self):
        for use_directory_urls in True, False:
            self.assertEqual(
                self.get_rendered_result(
                    use_directory_urls=use_directory_urls,
                    content='[link](#hash)',
                    files=['index.md'],
                ),
                '<a href="#hash">link</a>',
            )

    def test_relative_image_link_from_homepage(self):
        for use_directory_urls in True, False:
            self.assertEqual(
                self.get_rendered_result(
                    use_directory_urls=use_directory_urls,
                    content='![image](image.png)',
                    files=['index.md', 'image.png'],
                ),
                '<img alt="image" src="image.png" />',  # no opening ./
            )

    def test_relative_image_link_from_subpage(self):
        self.assertEqual(
            self.get_rendered_result(
                content='![image](../image.png)', files=['sub2/non-index.md', 'image.png']
            ),
            '<img alt="image" src="../../image.png" />',
        )

    def test_relative_image_link_from_sibling(self):
        self.assertEqual(
            self.get_rendered_result(
                content='![image](image.png)', files=['non-index.md', 'image.png']
            ),
            '<img alt="image" src="../image.png" />',
        )
        self.assertEqual(
            self.get_rendered_result(
                use_directory_urls=False,
                content='![image](image.png)',
                files=['non-index.md', 'image.png'],
            ),
            '<img alt="image" src="image.png" />',
        )

    def test_no_links(self):
        self.assertEqual(
            self.get_rendered_result(content='*__not__ a link*.', files=['index.md']),
            '<em><strong>not</strong> a link</em>.',
        )

    def test_bad_relative_doc_link(self):
        self.assertEqual(
            self.get_rendered_result(
                content='[link](non-existent.md)',
                files=['index.md'],
                logs="WARNING:Doc file 'index.md' contains a link 'non-existent.md', but the target is not found among documentation files.",
            ),
            '<a href="non-existent.md">link</a>',
        )
        self.assertEqual(
            self.get_rendered_result(
                validation=dict(links=dict(not_found='info')),
                content='[link](../non-existent.md)',
                files=['sub/index.md'],
                logs="INFO:Doc file 'sub/index.md' contains a link '../non-existent.md', but the target 'non-existent.md' is not found among documentation files.",
            ),
            '<a href="../non-existent.md">link</a>',
        )

    def test_relative_slash_link_with_suggestion(self):
        self.assertEqual(
            self.get_rendered_result(
                content='[link](../about/)',
                files=['foo/index.md', 'about.md'],
                logs="INFO:Doc file 'foo/index.md' contains an unrecognized relative link '../about/', it was left as is. Did you mean '../about.md'?",
            ),
            '<a href="../about/">link</a>',
        )
        self.assertEqual(
            self.get_rendered_result(
                validation=dict(links=dict(unrecognized_links='warn')),
                content='[link](../#example)',
                files=['foo/bar.md', 'index.md'],
                logs="WARNING:Doc file 'foo/bar.md' contains an unrecognized relative link '../#example', it was left as is. Did you mean '../index.md#example'?",
            ),
            '<a href="../#example">link</a>',
        )

    def test_self_anchor_link_with_suggestion(self):
        self.assertEqual(
            self.get_rendered_result(
                content='[link](./#test)',
                files=['index.md'],
                logs="INFO:Doc file 'index.md' contains an unrecognized relative link './#test', it was left as is. Did you mean '#test'?",
            ),
            '<a href="./#test">link</a>',
        )

    def test_absolute_self_anchor_link_with_suggestion(self):
        self.assertEqual(
            self.get_rendered_result(
                content='[link](/index#test)',
                files=['index.md'],
                logs="INFO:Doc file 'index.md' contains an absolute link '/index#test', it was left as is. Did you mean '#test'?",
            ),
            '<a href="/index#test">link</a>',
        )

    def test_absolute_self_anchor_link_with_validation_and_suggestion(self):
        self.assertEqual(
            self.get_rendered_result(
                validation=dict(links=dict(absolute_links='relative_to_docs')),
                content='[link](/index#test)',
                files=['index.md'],
                logs="WARNING:Doc file 'index.md' contains a link '/index#test', but the target 'index' is not found among documentation files. Did you mean '#test'?",
            ),
            '<a href="/index#test">link</a>',
        )

    def test_absolute_anchor_link_with_validation(self):
        self.assertEqual(
            self.get_rendered_result(
                validation=dict(links=dict(absolute_links='relative_to_docs')),
                content='[link](/foo/bar.md#test)',
                files=['index.md', 'foo/bar.md'],
            ),
            '<a href="foo/bar/#test">link</a>',
        )

    def test_absolute_anchor_link_with_validation_and_suggestion(self):
        self.assertEqual(
            self.get_rendered_result(
                validation=dict(links=dict(absolute_links='relative_to_docs')),
                content='[link](/foo/bar#test)',
                files=['zoo/index.md', 'foo/bar.md'],
                logs="WARNING:Doc file 'zoo/index.md' contains a link '/foo/bar#test', but the target 'foo/bar' is not found among documentation files. Did you mean '/foo/bar.md#test'?",
            ),
            '<a href="/foo/bar#test">link</a>',
        )

    def test_external_link(self):
        self.assertEqual(
            self.get_rendered_result(
                content='[external](http://example.com/index.md)', files=['index.md']
            ),
            '<a href="http://example.com/index.md">external</a>',
        )

    def test_absolute_link_with_suggestion(self):
        self.assertEqual(
            self.get_rendered_result(
                content='[absolute link](/path/to/file.md)',
                files=['index.md', 'path/to/file.md'],
                logs="INFO:Doc file 'index.md' contains an absolute link '/path/to/file.md', it was left as is. Did you mean 'path/to/file.md'?",
            ),
            '<a href="/path/to/file.md">absolute link</a>',
        )
        self.assertEqual(
            self.get_rendered_result(
                use_directory_urls=False,
                content='[absolute link](/path/to/file/)',
                files=['path/index.md', 'path/to/file.md'],
                logs="INFO:Doc file 'path/index.md' contains an absolute link '/path/to/file/', it was left as is.",
            ),
            '<a href="/path/to/file/">absolute link</a>',
        )
        self.assertEqual(
            self.get_rendered_result(
                content='[absolute link](/path/to/file)',
                files=['path/index.md', 'path/to/file.md'],
                logs="INFO:Doc file 'path/index.md' contains an absolute link '/path/to/file', it was left as is. Did you mean 'to/file.md'?",
            ),
            '<a href="/path/to/file">absolute link</a>',
        )

    def test_absolute_link_with_validation(self):
        self.assertEqual(
            self.get_rendered_result(
                validation=dict(links=dict(absolute_links='relative_to_docs')),
                content='[absolute link](/path/to/file.md)',
                files=['index.md', 'path/to/file.md'],
            ),
            '<a href="path/to/file/">absolute link</a>',
        )
        self.assertEqual(
            self.get_rendered_result(
                validation=dict(links=dict(absolute_links='relative_to_docs')),
                use_directory_urls=False,
                content='[absolute link](/path/to/file.md)',
                files=['path/index.md', 'path/to/file.md'],
            ),
            '<a href="to/file.html">absolute link</a>',
        )

    def test_absolute_link_with_validation_and_suggestion(self):
        self.assertEqual(
            self.get_rendered_result(
                validation=dict(links=dict(absolute_links='relative_to_docs')),
                use_directory_urls=False,
                content='[absolute link](/path/to/file/)',
                files=['path/index.md', 'path/to/file.md'],
                logs="WARNING:Doc file 'path/index.md' contains a link '/path/to/file/', but the target 'path/to/file' is not found among documentation files.",
            ),
            '<a href="/path/to/file/">absolute link</a>',
        )
        self.assertEqual(
            self.get_rendered_result(
                validation=dict(links=dict(absolute_links='relative_to_docs')),
                content='[absolute link](/path/to/file)',
                files=['path/index.md', 'path/to/file.md'],
                logs="WARNING:Doc file 'path/index.md' contains a link '/path/to/file', but the target is not found among documentation files. Did you mean '/path/to/file.md'?",
            ),
            '<a href="/path/to/file">absolute link</a>',
        )

    def test_absolute_link_with_validation_just_slash(self):
        self.assertEqual(
            self.get_rendered_result(
                validation=dict(links=dict(absolute_links='relative_to_docs')),
                content='[absolute link](/)',
                files=['path/to/file.md', 'index.md'],
                logs="WARNING:Doc file 'path/to/file.md' contains a link '/', but the target '.' is not found among documentation files. Did you mean '/index.md'?",
            ),
            '<a href="/">absolute link</a>',
        )

    def test_absolute_link_preserved_and_warned(self):
        self.assertEqual(
            self.get_rendered_result(
                validation=dict(links=dict(absolute_links='warn')),
                content='[absolute link](/path/to/file.md)',
                files=['index.md'],
                logs="WARNING:Doc file 'index.md' contains an absolute link '/path/to/file.md', it was left as is.",
            ),
            '<a href="/path/to/file.md">absolute link</a>',
        )
        self.assertEqual(
            self.get_rendered_result(
                validation=dict(links=dict(absolute_links='ignore')),
                content='[absolute link](/path/to/file.md)',
                files=['index.md'],
            ),
            '<a href="/path/to/file.md">absolute link</a>',
        )

    def test_image_link_with_suggestion(self):
        self.assertEqual(
            self.get_rendered_result(
                content='![image](../image.png)',
                files=['foo/bar.md', 'foo/image.png'],
                logs="WARNING:Doc file 'foo/bar.md' contains a link '../image.png', but the target 'image.png' is not found among documentation files. Did you mean 'image.png'?",
            ),
            '<img alt="image" src="../image.png" />',
        )
        self.assertEqual(
            self.get_rendered_result(
                content='![image](/image.png)',
                files=['foo/bar.md', 'image.png'],
                logs="INFO:Doc file 'foo/bar.md' contains an absolute link '/image.png', it was left as is. Did you mean '../image.png'?",
            ),
            '<img alt="image" src="/image.png" />',
        )

    def test_absolute_win_local_path(self):
        for use_directory_urls in True, False:
            self.assertEqual(
                self.get_rendered_result(
                    use_directory_urls=use_directory_urls,
                    content='[absolute local path](\\image.png)',
                    files=['index.md'],
                    logs="INFO:Doc file 'index.md' contains an absolute link '\\image.png', it was left as is.",
                ),
                '<a href="\\image.png">absolute local path</a>',
            )

    def test_email_link(self):
        self.assertEqual(
            self.get_rendered_result(content='<mail@example.com>', files=['index.md']),
            # Markdown's default behavior is to obscure email addresses by entity-encoding them.
            # The following is equivalent to: '<a href="mailto:mail@example.com">mail@example.com</a>'
            '<a href="&#109;&#97;&#105;&#108;&#116;&#111;&#58;&#109;&#97;&#105;&#108;&#64;&#101;'
            '&#120;&#97;&#109;&#112;&#108;&#101;&#46;&#99;&#111;&#109;">&#109;&#97;&#105;&#108;&#64;'
            '&#101;&#120;&#97;&#109;&#112;&#108;&#101;&#46;&#99;&#111;&#109;</a>',
        )

    def test_invalid_email_link(self):
        self.assertEqual(
            self.get_rendered_result(
                content='[contact](mail@example.com)',
                files=['index.md'],
                logs="WARNING:Doc file 'index.md' contains a link 'mail@example.com', but the target is not found among documentation files. Did you mean 'mailto:mail@example.com'?",
            ),
            '<a href="mail@example.com">contact</a>',
        )

    def test_possible_target_uris(self):
        def test(paths, expected='', exp_true=None, exp_false=None):
            """Test that `possible_target_uris` yields expected values, for use_directory_urls = true and false."""
            for use_directory_urls, expected_paths in (
                (True, exp_true or expected),
                (False, exp_false or expected),
            ):
                with self.subTest(paths, use_directory_urls=use_directory_urls):
                    src_path, dest_path = paths
                    f = File(src_path, '', '', use_directory_urls)
                    actual = _RelativePathTreeprocessor._possible_target_uris(
                        f, dest_path, use_directory_urls
                    )
                    self.assertEqual(list(actual), expected_paths.split(', '))

        test(('index.md', 'index.md'), expected='index.md')
        test(('index.md', 'foo/bar.md'), expected='foo/bar.md')
        test(
            ('index.md', 'foo/bar'),
            expected='foo/bar, foo/bar/index.md, foo/bar/README.md, foo/bar.md',
        )

        test(('index.md', 'foo/bar.html'), expected='foo/bar.html, foo/bar.md')
        test(
            ('foo.md', 'foo/bar.html'),
            exp_true='foo/bar.html, foo/bar.md, foo/foo/bar.html, foo/foo/bar.md',
            exp_false='foo/bar.html, foo/bar.md',
        )

        test(('foo.md', 'index.md'), exp_true='index.md, foo/index.md', exp_false='index.md')
        test(('foo.md', 'foo.md'), exp_true='foo.md, foo/foo.md', exp_false='foo.md')
        test(('foo.md', 'bar.md'), exp_true='bar.md, foo/bar.md', exp_false='bar.md')
        test(
            ('foo.md', 'foo/bar.md'), exp_true='foo/bar.md, foo/foo/bar.md', exp_false='foo/bar.md'
        )
        test(
            ('foo.md', 'foo'),
            exp_true='foo, foo/index.md, foo/README.md, foo.md, foo/foo, foo/foo/index.md, foo/foo/README.md, foo/foo.md',
            exp_false='foo, foo/index.md, foo/README.md, foo.md',
        )
        test(
            ('foo.md', 'foo/bar'),
            exp_true='foo/bar, foo/bar/index.md, foo/bar/README.md, foo/bar.md, foo/foo/bar, foo/foo/bar/index.md, foo/foo/bar/README.md, foo/foo/bar.md',
            exp_false='foo/bar, foo/bar/index.md, foo/bar/README.md, foo/bar.md',
        )
        test(
            ('foo.md', 'foo/bar/'),
            exp_true='foo/bar, foo/bar/index.md, foo/bar/README.md, foo/bar.md, foo/foo/bar, foo/foo/bar/index.md, foo/foo/bar/README.md, foo/foo/bar.md',
            exp_false='foo/bar, foo/bar/index.md, foo/bar/README.md',
        )

        test(
            ('foo.md', 'foo.html'),
            exp_true='foo.html, foo.md, foo/foo.html, foo/foo.md',
            exp_false='foo.html, foo.md',
        )
        test(
            ('foo.md', '../foo/'),
            exp_true='../foo, foo, foo/index.md, foo/README.md, foo.md',
            exp_false='../foo',
        )
        test(
            ('foo.md', 'foo/'),
            exp_true='foo, foo/index.md, foo/README.md, foo.md, foo/foo, foo/foo/index.md, foo/foo/README.md, foo/foo.md',
            exp_false='foo, foo/index.md, foo/README.md',
        )
        test(('foo/index.md', 'index.md'), expected='foo/index.md')
        test(('foo/index.md', 'foo/bar.html'), expected='foo/foo/bar.html, foo/foo/bar.md')
        test(('foo/index.md', '../foo.html'), expected='foo.html, foo.md')
        test(('foo/index.md', '../'), expected='., index.md, README.md')
        test(
            ('foo/bar.md', 'index.md'),
            exp_true='foo/index.md, foo/bar/index.md',
            exp_false='foo/index.md',
        )
        test(
            ('foo/bar.md', 'foo.md'),
            exp_true='foo/foo.md, foo/bar/foo.md',
            exp_false='foo/foo.md',
        )
        test(
            ('foo/bar.md', 'bar.md'),
            exp_true='foo/bar.md, foo/bar/bar.md',
            exp_false='foo/bar.md',
        )
        test(
            ('foo/bar.md', 'foo/bar.md'),
            exp_true='foo/foo/bar.md, foo/bar/foo/bar.md',
            exp_false='foo/foo/bar.md',
        )
        test(
            ('foo/bar.md', 'foo'),
            exp_true='foo/foo, foo/foo/index.md, foo/foo/README.md, foo/foo.md, foo/bar/foo, foo/bar/foo/index.md, foo/bar/foo/README.md, foo/bar/foo.md',
            exp_false='foo/foo, foo/foo/index.md, foo/foo/README.md, foo/foo.md',
        )
        test(
            ('foo/bar.md', 'foo/bar'),
            exp_true='foo/foo/bar, foo/foo/bar/index.md, foo/foo/bar/README.md, foo/foo/bar.md, foo/bar/foo/bar, foo/bar/foo/bar/index.md, foo/bar/foo/bar/README.md, foo/bar/foo/bar.md',
            exp_false='foo/foo/bar, foo/foo/bar/index.md, foo/foo/bar/README.md, foo/foo/bar.md',
        )
        test(
            ('foo/bar.md', 'foo.html'),
            exp_true='foo/foo.html, foo/foo.md, foo/bar/foo.html, foo/bar/foo.md',
            exp_false='foo/foo.html, foo/foo.md',
        )
        test(
            ('foo/bar.md', 'foo/bar.html'),
            exp_true='foo/foo/bar.html, foo/foo/bar.md, foo/bar/foo/bar.html, foo/bar/foo/bar.md',
            exp_false='foo/foo/bar.html, foo/foo/bar.md',
        )
        test(
            ('foo/bar.md', '../foo/bar.html'),
            exp_true='foo/bar.html, foo/bar.md, foo/foo/bar.html, foo/foo/bar.md',
            exp_false='foo/bar.html, foo/bar.md',
        )
        test(
            ('foo/bar.md', '../foo'),
            exp_true='foo, foo/index.md, foo/README.md, foo.md, foo/foo, foo/foo/index.md, foo/foo/README.md, foo/foo.md',
            exp_false='foo, foo/index.md, foo/README.md, foo.md',
        )
        test(
            ('foo/bar.md', '../'),
            exp_true='., index.md, README.md, foo, foo/index.md, foo/README.md',
            exp_false='., index.md, README.md',
        )

        for src in 'foo/bar.md', 'foo.md', 'foo/index.md':
            test((src, '/foo'), expected='foo, foo/index.md, foo/README.md, foo.md')
            test((src, '/foo/bar.md'), expected='foo/bar.md')
            test((src, '/foo/bar.html'), expected='foo/bar.html, foo/bar.md')

        for dest in '', '.', './':
            test(('index.md', dest), expected='., index.md')
            test(('foo/bar.md', dest), expected='foo, foo/bar.md')

        test(
            ('foo/bar.md', '../test.png'),
            exp_true='test.png, test.png.md, foo/test.png, foo/test.png.md',
            exp_false='test.png, test.png.md',
        )

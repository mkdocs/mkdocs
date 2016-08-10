#!/usr/bin/env python
# coding: utf-8

from __future__ import unicode_literals
import os
import shutil
import tempfile
import unittest
import mock

try:
    from itertools import izip as zip
except ImportError:
    # In Py3 use builtin zip function
    pass


from mkdocs import nav, config
from mkdocs.commands import build
from mkdocs.exceptions import MarkdownNotFound
from mkdocs.tests.base import dedent


def load_config(cfg=None):
    """ Helper to build a simple config for testing. """
    cfg = cfg or {}
    if 'site_name' not in cfg:
        cfg['site_name'] = 'Example'
    if 'config_file_path' not in cfg:
        cfg['config_file_path'] = os.path.join(os.path.abspath('.'), 'mkdocs.yml')
    if 'extra_css' not in cfg:
        cfg['extra_css'] = ['css/extra.css']
    conf = config.Config(schema=config.DEFAULT_SCHEMA)
    conf.load_dict(cfg)

    errors_warnings = conf.validate()
    assert(errors_warnings == ([], [])), errors_warnings
    return conf


class BuildTests(unittest.TestCase):

    def test_empty_document(self):
        html, toc, meta = build.convert_markdown("", load_config())

        self.assertEqual(html, '')
        self.assertEqual(len(list(toc)), 0)
        self.assertEqual(meta, {})

    def test_convert_markdown(self):
        """
        Ensure that basic Markdown -> HTML and TOC works.
        """
        html, toc, meta = build.convert_markdown(dedent("""
            page_title: custom title

            # Heading 1

            This is some text.

            # Heading 2

            And some more text.
        """), load_config())

        expected_html = dedent("""
            <h1 id="heading-1">Heading 1</h1>
            <p>This is some text.</p>
            <h1 id="heading-2">Heading 2</h1>
            <p>And some more text.</p>
        """)

        expected_toc = dedent("""
            Heading 1 - #heading-1
            Heading 2 - #heading-2
        """)

        expected_meta = {'page_title': ['custom title']}

        self.assertEqual(html.strip(), expected_html)
        self.assertEqual(str(toc).strip(), expected_toc)
        self.assertEqual(meta, expected_meta)

    def test_convert_internal_link(self):
        md_text = 'An [internal link](internal.md) to another document.'
        expected = '<p>An <a href="internal/">internal link</a> to another document.</p>'
        html, toc, meta = build.convert_markdown(md_text, load_config())
        self.assertEqual(html.strip(), expected.strip())

    def test_convert_multiple_internal_links(self):
        md_text = '[First link](first.md) [second link](second.md).'
        expected = '<p><a href="first/">First link</a> <a href="second/">second link</a>.</p>'
        html, toc, meta = build.convert_markdown(md_text, load_config())
        self.assertEqual(html.strip(), expected.strip())

    def test_convert_internal_link_differing_directory(self):
        md_text = 'An [internal link](../internal.md) to another document.'
        expected = '<p>An <a href="../internal/">internal link</a> to another document.</p>'
        html, toc, meta = build.convert_markdown(md_text, load_config())
        self.assertEqual(html.strip(), expected.strip())

    def test_convert_internal_link_with_anchor(self):
        md_text = 'An [internal link](internal.md#section1.1) to another document.'
        expected = '<p>An <a href="internal/#section1.1">internal link</a> to another document.</p>'
        html, toc, meta = build.convert_markdown(md_text, load_config())
        self.assertEqual(html.strip(), expected.strip())

    def test_convert_internal_media(self):
        """Test relative image URL's are the same for different base_urls"""
        pages = [
            'index.md',
            'internal.md',
            'sub/internal.md',
        ]

        site_navigation = nav.SiteNavigation(pages)

        expected_results = (
            './img/initial-layout.png',
            '../img/initial-layout.png',
            '../img/initial-layout.png',
        )

        template = '<p><img alt="The initial MkDocs layout" src="%s" /></p>'

        for (page, expected) in zip(site_navigation.walk_pages(), expected_results):
            md_text = '![The initial MkDocs layout](img/initial-layout.png)'
            html, _, _ = build.convert_markdown(md_text, load_config(), site_navigation=site_navigation)
            self.assertEqual(html, template % expected)

    def test_convert_internal_asbolute_media(self):
        """Test absolute image URL's are correct for different base_urls"""
        pages = [
            'index.md',
            'internal.md',
            'sub/internal.md',
        ]

        site_navigation = nav.SiteNavigation(pages)

        expected_results = (
            './img/initial-layout.png',
            '../img/initial-layout.png',
            '../../img/initial-layout.png',
        )

        template = '<p><img alt="The initial MkDocs layout" src="%s" /></p>'

        for (page, expected) in zip(site_navigation.walk_pages(), expected_results):
            md_text = '![The initial MkDocs layout](/img/initial-layout.png)'
            html, _, _ = build.convert_markdown(md_text, load_config(), site_navigation=site_navigation)
            self.assertEqual(html, template % expected)

    def test_dont_convert_code_block_urls(self):
        pages = [
            'index.md',
            'internal.md',
            'sub/internal.md',
        ]

        site_navigation = nav.SiteNavigation(pages)

        expected = dedent("""
        <p>An HTML Anchor::</p>
        <pre><code>&lt;a href="index.md"&gt;My example link&lt;/a&gt;
        </code></pre>
        """)

        for page in site_navigation.walk_pages():
            markdown = 'An HTML Anchor::\n\n    <a href="index.md">My example link</a>\n'
            html, _, _ = build.convert_markdown(markdown, load_config(), site_navigation=site_navigation)
            self.assertEqual(dedent(html), expected)

    def test_anchor_only_link(self):
        pages = [
            'index.md',
            'internal.md',
            'sub/internal.md',
        ]

        site_navigation = nav.SiteNavigation(pages)

        for page in site_navigation.walk_pages():
            markdown = '[test](#test)'
            html, _, _ = build.convert_markdown(markdown, load_config(), site_navigation=site_navigation)
            self.assertEqual(html, '<p><a href="#test">test</a></p>')

    def test_ignore_external_link(self):
        md_text = 'An [external link](http://example.com/external.md).'
        expected = '<p>An <a href="http://example.com/external.md">external link</a>.</p>'
        html, toc, meta = build.convert_markdown(md_text, load_config())
        self.assertEqual(html.strip(), expected.strip())

    def test_not_use_directory_urls(self):
        md_text = 'An [internal link](internal.md) to another document.'
        expected = '<p>An <a href="internal/index.html">internal link</a> to another document.</p>'
        pages = [
            'internal.md',
        ]
        site_navigation = nav.SiteNavigation(pages, use_directory_urls=False)
        html, toc, meta = build.convert_markdown(md_text, load_config(), site_navigation=site_navigation)
        self.assertEqual(html.strip(), expected.strip())

    def test_ignore_email_links(self):
        md_text = 'A <autolink@example.com> and an [link](mailto:example@example.com).'
        expected = ''.join([
            '<p>A <a href="&#109;&#97;&#105;&#108;&#116;&#111;&#58;&#97;&#117;&#116;',
            '&#111;&#108;&#105;&#110;&#107;&#64;&#101;&#120;&#97;&#109;&#112;&#108;',
            '&#101;&#46;&#99;&#111;&#109;">&#97;&#117;&#116;&#111;&#108;&#105;&#110;',
            '&#107;&#64;&#101;&#120;&#97;&#109;&#112;&#108;&#101;&#46;&#99;&#111;&#109;',
            '</a> and an <a href="mailto:example@example.com">link</a>.</p>'
        ])
        html, toc, meta = build.convert_markdown(md_text, load_config())
        self.assertEqual(html.strip(), expected.strip())

    def test_markdown_table_extension(self):
        """
        Ensure that the table extension is supported.
        """
        html, toc, meta = build.convert_markdown(dedent("""
        First Header   | Second Header
        -------------- | --------------
        Content Cell 1 | Content Cell 2
        Content Cell 3 | Content Cell 4
        """), load_config())

        expected_html = dedent("""
        <table>
        <thead>
        <tr>
        <th>First Header</th>
        <th>Second Header</th>
        </tr>
        </thead>
        <tbody>
        <tr>
        <td>Content Cell 1</td>
        <td>Content Cell 2</td>
        </tr>
        <tr>
        <td>Content Cell 3</td>
        <td>Content Cell 4</td>
        </tr>
        </tbody>
        </table>
        """)

        self.assertEqual(html.strip(), expected_html)

    def test_markdown_fenced_code_extension(self):
        """
        Ensure that the fenced code extension is supported.
        """
        html, toc, meta = build.convert_markdown(dedent("""
        ```
        print 'foo'
        ```
        """), load_config())

        expected_html = dedent("""
        <pre><code>print 'foo'\n</code></pre>
        """)

        self.assertEqual(html.strip(), expected_html)

    def test_markdown_custom_extension(self):
        """
        Check that an extension applies when requested in the arguments to
        `convert_markdown`.
        """
        md_input = "foo__bar__baz"

        # Check that the plugin is not active when not requested.
        expected_without_smartstrong = "<p>foo<strong>bar</strong>baz</p>"
        html_base, _, _ = build.convert_markdown(md_input, load_config())
        self.assertEqual(html_base.strip(), expected_without_smartstrong)

        # Check that the plugin is active when requested.
        cfg = load_config({
            'markdown_extensions': ['smart_strong']
        })
        expected_with_smartstrong = "<p>foo__bar__baz</p>"
        html_ext, _, _ = build.convert_markdown(md_input, cfg)
        self.assertEqual(html_ext.strip(), expected_with_smartstrong)

    def test_markdown_duplicate_custom_extension(self):
        """
        Duplicated extension names should not cause problems.
        """
        cfg = load_config({
            'markdown_extensions': ['toc']
        })
        md_input = "foo"
        html_ext, _, _ = build.convert_markdown(md_input, cfg)
        self.assertEqual(html_ext.strip(), '<p>foo</p>')

    def test_copying_media(self):
        docs_dir = tempfile.mkdtemp()
        site_dir = tempfile.mkdtemp()
        try:
            # Create a non-empty markdown file, image, html file, dot file and dot directory.
            f = open(os.path.join(docs_dir, 'index.md'), 'w')
            f.write(dedent("""
                page_title: custom title

                # Heading 1

                This is some text.

                # Heading 2

                And some more text.
            """))
            f.close()
            open(os.path.join(docs_dir, 'img.jpg'), 'w').close()
            open(os.path.join(docs_dir, 'example.html'), 'w').close()
            open(os.path.join(docs_dir, '.hidden'), 'w').close()
            os.mkdir(os.path.join(docs_dir, '.git'))
            open(os.path.join(docs_dir, '.git/hidden'), 'w').close()

            cfg = load_config({
                'docs_dir': docs_dir,
                'site_dir': site_dir
            })
            build.build(cfg)

            # Verify only the markdown (coverted to html) and the image are copied.
            self.assertTrue(os.path.isfile(os.path.join(site_dir, 'index.html')))
            self.assertTrue(os.path.isfile(os.path.join(site_dir, 'img.jpg')))
            self.assertTrue(os.path.isfile(os.path.join(site_dir, 'example.html')))
            self.assertFalse(os.path.isfile(os.path.join(site_dir, '.hidden')))
            self.assertFalse(os.path.isfile(os.path.join(site_dir, '.git/hidden')))
        finally:
            shutil.rmtree(docs_dir)
            shutil.rmtree(site_dir)

    def test_copy_theme_files(self):
        docs_dir = tempfile.mkdtemp()
        site_dir = tempfile.mkdtemp()
        try:
            # Create a non-empty markdown file.
            f = open(os.path.join(docs_dir, 'index.md'), 'w')
            f.write(dedent("""
                page_title: custom title

                # Heading 1

                This is some text.
            """))
            f.close()

            cfg = load_config({
                'docs_dir': docs_dir,
                'site_dir': site_dir
            })
            build.build(cfg)

            # Verify only theme media are copied, not templates or Python files.
            self.assertTrue(os.path.isfile(os.path.join(site_dir, 'index.html')))
            self.assertTrue(os.path.isdir(os.path.join(site_dir, 'js')))
            self.assertTrue(os.path.isdir(os.path.join(site_dir, 'css')))
            self.assertTrue(os.path.isdir(os.path.join(site_dir, 'img')))
            self.assertFalse(os.path.isfile(os.path.join(site_dir, '__init__.py')))
            self.assertFalse(os.path.isfile(os.path.join(site_dir, '__init__.pyc')))
            self.assertFalse(os.path.isfile(os.path.join(site_dir, 'base.html')))
            self.assertFalse(os.path.isfile(os.path.join(site_dir, 'content.html')))
            self.assertFalse(os.path.isfile(os.path.join(site_dir, 'nav.html')))
        finally:
            shutil.rmtree(docs_dir)
            shutil.rmtree(site_dir)

    def test_strict_mode_valid(self):
        pages = [
            'index.md',
            'internal.md',
            'sub/internal.md',
        ]
        site_nav = nav.SiteNavigation(pages)

        valid = "[test](internal.md)"
        build.convert_markdown(valid, load_config({'strict': False}), site_nav)
        build.convert_markdown(valid, load_config({'strict': True}), site_nav)

    def test_strict_mode_invalid(self):
        pages = [
            'index.md',
            'internal.md',
            'sub/internal.md',
        ]
        site_nav = nav.SiteNavigation(pages)

        invalid = "[test](bad_link.md)"
        build.convert_markdown(invalid, load_config({'strict': False}), site_nav)

        self.assertRaises(
            MarkdownNotFound,
            build.convert_markdown, invalid, load_config({'strict': True}), site_nav)

    def test_absolute_link(self):
        pages = [
            'index.md',
            'sub/index.md',
        ]
        site_nav = nav.SiteNavigation(pages)

        markdown = "[test 1](/index.md) [test 2](/sub/index.md)"
        cfg = load_config({'strict': True})
        build.convert_markdown(markdown, cfg, site_nav)

    def test_extension_config(self):
        """
        Test that a dictionary of 'markdown_extensions' is recognized as
        both a list of extensions and a dictionary of extnesion configs.
        """
        cfg = load_config({
            'markdown_extensions': [{'toc': {'permalink': True}}]
        })

        html, toc, meta = build.convert_markdown(dedent("""
        # A Header
        """), cfg)

        expected_html = dedent("""
        <h1 id="a-header">A Header<a class="headerlink" href="#a-header" title="Permanent link">&para;</a></h1>
        """)

        self.assertEqual(html.strip(), expected_html)

    def test_extra_context(self):

        # Same as the default schema, but don't verify the docs_dir exists.
        cfg = load_config({
            'site_name': "Site",
            'extra': {
                'a': 1
            }
        })

        context = build.get_global_context(mock.Mock(), cfg)

        self.assertEqual(context['config']['extra']['a'], 1)

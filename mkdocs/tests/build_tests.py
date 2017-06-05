#!/usr/bin/env python
# coding: utf-8

from __future__ import unicode_literals
import os
import shutil
import tempfile
import unittest
import mock
import io

try:
    from itertools import izip as zip
except ImportError:
    # In Py3 use builtin zip function
    pass


from mkdocs import nav
from mkdocs.commands import build
from mkdocs.exceptions import MarkdownNotFound
from mkdocs.tests.base import dedent, load_config
from mkdocs.utils import meta


def build_page(title, path, config, md_src=None):
    """ Helper which returns a Page object. """

    sitenav = nav.SiteNavigation(config)
    page = nav.Page(title, path, sitenav.url_context, config)
    if md_src:
        # Fake page.read_source()
        page.markdown, page.meta = meta.get_data(md_src)
    return page, sitenav


class BuildTests(unittest.TestCase):

    def test_empty_document(self):
        config = load_config(pages=[{'Home': 'index.md'}])
        page, nav = build_page(None, 'index.md', config)
        page.render(config, nav)

        self.assertEqual(page.content, '')
        self.assertEqual(len(list(page.toc)), 0)
        self.assertEqual(page.meta, {})
        self.assertEqual(page.title, 'Home')

    def test_convert_markdown(self):
        """
        Ensure that basic Markdown -> HTML and TOC works.
        """
        md_text = dedent("""
            title: custom title

            # Heading 1

            This is some text.

            # Heading 2

            And some more text.
        """)

        config = load_config(pages=[{'Home': 'index.md'}])
        page, nav = build_page(None, 'index.md', config, md_text)
        page.render(config, nav)

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

        expected_meta = {'title': 'custom title'}

        self.assertEqual(page.content.strip(), expected_html)
        self.assertEqual(str(page.toc).strip(), expected_toc)
        self.assertEqual(page.meta, expected_meta)
        self.assertEqual(page.title, 'custom title')

    def test_convert_internal_link(self):
        md_text = 'An [internal link](internal.md) to another document.'
        expected = '<p>An <a href="internal/">internal link</a> to another document.</p>'
        config = load_config(pages=['index.md', 'internal.md'])
        page, nav = build_page(None, 'index.md', config, md_text)
        page.render(config, nav)
        self.assertEqual(page.content.strip(), expected.strip())

    def test_convert_multiple_internal_links(self):
        md_text = '[First link](first.md) [second link](second.md).'
        expected = '<p><a href="first/">First link</a> <a href="second/">second link</a>.</p>'
        config = load_config(pages=['index.md', 'first.md', 'second.md'])
        page, nav = build_page(None, 'index.md', config, md_text)
        page.render(config, nav)
        self.assertEqual(page.content.strip(), expected.strip())

    def test_convert_internal_link_differing_directory(self):
        md_text = 'An [internal link](../internal.md) to another document.'
        expected = '<p>An <a href="../internal/">internal link</a> to another document.</p>'
        config = load_config(pages=['foo/bar.md', 'internal.md'])
        page, nav = build_page(None, 'foo/bar.md', config, md_text)
        page.render(config)
        self.assertEqual(page.content.strip(), expected.strip())

    def test_convert_internal_link_with_anchor(self):
        md_text = 'An [internal link](internal.md#section1.1) to another document.'
        expected = '<p>An <a href="internal/#section1.1">internal link</a> to another document.</p>'
        config = load_config(pages=['index.md', 'internal.md'])
        page, nav = build_page(None, 'index.md', config, md_text)
        page.render(config, nav)
        self.assertEqual(page.content.strip(), expected.strip())

    def test_convert_internal_media(self):
        """Test relative image URL's are the same for different base_urls"""
        pages = [
            'index.md',
            'internal.md',
            'sub/internal.md',
        ]

        config = load_config(pages=pages)
        site_navigation = nav.SiteNavigation(config)

        expected_results = (
            './img/initial-layout.png',
            '../img/initial-layout.png',
            '../img/initial-layout.png',
        )

        template = '<p><img alt="The initial MkDocs layout" src="%s" /></p>'

        for (page, expected) in zip(site_navigation.walk_pages(), expected_results):
            page.markdown = '![The initial MkDocs layout](img/initial-layout.png)'
            page.render(config, site_navigation)
            self.assertEqual(page.content, template % expected)

    def test_convert_internal_asbolute_media(self):
        """Test absolute image URL's are correct for different base_urls"""
        pages = [
            'index.md',
            'internal.md',
            'sub/internal.md',
        ]

        config = load_config(pages=pages)
        site_navigation = nav.SiteNavigation(config)

        expected_results = (
            './img/initial-layout.png',
            '../img/initial-layout.png',
            '../../img/initial-layout.png',
        )

        template = '<p><img alt="The initial MkDocs layout" src="%s" /></p>'

        for (page, expected) in zip(site_navigation.walk_pages(), expected_results):
            page.markdown = '![The initial MkDocs layout](/img/initial-layout.png)'
            page.render(config, site_navigation)
            self.assertEqual(page.content, template % expected)

    def test_dont_convert_code_block_urls(self):
        pages = [
            'index.md',
            'internal.md',
            'sub/internal.md',
        ]

        config = load_config(pages=pages)
        site_navigation = nav.SiteNavigation(config)

        expected = dedent("""
        <p>An HTML Anchor::</p>
        <pre><code>&lt;a href="index.md"&gt;My example link&lt;/a&gt;
        </code></pre>
        """)

        for page in site_navigation.walk_pages():
            page.markdown = 'An HTML Anchor::\n\n    <a href="index.md">My example link</a>\n'
            page.render(config, site_navigation)
            self.assertEqual(page.content, expected)

    def test_anchor_only_link(self):
        pages = [
            'index.md',
            'internal.md',
            'sub/internal.md',
        ]

        config = load_config(pages=pages)
        site_navigation = nav.SiteNavigation(config)

        for page in site_navigation.walk_pages():
            page.markdown = '[test](#test)'
            page.render(config, site_navigation)
            self.assertEqual(page.content, '<p><a href="#test">test</a></p>')

    def test_ignore_external_link(self):
        md_text = 'An [external link](http://example.com/external.md).'
        expected = '<p>An <a href="http://example.com/external.md">external link</a>.</p>'
        config = load_config(pages=[{'Home': 'index.md'}])
        page, nav = build_page(None, 'index.md', config, md_text)
        page.render(config, nav)
        self.assertEqual(page.content.strip(), expected.strip())

    def test_not_use_directory_urls(self):
        md_text = 'An [internal link](internal.md) to another document.'
        expected = '<p>An <a href="internal/index.html">internal link</a> to another document.</p>'
        config = load_config(pages=['index.md', 'internal.md'], use_directory_urls=False)
        page, nav = build_page(None, 'index.md', config, md_text)
        page.render(config, nav)
        self.assertEqual(page.content.strip(), expected.strip())

    def test_ignore_email_links(self):
        md_text = 'A <autolink@example.com> and an [link](mailto:example@example.com).'
        expected = ''.join([
            '<p>A <a href="&#109;&#97;&#105;&#108;&#116;&#111;&#58;&#97;&#117;&#116;',
            '&#111;&#108;&#105;&#110;&#107;&#64;&#101;&#120;&#97;&#109;&#112;&#108;',
            '&#101;&#46;&#99;&#111;&#109;">&#97;&#117;&#116;&#111;&#108;&#105;&#110;',
            '&#107;&#64;&#101;&#120;&#97;&#109;&#112;&#108;&#101;&#46;&#99;&#111;&#109;',
            '</a> and an <a href="mailto:example@example.com">link</a>.</p>'
        ])
        config = load_config(pages=[{'Home': 'index.md'}])
        page, nav = build_page(None, 'index.md', config, md_text)
        page.render(config, nav)
        self.assertEqual(page.content.strip(), expected.strip())

    def test_markdown_table_extension(self):
        """
        Ensure that the table extension is supported.
        """
        md_text = dedent("""
        First Header   | Second Header
        -------------- | --------------
        Content Cell 1 | Content Cell 2
        Content Cell 3 | Content Cell 4
        """)

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

        config = load_config(pages=[{'Home': 'index.md'}])
        page, nav = build_page(None, 'index.md', config, md_text)
        page.render(config, nav)
        self.assertEqual(page.content.strip(), expected_html)

    def test_markdown_fenced_code_extension(self):
        """
        Ensure that the fenced code extension is supported.
        """
        md_text = dedent("""
        ```
        print 'foo'
        ```
        """)

        expected_html = dedent("""
        <pre><code>print 'foo'\n</code></pre>
        """)

        config = load_config(pages=[{'Home': 'index.md'}])
        page, nav = build_page(None, 'index.md', config, md_text)
        page.render(config, nav)
        self.assertEqual(page.content.strip(), expected_html)

    def test_markdown_custom_extension(self):
        """
        Check that an extension applies when requested in the arguments to
        `convert_markdown`.
        """
        md_text = "foo__bar__baz"

        # Check that the plugin is not active when not requested.
        expected_without_smartstrong = "<p>foo<strong>bar</strong>baz</p>"
        config = load_config(pages=[{'Home': 'index.md'}])
        page, nav = build_page(None, 'index.md', config, md_text)
        page.render(config, nav)
        self.assertEqual(page.content.strip(), expected_without_smartstrong)

        # Check that the plugin is active when requested.
        expected_with_smartstrong = "<p>foo__bar__baz</p>"
        config = load_config(pages=[{'Home': 'index.md'}], markdown_extensions=['smart_strong'])
        page, nav = build_page(None, 'index.md', config, md_text)
        page.render(config, nav)
        self.assertEqual(page.content.strip(), expected_with_smartstrong)

    def test_markdown_duplicate_custom_extension(self):
        """
        Duplicated extension names should not cause problems.
        """
        md_text = "foo"
        config = load_config(pages=[{'Home': 'index.md'}], markdown_extensions=['toc'])
        page, nav = build_page(None, 'index.md', config, md_text)
        page.render(config, nav)
        self.assertEqual(page.content.strip(), '<p>foo</p>')

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

            cfg = load_config(docs_dir=docs_dir, site_dir=site_dir)
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

            cfg = load_config(docs_dir=docs_dir, site_dir=site_dir)
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

        md_text = "[test](internal.md)"

        config = load_config(pages=pages, strict=False)
        page, nav = build_page(None, 'index.md', config, md_text)
        page.render(config, nav)

        config = load_config(pages=pages, strict=True)
        page, nav = build_page(None, 'index.md', config, md_text)
        page.render(config, nav)

    def test_strict_mode_invalid(self):
        pages = [
            'index.md',
            'internal.md',
            'sub/internal.md',
        ]

        md_text = "[test](bad_link.md)"

        config = load_config(pages=pages, strict=False)
        page, nav = build_page(None, 'index.md', config, md_text)
        page.render(config, nav)

        config = load_config(pages=pages, strict=True)
        page, nav = build_page(None, 'index.md', config, md_text)
        self.assertRaises(
            MarkdownNotFound,
            page.render, config, nav)

    def test_absolute_link(self):
        pages = [
            'index.md',
            'sub/index.md',
        ]

        md_text = "[test 1](/index.md) [test 2](/sub/index.md)"
        config = load_config(pages=pages, strict=True)
        page, nav = build_page(None, 'index.md', config, md_text)
        page.render(config, nav)

    def test_extension_config(self):
        """
        Test that a dictionary of 'markdown_extensions' is recognized as
        both a list of extensions and a dictionary of extnesion configs.
        """
        md_text = dedent("""
        # A Header
        """)

        expected_html = dedent("""
        <h1 id="a-header">A Header<a class="headerlink" href="#a-header" title="Permanent link">&para;</a></h1>
        """)

        config = load_config(pages=[{'Home': 'index.md'}], markdown_extensions=[{'toc': {'permalink': True}}])
        page, nav = build_page(None, 'index.md', config, md_text)
        page.render(config, nav)
        self.assertEqual(page.content.strip(), expected_html)

    def test_extra_context(self):

        # Same as the default schema, but don't verify the docs_dir exists.
        cfg = load_config(
            site_name="Site",
            extra={
                'a': 1
            }
        )

        context = build.get_context(mock.Mock(), cfg)

        self.assertEqual(context['config']['extra']['a'], 1)

    def test_BOM(self):
        docs_dir = tempfile.mkdtemp()
        site_dir = tempfile.mkdtemp()
        try:
            # Create an UTF-8 Encoded file with BOM (as Micorsoft editors do). See #1186.
            f = io.open(os.path.join(docs_dir, 'index.md'), 'w', encoding='utf-8-sig')
            f.write('# An UTF-8 encoded file with a BOM')
            f.close()

            cfg = load_config(
                docs_dir=docs_dir,
                site_dir=site_dir
            )
            build.build(cfg)

            # Verify that the file was generated properly.
            # If the BOM is not removed, Markdown will return:
            # `<p>\ufeff# An UTF-8 encoded file with a BOM</p>`.
            f = io.open(os.path.join(site_dir, 'index.html'), 'r', encoding='utf-8')
            output = f.read()
            f.close()
            self.assertTrue(
                '<h1 id="an-utf-8-encoded-file-with-a-bom">An UTF-8 encoded file with a BOM</h1>' in output
            )

        finally:
            shutil.rmtree(docs_dir)
            shutil.rmtree(site_dir)

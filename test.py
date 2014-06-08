#!/usr/bin/env python
# coding: utf-8

from mkdocs import build, nav, toc, utils, config
import markdown
import os
import shutil
import textwrap
import tempfile
import unittest


def dedent(text):
    return textwrap.dedent(text).strip()


class ConfigTests(unittest.TestCase):
    def test_config_option(self):
        """
        Users can explicitly set the config file using the '--config' option.
        Allows users to specify a config other than the default `mkdocs.yml`.
        """
        expected_results = {
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
        config_file = tempfile.NamedTemporaryFile()
        config_file.write(file_contents)
        config_file.flush()
        options = {'config': config_file.name}
        results = config.load_config(options=options)
        self.assertEqual(results['site_name'], expected_results['site_name'])
        self.assertEqual(results['pages'], expected_results['pages'])

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


class TableOfContentsTests(unittest.TestCase):
    def markdown_to_toc(self, markdown_source):
        markdown_source = toc.pre_process(markdown_source)
        md = markdown.Markdown(extensions=['toc'])
        html_output = md.convert(markdown_source)
        html_output, toc_output = toc.post_process(html_output)
        return toc.TableOfContents(toc_output)

    def test_indented_toc(self):
        md = dedent("""
        # Heading 1
        ## Heading 2
        ### Heading 3
        """)
        expected = dedent("""
        Heading 1 - #heading-1
            Heading 2 - #heading-2
                Heading 3 - #heading-3
        """)
        toc = self.markdown_to_toc(md)
        self.assertEqual(str(toc).strip(), expected)

    def test_flat_toc(self):
        md = dedent("""
        # Heading 1
        # Heading 2
        # Heading 3
        """)
        expected = dedent("""
        Heading 1 - #heading-1
        Heading 2 - #heading-2
        Heading 3 - #heading-3
        """)
        toc = self.markdown_to_toc(md)
        self.assertEqual(str(toc).strip(), expected)

    def test_flat_h2_toc(self):
        md = dedent("""
        ## Heading 1
        ## Heading 2
        ## Heading 3
        """)
        expected = dedent("""
        Heading 1 - #heading-1
        Heading 2 - #heading-2
        Heading 3 - #heading-3
        """)
        toc = self.markdown_to_toc(md)
        self.assertEqual(str(toc).strip(), expected)

    def test_mixed_toc(self):
        md = dedent("""
        # Heading 1
        ## Heading 2
        # Heading 3
        ### Heading 4
        ### Heading 5
        """)
        expected = dedent("""
        Heading 1 - #heading-1
            Heading 2 - #heading-2
        Heading 3 - #heading-3
            Heading 4 - #heading-4
            Heading 5 - #heading-5
        """)
        toc = self.markdown_to_toc(md)
        self.assertEqual(str(toc).strip(), expected)


class SiteNavigationTests(unittest.TestCase):
    def test_simple_toc(self):
        pages = [
            ('index.md', 'Home'),
            ('about.md', 'About')
        ]
        expected = dedent("""
        Home - /
        About - /about/
        """)
        site_navigation = nav.SiteNavigation(pages)
        self.assertEqual(str(site_navigation).strip(), expected)
        self.assertEqual(len(site_navigation.nav_items), 2)
        self.assertEqual(len(site_navigation.pages), 2)

    def test_empty_toc_item(self):
        pages = [
            ('index.md',),
            ('about.md', 'About')
        ]
        expected = dedent("""
        About - /about/
        """)
        site_navigation = nav.SiteNavigation(pages)
        self.assertEqual(str(site_navigation).strip(), expected)
        self.assertEqual(len(site_navigation.nav_items), 1)
        self.assertEqual(len(site_navigation.pages), 2)

    def test_indented_toc(self):
        pages = [
            ('index.md', 'Home'),
            ('api-guide/running.md', 'API Guide', 'Running'),
            ('api-guide/testing.md', 'API Guide', 'Testing'),
            ('api-guide/debugging.md', 'API Guide', 'Debugging'),
            ('about/release-notes.md', 'About', 'Release notes'),
            ('about/license.md', 'About', 'License')
        ]
        expected = dedent("""
        Home - /
        API Guide
            Running - /api-guide/running/
            Testing - /api-guide/testing/
            Debugging - /api-guide/debugging/
        About
            Release notes - /about/release-notes/
            License - /about/license/
        """)
        site_navigation = nav.SiteNavigation(pages)
        self.assertEqual(str(site_navigation).strip(), expected)
        self.assertEqual(len(site_navigation.nav_items), 3)
        self.assertEqual(len(site_navigation.pages), 6)

    def test_walk_simple_toc(self):
        pages = [
            ('index.md', 'Home'),
            ('about.md', 'About')
        ]
        expected = [
            dedent("""
                Home - / [*]
                About - /about/
            """),
            dedent("""
                Home - /
                About - /about/ [*]
            """)
        ]
        site_navigation = nav.SiteNavigation(pages)
        for index, page in enumerate(site_navigation.walk_pages()):
            self.assertEqual(str(site_navigation).strip(), expected[index])

    def test_walk_empty_toc(self):
        pages = [
            ('index.md',),
            ('about.md', 'About')
        ]
        expected = [
            dedent("""
                About - /about/
            """),
            dedent("""
                About - /about/ [*]
            """)
        ]
        site_navigation = nav.SiteNavigation(pages)
        for index, page in enumerate(site_navigation.walk_pages()):
            self.assertEqual(str(site_navigation).strip(), expected[index])

    def test_walk_indented_toc(self):
        pages = [
            ('index.md', 'Home'),
            ('api-guide/running.md', 'API Guide', 'Running'),
            ('api-guide/testing.md', 'API Guide', 'Testing'),
            ('api-guide/debugging.md', 'API Guide', 'Debugging'),
            ('about/release-notes.md', 'About', 'Release notes'),
            ('about/license.md', 'About', 'License')
        ]
        expected = [
            dedent("""
                Home - / [*]
                API Guide
                    Running - /api-guide/running/
                    Testing - /api-guide/testing/
                    Debugging - /api-guide/debugging/
                About
                    Release notes - /about/release-notes/
                    License - /about/license/
            """),
            dedent("""
                Home - /
                API Guide [*]
                    Running - /api-guide/running/ [*]
                    Testing - /api-guide/testing/
                    Debugging - /api-guide/debugging/
                About
                    Release notes - /about/release-notes/
                    License - /about/license/
            """),
            dedent("""
                Home - /
                API Guide [*]
                    Running - /api-guide/running/
                    Testing - /api-guide/testing/ [*]
                    Debugging - /api-guide/debugging/
                About
                    Release notes - /about/release-notes/
                    License - /about/license/
            """),
            dedent("""
                Home - /
                API Guide [*]
                    Running - /api-guide/running/
                    Testing - /api-guide/testing/
                    Debugging - /api-guide/debugging/ [*]
                About
                    Release notes - /about/release-notes/
                    License - /about/license/
            """),
            dedent("""
                Home - /
                API Guide
                    Running - /api-guide/running/
                    Testing - /api-guide/testing/
                    Debugging - /api-guide/debugging/
                About [*]
                    Release notes - /about/release-notes/ [*]
                    License - /about/license/
            """),
            dedent("""
                Home - /
                API Guide
                    Running - /api-guide/running/
                    Testing - /api-guide/testing/
                    Debugging - /api-guide/debugging/
                About [*]
                    Release notes - /about/release-notes/
                    License - /about/license/ [*]
            """)
        ]
        site_navigation = nav.SiteNavigation(pages)
        for index, page in enumerate(site_navigation.walk_pages()):
            self.assertEqual(str(site_navigation).strip(), expected[index])


class BuildTests(unittest.TestCase):
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
        """))

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
        html, toc, meta = build.convert_markdown(md_text)
        html = build.post_process_html(html)
        self.assertEqual(html.strip(), expected.strip())

    def test_convert_multiple_internal_links(self):
        md_text = '[First link](first.md) [second link](second.md).'
        expected = '<p><a href="first/">First link</a> <a href="second/">second link</a>.</p>'
        html, toc, meta = build.convert_markdown(md_text)
        html = build.post_process_html(html)
        self.assertEqual(html.strip(), expected.strip())

    def test_convert_internal_link_differing_directory(self):
        md_text = 'An [internal link](../internal.md) to another document.'
        expected = '<p>An <a href="../internal/">internal link</a> to another document.</p>'
        html, toc, meta = build.convert_markdown(md_text)
        html = build.post_process_html(html)
        self.assertEqual(html.strip(), expected.strip())

    def test_convert_internal_link_with_anchor(self):
        md_text = 'An [internal link](internal.md#section1.1) to another document.'
        expected = '<p>An <a href="internal/#section1.1">internal link</a> to another document.</p>'
        html, toc, meta = build.convert_markdown(md_text)
        html = build.post_process_html(html)
        self.assertEqual(html.strip(), expected.strip())

    def test_ignore_external_link(self):
        md_text = 'An [external link](http://example.com/external.md).'
        expected = '<p>An <a href="http://example.com/external.md">external link</a>.</p>'
        html, toc, meta = build.convert_markdown(md_text)
        html = build.post_process_html(html)
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
        """))

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
        """))

        expected_html = dedent("""
        <pre><code>print 'foo'\n</code></pre>
        """)

        self.assertEqual(html.strip(), expected_html)

# class IntegrationTests(unittest.TestCase):
#     def test_mkdocs_site(self):
#         """
#         Build the MkDocs site itself, as an integration test.
#         Check that all the resulting HTML pages actually exist.
#         """
#         tmp_dir = tempfile.mkdtemp()
#         try:
#             conf = config.load_config(options={'site_dir': tmp_dir})
#             build.build(conf)
#             for page in conf['pages']:
#                 html_path = utils.get_html_path(page[0])
#                 filename = os.path.join(tmp_dir, html_path)
#                 self.assertTrue(os.path.exists(filename))
#         finally:
#             shutil.rmtree(tmp_dir)


if __name__ == '__main__':
    unittest.main()

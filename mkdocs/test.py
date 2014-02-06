#!/usr/bin/env python
# coding: utf-8

from mkdocs import build, nav, toc, utils, config
import markdown
import textwrap
import tempfile
import os
import unittest


def dedent(text):
    return textwrap.dedent(text).strip()

class ConfigTests(unittest.TestCase):
    def test_config_option(self):
        expected_results = {
             'site_name': 'UnitTest',
             'site_description': 'unittest for mkdocs.',
             'site_dir': 'site',
             'docs_dir': 'docs',
             'site_url': 'http://www.unittest.org/',
             'dev_addr': '127.0.0.1:8000',
             'theme': 'bootstrap',
             'site_author': None,
             'use_direcory_urls': True,
             'site_favicon': None,
             'config': None,
             'pages': [['windex.md', 'Introduction'],
                       ['user-guide/writing-your-tests.md', 'User Guide', 'Writing your tests'],
                       ['about/splicense.md', 'About', 'Splicense']],
             'theme_dir': 'theme'
        }
        file_contents = ["site_name: UnitTest\n",
                         "site_url: http://www.unittest.org/\n",
                         "site_description: unittest for mkdocs.\n",
                         "\n",
                         "pages:\n",
                         "- ['windex.md', 'Introduction']\n",
                         "- ['user-guide/writing-your-tests.md', 'User Guide', 'Writing your tests']\n",
                         "- ['about/splicense.md', 'About', 'Splicense']\n",
                         "\n",
                         "theme_dir: 'theme'\n"]
        fd, file_path = tempfile.mkstemp(text=True)
        expected_results['config'] = file_path
        file = open(file_path, 'a')
        for i in file_contents:
            file.write(i)
        file.close()
        os.close(fd)
        options = {'config': file_path}
        results = config.load_config(options=options)
        self.assertEqual(results, expected_results)
        os.remove(file_path)


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

    def test_indented_toc(self):
        pages = [
            ('index.md', 'Home'),
            ('api-guide/running.md', 'API Guide / Running'),
            ('api-guide/testing.md', 'API Guide / Testing'),
            ('api-guide/debugging.md', 'API Guide / Debugging'),
            ('about/release-notes.md', 'About / Release notes'),
            ('about/license.md', 'About / License')
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

    def test_walk_indented_toc(self):
        pages = [
            ('index.md', 'Home'),
            ('api-guide/running.md', 'API Guide / Running'),
            ('api-guide/testing.md', 'API Guide / Testing'),
            ('api-guide/debugging.md', 'API Guide / Debugging'),
            ('about/release-notes.md', 'About / Release notes'),
            ('about/license.md', 'About / License')
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

if __name__ == '__main__':
    unittest.main()

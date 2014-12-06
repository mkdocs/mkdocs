#!/usr/bin/env python
# coding: utf-8


from mkdocs import build, config, main, nav, search, toc, utils
from mkdocs.compat import PY2, zip
from mkdocs.exceptions import ConfigurationError, MarkdownNotFound
import logging
import markdown
import mock
import os
import shutil
import tempfile
import textwrap
import unittest


def dedent(text):
    return textwrap.dedent(text).strip()


def ensure_utf(string):
    return string.encode('utf-8') if PY2 else string


def strip_whitespace(string):
    return string.replace("\n", "").replace(" ", "")


class MainTests(unittest.TestCase):
    def test_arg_to_option(self):
        """
        Check that we parse parameters passed to mkdocs properly
        """
        arg, option = main.arg_to_option('--site-dir=dir')
        self.assertEqual('site_dir', arg)
        self.assertEqual('dir', option)
        arg, option = main.arg_to_option('--site-dir=dir-name')
        self.assertEqual('site_dir', arg)
        self.assertEqual('dir-name', option)
        arg, option = main.arg_to_option('--site-dir=dir=name')
        self.assertEqual('site_dir', arg)
        self.assertEqual('dir=name', option)
        arg, option = main.arg_to_option('--use_directory_urls')
        self.assertEqual('use_directory_urls', arg)
        self.assertEqual(True, option)

    def test_configure_logging(self):
        """
        Check that logging is configured correctly
        """
        logger = logging.getLogger('mkdocs')
        main.configure_logging({})
        self.assertEqual(logging.WARNING, logger.level)
        main.configure_logging({'verbose': True})
        self.assertEqual(logging.DEBUG, logger.level)


class ConfigTests(unittest.TestCase):
    def test_missing_config_file(self):

        def load_missing_config():
            options = {'config': 'bad_filename.yaml'}
            config.load_config(options=options)
        self.assertRaises(ConfigurationError, load_missing_config)

    def test_missing_site_name(self):
        def load_missing_site_name():
            config.validate_config({})
        self.assertRaises(ConfigurationError, load_missing_site_name)

    def test_empty_config(self):
        def load_empty_config():
            config.load_config(filename='/dev/null')
        self.assertRaises(ConfigurationError, load_empty_config)

    def test_config_option(self):
        """
        Users can explicitly set the config file using the '--config' option.
        Allows users to specify a config other than the default `mkdocs.yml`.
        """
        expected_result = {
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
        config_file = tempfile.NamedTemporaryFile('w', delete=False)
        try:
            config_file.write(ensure_utf(file_contents))
            config_file.flush()
            options = {'config': config_file.name}
            result = config.load_config(options=options)
            self.assertEqual(result['site_name'], expected_result['site_name'])
            self.assertEqual(result['pages'], expected_result['pages'])
            config_file.close()
        finally:
            os.remove(config_file.name)

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


def _markdown_to_toc(markdown_source):
    markdown_source = toc.pre_process(markdown_source)
    md = markdown.Markdown(extensions=['toc'])
    html_output = md.convert(markdown_source)
    html_output, toc_output = toc.post_process(html_output)
    return toc.TableOfContents(toc_output)


class TableOfContentsTests(unittest.TestCase):
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
        toc = _markdown_to_toc(md)
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
        toc = _markdown_to_toc(md)
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
        toc = _markdown_to_toc(md)
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
        toc = _markdown_to_toc(md)
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

    def test_base_url(self):
        pages = [
            ('index.md',)
        ]
        site_navigation = nav.SiteNavigation(pages, use_directory_urls=False)
        base_url = site_navigation.url_context.make_relative('/')
        self.assertEqual(base_url, '.')

    def test_generate_site_navigation(self):
        """
        Verify inferring page titles based on the filename
        """

        pages = [
            ('index.md', ),
            ('api-guide/running.md', ),
            ('about/notes.md', ),
            ('about/sub/license.md', ),
        ]

        url_context = nav.URLContext()
        nav_items, pages = nav._generate_site_navigation(pages, url_context)

        self.assertEqual([n.title for n in nav_items],
                         ['Home', 'Api guide', 'About'])
        self.assertEqual([p.title for p in pages],
                         ['Home', 'Running', 'Notes', 'License'])

    @mock.patch.object(os.path, 'sep', '\\')
    def test_generate_site_navigation_windows(self):
        """
        Verify inferring page titles based on the filename with a windows path
        """
        pages = [
            ('index.md', ),
            ('api-guide\\running.md', ),
            ('about\\notes.md', ),
            ('about\\sub\\license.md', ),
        ]

        url_context = nav.URLContext()
        nav_items, pages = nav._generate_site_navigation(pages, url_context)

        self.assertEqual([n.title for n in nav_items],
                         ['Home', 'Api guide', 'About'])
        self.assertEqual([p.title for p in pages],
                         ['Home', 'Running', 'Notes', 'License'])

    def test_invalid_pages_config(self):

        bad_pages = [
            (),  # too short
            ('this', 'is', 'too', 'long'),
        ]

        for bad_page in bad_pages:

            def _test():
                return nav._generate_site_navigation((bad_page, ), None)

            self.assertRaises(ConfigurationError, _test)


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
        self.assertEqual(html.strip(), expected.strip())

    def test_convert_multiple_internal_links(self):
        md_text = '[First link](first.md) [second link](second.md).'
        expected = '<p><a href="first/">First link</a> <a href="second/">second link</a>.</p>'
        html, toc, meta = build.convert_markdown(md_text)
        self.assertEqual(html.strip(), expected.strip())

    def test_convert_internal_link_differing_directory(self):
        md_text = 'An [internal link](../internal.md) to another document.'
        expected = '<p>An <a href="../internal/">internal link</a> to another document.</p>'
        html, toc, meta = build.convert_markdown(md_text)
        self.assertEqual(html.strip(), expected.strip())

    def test_convert_internal_link_with_anchor(self):
        md_text = 'An [internal link](internal.md#section1.1) to another document.'
        expected = '<p>An <a href="internal/#section1.1">internal link</a> to another document.</p>'
        html, toc, meta = build.convert_markdown(md_text)
        self.assertEqual(html.strip(), expected.strip())

    def test_convert_internal_media(self):
        """Test relative image URL's are the same for different base_urls"""
        pages = [
            ('index.md',),
            ('internal.md',),
            ('sub/internal.md')
        ]

        site_navigation = nav.SiteNavigation(pages)

        expected_results = (
            './img/initial-layout.png',
            '../img/initial-layout.png',
            '../img/initial-layout.png',
        )

        template = '<p><img alt="The initial MkDocs layout" src="%s" /></p>\n'

        for (page, expected) in zip(site_navigation.walk_pages(), expected_results):
            md_text = '![The initial MkDocs layout](img/initial-layout.png)'
            html, _, _ = build.convert_markdown(md_text, site_navigation=site_navigation)
            self.assertEqual(html, template % expected)

    def test_convert_internal_asbolute_media(self):
        """Test absolute image URL's are correct for different base_urls"""
        pages = [
            ('index.md',),
            ('internal.md',),
            ('sub/internal.md')
        ]

        site_navigation = nav.SiteNavigation(pages)

        expected_results = (
            './img/initial-layout.png',
            '../img/initial-layout.png',
            '../../img/initial-layout.png',
        )

        template = '<p><img alt="The initial MkDocs layout" src="%s" /></p>\n'

        for (page, expected) in zip(site_navigation.walk_pages(), expected_results):
            md_text = '![The initial MkDocs layout](/img/initial-layout.png)'
            html, _, _ = build.convert_markdown(md_text, site_navigation=site_navigation)
            self.assertEqual(html, template % expected)

    def test_dont_convert_code_block_urls(self):
        pages = [
            ('index.md',),
            ('internal.md',),
            ('sub/internal.md')
        ]

        site_navigation = nav.SiteNavigation(pages)

        expected = dedent("""
        <p>An HTML Anchor::</p>
        <pre><code>&lt;a href="index.md"&gt;My example link&lt;/a&gt;
        </code></pre>
        """)

        for page in site_navigation.walk_pages():
            markdown = 'An HTML Anchor::\n\n    <a href="index.md">My example link</a>\n'
            html, _, _ = build.convert_markdown(markdown, site_navigation=site_navigation)
            self.assertEqual(dedent(html), expected)

    def test_anchor_only_link(self):

        pages = [
            ('index.md',),
            ('internal.md',),
            ('sub/internal.md')
        ]

        site_navigation = nav.SiteNavigation(pages)

        for page in site_navigation.walk_pages():
            markdown = '[test](#test)'
            html, _, _ = build.convert_markdown(markdown, site_navigation=site_navigation)
            self.assertEqual(html, '<p><a href="#test">test</a></p>\n')

    def test_ignore_external_link(self):
        md_text = 'An [external link](http://example.com/external.md).'
        expected = '<p>An <a href="http://example.com/external.md">external link</a>.</p>'
        html, toc, meta = build.convert_markdown(md_text)
        self.assertEqual(html.strip(), expected.strip())

    def test_not_use_directory_urls(self):
        md_text = 'An [internal link](internal.md) to another document.'
        expected = '<p>An <a href="internal/index.html">internal link</a> to another document.</p>'
        pages = [
            ('internal.md',)
        ]
        site_navigation = nav.SiteNavigation(pages, use_directory_urls=False)
        html, toc, meta = build.convert_markdown(md_text, site_navigation=site_navigation)
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

    def test_markdown_custom_extension(self):
        """
        Check that an extension applies when requested in the arguments to
        `convert_markdown`.
        """
        md_input = "foo__bar__baz"

        # Check that the plugin is not active when not requested.
        expected_without_smartstrong = "<p>foo<strong>bar</strong>baz</p>"
        html_base, _, _ = build.convert_markdown(md_input)
        self.assertEqual(html_base.strip(), expected_without_smartstrong)

        # Check that the plugin is active when requested.
        expected_with_smartstrong = "<p>foo__bar__baz</p>"
        html_ext, _, _ = build.convert_markdown(md_input, extensions=['smart_strong'])
        self.assertEqual(html_ext.strip(), expected_with_smartstrong)

    def test_markdown_duplicate_custom_extension(self):
        """
        Duplicated extension names should not cause problems.
        """
        md_input = "foo"
        html_ext, _, _ = build.convert_markdown(md_input, ['toc'])
        self.assertEqual(html_ext.strip(), '<p>foo</p>')

    def test_copying_media(self):

        docs_dir = tempfile.mkdtemp()
        site_dir = tempfile.mkdtemp()
        try:
            # Create a markdown file, image, dot file and dot directory.
            open(os.path.join(docs_dir, 'index.md'), 'w').close()
            open(os.path.join(docs_dir, 'img.jpg'), 'w').close()
            open(os.path.join(docs_dir, '.hidden'), 'w').close()
            os.mkdir(os.path.join(docs_dir, '.git'))
            open(os.path.join(docs_dir, '.git/hidden'), 'w').close()

            conf = config.validate_config({
                'site_name': 'Example',
                'docs_dir': docs_dir,
                'site_dir': site_dir
            })
            build.build(conf)

            # Verify only the markdown (coverted to html) and the image are copied.
            self.assertTrue(os.path.isfile(os.path.join(site_dir, 'index.html')))
            self.assertTrue(os.path.isfile(os.path.join(site_dir, 'img.jpg')))
            self.assertFalse(os.path.isfile(os.path.join(site_dir, '.hidden')))
            self.assertFalse(os.path.isfile(os.path.join(site_dir, '.git/hidden')))
        finally:
            shutil.rmtree(docs_dir)
            shutil.rmtree(site_dir)

    def test_strict_mode_valid(self):
        pages = [
            ('index.md',),
            ('internal.md',),
            ('sub/internal.md')
        ]
        site_nav = nav.SiteNavigation(pages)

        valid = "[test](internal.md)"
        build.convert_markdown(valid, site_nav, strict=False)
        build.convert_markdown(valid, site_nav, strict=True)

    def test_strict_mode_invalid(self):
        pages = [
            ('index.md',),
            ('internal.md',),
            ('sub/internal.md')
        ]
        site_nav = nav.SiteNavigation(pages)

        invalid = "[test](bad_link.md)"
        build.convert_markdown(invalid, site_nav, strict=False)

        self.assertRaises(
            MarkdownNotFound,
            build.convert_markdown, invalid, site_nav, strict=True)


class SearchTests(unittest.TestCase):

    def test_html_stripper(self):

        stripper = search.HTMLStripper()

        stripper.feed("<h1>Testing</h1><p>Content</p>")

        self.assertEquals(stripper.data, ["Testing", "Content"])

    def test_content_parser(self):

        parser = search.ContentParser()

        parser.feed('<h1 id="title">Title</h1>TEST')

        self.assertEquals(parser.data, [search.ContentSection(
            text=["TEST"],
            id_="title",
            title="Title"
        )])

    def test_content_parser_no_id(self):

        parser = search.ContentParser()

        parser.feed("<h1>Title</h1>TEST")

        self.assertEquals(parser.data, [search.ContentSection(
            text=["TEST"],
            id_=None,
            title="Title"
        )])

    def test_content_parser_content_before_header(self):

        parser = search.ContentParser()

        parser.feed("Content Before H1 <h1>Title</h1>TEST")

        self.assertEquals(parser.data, [search.ContentSection(
            text=["TEST"],
            id_=None,
            title="Title"
        )])

    def test_content_parser_no_sections(self):

        parser = search.ContentParser()

        parser.feed("No H1 or H2<span>Title</span>TEST")

        self.assertEquals(parser.data, [])

    def test_find_toc_by_id(self):
        """
        Test finding the relevant TOC item by the tag ID.
        """

        index = search.SearchIndex()

        md = dedent("""
        # Heading 1
        ## Heading 2
        ### Heading 3
        """)
        toc = _markdown_to_toc(md)

        toc_item = index._find_toc_by_id(toc, "heading-1")
        self.assertEqual(toc_item.url, "#heading-1")
        self.assertEqual(toc_item.title, "Heading 1")

        toc_item2 = index._find_toc_by_id(toc, "heading-2")
        self.assertEqual(toc_item2.url, "#heading-2")
        self.assertEqual(toc_item2.title, "Heading 2")

        toc_item3 = index._find_toc_by_id(toc, "heading-3")
        self.assertEqual(toc_item3, None)

    def test_create_search_index(self):

        html_content = """
        <h1 id="heading-1">Heading 1</h1>
        <p>Content 1</p>
        <h2 id="heading-2">Heading 2</h1>
        <p>Content 2</p>
        <h3 id="heading-3">Heading 3</h1>
        <p>Content 3</p>
        """

        pages = [
            ('index.md', 'Home'),
            ('about.md', 'About')
        ]
        site_navigation = nav.SiteNavigation(pages)

        md = dedent("""
        # Heading 1
        ## Heading 2
        ### Heading 3
        """)
        toc = _markdown_to_toc(md)

        full_content = ''.join("""Heading{0}Content{0}""".format(i) for i in range(1, 4))

        for page in site_navigation:

            index = search.SearchIndex()
            index.add_entry_from_context(page, html_content, toc)

            self.assertEqual(len(index._entries), 3)

            loc = page.abs_url

            self.assertEqual(index._entries[0]['title'], page.title)
            self.assertEqual(strip_whitespace(index._entries[0]['text']), full_content)
            self.assertEqual(index._entries[0]['tags'], "")
            self.assertEqual(index._entries[0]['loc'], loc)

            self.assertEqual(index._entries[1]['title'], "Heading 1")
            self.assertEqual(index._entries[1]['text'], "Content 1")
            self.assertEqual(index._entries[1]['tags'], "")
            self.assertEqual(index._entries[1]['loc'], "{0}#heading-1".format(loc))

            self.assertEqual(index._entries[2]['title'], "Heading 2")
            self.assertEqual(strip_whitespace(index._entries[2]['text']), "Content2Heading3Content3")
            self.assertEqual(index._entries[2]['tags'], "")
            self.assertEqual(index._entries[2]['loc'], "{0}#heading-2".format(loc))


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

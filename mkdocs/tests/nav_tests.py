#!/usr/bin/env python
# coding: utf-8

import mock
import os
import unittest

from mkdocs import nav
from mkdocs.exceptions import ConfigurationError
from mkdocs.tests.base import dedent


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

    def test_indented_toc_missing_child_title(self):
        pages = [
            ('index.md', 'Home'),
            ('api-guide/running.md', 'API Guide', 'Running'),
            ('api-guide/testing.md', 'API Guide'),
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

    def test_nested_ungrouped(self):
        pages = [
            ('index.md', 'Home'),
            ('about/contact.md', 'Contact'),
            ('about/sub/license.md', 'License Title')
        ]
        expected = dedent("""
        Home - /
        Contact - /about/contact/
        License Title - /about/sub/license/
        """)
        site_navigation = nav.SiteNavigation(pages)
        self.assertEqual(str(site_navigation).strip(), expected)
        self.assertEqual(len(site_navigation.nav_items), 3)
        self.assertEqual(len(site_navigation.pages), 3)

    def test_nested_ungrouped_no_titles(self):
        pages = [
            ('index.md',),
            ('about/contact.md'),
            ('about/sub/license.md')
        ]
        expected = dedent("""
        Home - /
        About
            Contact - /about/contact/
            License - /about/sub/license/
        """)

        site_navigation = nav.SiteNavigation(pages)
        self.assertEqual(str(site_navigation).strip(), expected)
        self.assertEqual(len(site_navigation.nav_items), 2)
        self.assertEqual(len(site_navigation.pages), 3)

    @mock.patch.object(os.path, 'sep', '\\')
    def test_nested_ungrouped_no_titles_windows(self):
        pages = [
            ('index.md',),
            ('about\\contact.md'),
            ('about\\sub\\license.md')
        ]
        expected = dedent("""
        Home - /
        About
            Contact - /about/contact/
            License - /about/sub/license/
        """)

        site_navigation = nav.SiteNavigation(pages)
        self.assertEqual(str(site_navigation).strip(), expected)
        self.assertEqual(len(site_navigation.nav_items), 2)
        self.assertEqual(len(site_navigation.pages), 3)

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

    def test_relative_md_links_have_slash(self):
        pages = [
            ('index.md',),
            ('user-guide/styling-your-docs.md',)
        ]
        site_navigation = nav.SiteNavigation(pages, use_directory_urls=False)
        site_navigation.url_context.base_path = "/user-guide/configuration"
        url = site_navigation.url_context.make_relative('/user-guide/styling-your-docs/')
        self.assertEqual(url, '../styling-your-docs/')

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

    def test_ancestors(self):

        pages = [
            ('index.md', 'Home'),
            ('api-guide/running.md', 'API Guide', 'Running'),
            ('api-guide/testing.md', 'API Guide', 'Testing'),
            ('api-guide/debugging.md', 'API Guide', 'Debugging'),
            ('about/release-notes.md', 'About', 'Release notes'),
            ('about/license.md', 'About', 'License')
        ]
        site_navigation = nav.SiteNavigation(pages)

        ancestors = (
            [],
            [site_navigation.nav_items[1]],
            [site_navigation.nav_items[1]],
            [site_navigation.nav_items[1]],
            [site_navigation.nav_items[2]],
            [site_navigation.nav_items[2]],
        )

        for page, expected_ancestor in zip(site_navigation.pages, ancestors):
            self.assertEqual(page.ancestors, expected_ancestor)

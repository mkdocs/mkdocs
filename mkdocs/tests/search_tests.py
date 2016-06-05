#!/usr/bin/env python
# coding: utf-8

from __future__ import unicode_literals
import unittest

from mkdocs import nav
from mkdocs import search
from mkdocs.tests.base import dedent, markdown_to_toc


def strip_whitespace(string):
    return string.replace("\n", "").replace(" ", "")


class SearchTests(unittest.TestCase):

    def test_html_stripper(self):

        stripper = search.HTMLStripper()

        stripper.feed("<h1>Testing</h1><p>Content</p>")

        self.assertEquals(stripper.data, ["Testing", "Content"])

    def test_content_parser(self):

        parser = search.ContentParser()

        parser.feed('<h1 id="title">Title</h1>TEST')
        parser.close()

        self.assertEquals(parser.data, [search.ContentSection(
            text=["TEST"],
            id_="title",
            title="Title"
        )])

    def test_content_parser_no_id(self):

        parser = search.ContentParser()

        parser.feed("<h1>Title</h1>TEST")
        parser.close()

        self.assertEquals(parser.data, [search.ContentSection(
            text=["TEST"],
            id_=None,
            title="Title"
        )])

    def test_content_parser_content_before_header(self):

        parser = search.ContentParser()

        parser.feed("Content Before H1 <h1>Title</h1>TEST")
        parser.close()

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
        toc = markdown_to_toc(md)

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

        pages = [
            {'Home': 'index.md'},
            {'About': 'about.md'},
        ]
        site_navigation = nav.SiteNavigation(pages)

        md = dedent("""
        # Heading 1
        ## Heading 2
        ### Heading 3
        """)
        toc = markdown_to_toc(md)

        full_content = ''.join("""Heading{0}Content{0}""".format(i) for i in range(1, 4))

        for page in site_navigation:

            index = search.SearchIndex()
            index.add_entry_from_context(page, html_content, toc)

            self.assertEqual(len(index._entries), 4)

            loc = page.abs_url

            self.assertEqual(index._entries[0]['title'], page.title)
            self.assertEqual(strip_whitespace(index._entries[0]['text']), full_content)
            self.assertEqual(index._entries[0]['location'], loc)

            self.assertEqual(index._entries[1]['title'], "Heading 1")
            self.assertEqual(index._entries[1]['text'], "Content 1")
            self.assertEqual(index._entries[1]['location'], "{0}#heading-1".format(loc))

            self.assertEqual(index._entries[2]['title'], "Heading 2")
            self.assertEqual(strip_whitespace(index._entries[2]['text']), "Content2")
            self.assertEqual(index._entries[2]['location'], "{0}#heading-2".format(loc))

            self.assertEqual(index._entries[3]['title'], "Heading 3")
            self.assertEqual(strip_whitespace(index._entries[3]['text']), "Content3")
            self.assertEqual(index._entries[3]['location'], "{0}#heading-3".format(loc))

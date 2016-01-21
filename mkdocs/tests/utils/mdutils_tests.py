#!/usr/bin/env python
# coding: utf-8

from __future__ import unicode_literals

from unittest import TestCase

from mkdocs.utils import mdutils


class MDUtilsTests(TestCase):

    def test_simple(self):

        markdown = """
        # The title
        """

        title = mdutils.get_markdown_title(markdown)

        self.assertEqual(title, "The title")

    def test_no_title(self):

        markdown = """
        Some markdown content
        """

        title = mdutils.get_markdown_title(markdown)

        self.assertEqual(title, None)

    def test_title_not_at_the_start(self):

        markdown = """
        Some markdown content

        # Title
        """

        title = mdutils.get_markdown_title(markdown)

        self.assertEqual(title, None)

    def test_h2_not_h1(self):

        markdown = """
        ## Title
        """

        title = mdutils.get_markdown_title(markdown)

        self.assertEqual(title, None)

    def test_whitespace_before_title(self):

        markdown = """
            \n# Title
        """

        title = mdutils.get_markdown_title(markdown)

        self.assertEqual(title, "Title")

#!/usr/bin/env python
# coding: utf-8

import markdown
import unittest

from mkdocs import toc
from mkdocs.tests.base import dedent


class TableOfContentsTests(unittest.TestCase):
    def markdown_to_toc(self, markdown_source):
        md = markdown.Markdown(extensions=['toc'])
        md.convert(markdown_source)
        toc_output = md.toc
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

    def test_indented_toc_html(self):
        md = dedent("""
        # Heading 1
        ## <code>Heading</code> 2
        ## Heading 3
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

    def test_mixed_html(self):
        md = dedent("""
        # Heading 1
        ## Heading 2
        # Heading 3
        ### Heading 4
        ### <a>Heading 5</a>
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

    def test_nested_anchor(self):
        md = dedent("""
        # Heading 1
        ## Heading 2
        # Heading 3
        ### Heading 4
        ### <a href="/">Heading 5</a>
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

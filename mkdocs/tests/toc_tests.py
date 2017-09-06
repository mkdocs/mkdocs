#!/usr/bin/env python
# coding: utf-8

from __future__ import unicode_literals
import unittest

from mkdocs.tests.base import dedent, markdown_to_toc


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
        toc = markdown_to_toc(md)
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
        toc = markdown_to_toc(md)
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
        toc = markdown_to_toc(md)
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
        toc = markdown_to_toc(md)
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
        toc = markdown_to_toc(md)
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
        toc = markdown_to_toc(md)
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
        toc = markdown_to_toc(md)
        self.assertEqual(str(toc).strip(), expected)

    def test_entityref(self):
        md = dedent("""
        # Heading & 1
        ## Heading > 2
        ### Heading < 3
        """)
        expected = dedent("""
        Heading &amp; 1 - #heading-1
            Heading &gt; 2 - #heading-2
                Heading &lt; 3 - #heading-3
        """)
        toc = markdown_to_toc(md)
        self.assertEqual(str(toc).strip(), expected)

    def test_level(self):
        md = dedent("""
        # Heading 1
        ## Heading 1.1
        ### Heading 1.1.1
        ### Heading 1.1.2
        ## Heading 1.2
        """)
        toc = markdown_to_toc(md)

        def get_level_sequence(item):
            result = (item.level,)
            for subitem in item.children:
                result += get_level_sequence(subitem)
            return result

        level_sequence = ()
        for item in toc:
            level_sequence += get_level_sequence(item)

        self.assertEqual(level_sequence, (0, 1, 2, 2, 1))

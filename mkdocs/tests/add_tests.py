#!/usr/bin/env python
# coding: utf-8

from __future__ import unicode_literals
import io
import os
import tempfile
import unittest

from mkdocs.commands import add, new

class AddTests(unittest.TestCase):

    def test_add(self):      
        template_text = """# Test content
        
        With some text ;)
        """

        temp_dir = tempfile.mkdtemp()
        new.new("myproject")
        project_dir = os.path.join(temp_dir, "myproject")
        os.chdir(project_dir)

        os.mkdir("_scaffold")
        temp_file = [
            tempfile.mkstemp('', '', os.path.join(project_dir, '_scaffold'), template_text),
            tempfile.mkstemp('', '', os.path.join(project_dir, '_template'), template_text)
        ]

        os.mkdir("_template")

        add.add(temp_file[0], 'test1', 'tempfile', True, None)
        add.add(temp_file[1], 'test2', 'tempfile', True, '_template')

        expected_paths = [
            os.path.join(project_dir, "docs", "test1", "tempfile.md"),
            os.path.join(project_dir, "docs", "test2", "tempfile.md")
        ]

        for expected_path in expected_paths:
            self.assertTrue(os.path.exists(expected_path))
            self.assertTrue(io.open(expected_path, 'r', encoding='utf-8') == template_text)

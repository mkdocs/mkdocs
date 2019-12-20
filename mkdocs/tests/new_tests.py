#!/usr/bin/env python

import tempfile
import unittest
import os

from mkdocs.commands import new


class NewTests(unittest.TestCase):

    def test_new(self):

        tempdir = tempfile.mkdtemp()
        os.chdir(tempdir)

        new.new("myproject")

        expected_paths = [
            os.path.join(tempdir, "myproject"),
            os.path.join(tempdir, "myproject", "mkdocs.yml"),
            os.path.join(tempdir, "myproject", "docs"),
            os.path.join(tempdir, "myproject", "docs", "index.md"),
        ]

        for expected_path in expected_paths:
            self.assertTrue(os.path.exists(expected_path))

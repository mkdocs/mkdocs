#!/usr/bin/env python
# coding: utf-8

from __future__ import unicode_literals

import os
import shutil
import tempfile
import unittest

from mkdocs.commands import new


class NewTests(unittest.TestCase):

    def setUp(self):

        self.old_cwd = os.getcwd()
        self.tempdir = tempfile.mkdtemp()
        os.chdir(self.tempdir)

    def tearDown(self):
        os.chdir(self.old_cwd)
        shutil.rmtree(self.tempdir)

    def test_new(self):

        new.new("myproject")

        expected_paths = [
            os.path.join(self.tempdir, "myproject"),
            os.path.join(self.tempdir, "myproject", "mkdocs.yml"),
            os.path.join(self.tempdir, "myproject", "docs"),
            os.path.join(self.tempdir, "myproject", "docs", "index.md"),
        ]

        for expected_path in expected_paths:
            self.assertTrue(os.path.exists(expected_path))

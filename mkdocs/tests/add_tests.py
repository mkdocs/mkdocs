#!/usr/bin/env python
# coding: utf-8

from __future__ import unicode_literals
import os
import tempfile
import unittest

from mkdocs.commands import add


class AddTests(unittest.TestCase):

    def test_is_cwd_mkdocs_project(self):
        """Current directory is a mkdocs project"""
        self.assertTrue(add._is_cwd_mkdocs_project())

    def test_is_cwd_as_template_directory(self):
        """Current directory as a template directory"""
        os.mkdir('_template')
        self.assertTrue(add._is_cwd_as_template_directory('_template'))
        os.rmdir('_template')

    def test_not_is_cwd_as_template_directory(self):
        """Current directory asn't a template directory"""
        self.assertFalse(add._is_cwd_as_template_directory('dir_error'))

    def test_not_as_file_in_docs_directory(self):
        """File doesn't exist in docs directory"""
        self.assertTrue(add._as_not_file_in_docs_directory('no_file_in_dir'))

    def test_as_output_directory(self):
        """Output directory already exist"""
        os.makedirs('tmp/output')
        self.assertTrue(add._as_output_directory('tmp/output', False))
        os.removedirs('tmp/output')

    def test_not_as_output_directory_without_creation(self):
        """Output directory doesn't exist and no creation allowed"""
        self.assertFalse(add._as_output_directory('output', False))

    def test_not_as_output_directory_with_creation(self):
        """Output directory doesn't exist and creation allowed"""
        os.mkdir('tmp')
        self.assertTrue(add._as_output_directory('tmp/output', True))
        os.removedirs('tmp/output')

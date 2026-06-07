#!/usr/bin/env python

import unittest
from pathlib import Path

from mkdocs.commands import serve
from mkdocs.tests.base import load_config, tempdir


class ServeTests(unittest.TestCase):
    @tempdir(files=['index.md', '.hidden', 'ignored.md', 'templates/page.html'])
    def test_docs_file_ignore_matches_config_exclusions(self, docs_dir):
        cfg = load_config(docs_dir=docs_dir, exclude_docs='ignored.md')
        is_ignored = serve._make_docs_file_ignored(cfg, include_drafts=True)

        self.assertFalse(is_ignored(str(Path(docs_dir, 'index.md'))))
        self.assertTrue(is_ignored(str(Path(docs_dir, '.hidden'))))
        self.assertTrue(is_ignored(str(Path(docs_dir, 'ignored.md'))))
        self.assertTrue(is_ignored(str(Path(docs_dir, 'templates/page.html'))))
        self.assertFalse(is_ignored(str(Path(docs_dir).parent / 'index.md')))

    @tempdir(files=['.well-known/security.txt'])
    def test_docs_file_ignore_respects_exclude_docs_negation(self, docs_dir):
        cfg = load_config(docs_dir=docs_dir, exclude_docs='!.well-known/security.txt')
        is_ignored = serve._make_docs_file_ignored(cfg, include_drafts=True)

        self.assertFalse(is_ignored(str(Path(docs_dir, '.well-known/security.txt'))))

    @tempdir(files=['draft.md'])
    def test_docs_file_ignore_follows_serve_preview_inclusion(self, docs_dir):
        cfg = load_config(docs_dir=docs_dir, draft_docs='draft.md')

        is_ignored_in_serve = serve._make_docs_file_ignored(cfg, include_drafts=True)
        is_ignored_in_clean_serve = serve._make_docs_file_ignored(cfg, include_drafts=False)

        self.assertFalse(is_ignored_in_serve(str(Path(docs_dir, 'draft.md'))))
        self.assertTrue(is_ignored_in_clean_serve(str(Path(docs_dir, 'draft.md'))))

    @tempdir(files=['templates/page.html'])
    def test_docs_file_ignore_keeps_extra_templates(self, docs_dir):
        cfg = load_config(docs_dir=docs_dir, extra_templates=['templates/page.html'])
        is_ignored = serve._make_docs_file_ignored(cfg, include_drafts=True)

        self.assertFalse(is_ignored(str(Path(docs_dir, 'templates/page.html'))))

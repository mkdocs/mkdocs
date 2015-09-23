#!/usr/bin/env python
# coding: utf-8

from __future__ import unicode_literals
import unittest
import mock

from click.testing import CliRunner

from mkdocs import __main__ as cli


class CLITests(unittest.TestCase):

    def setUp(self):
        self.runner = CliRunner()

    @mock.patch('mkdocs.commands.serve.serve', autospec=True)
    def test_serve(self, mock_serve):

        result = self.runner.invoke(
            cli.cli, ["serve", ], catch_exceptions=False)

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(mock_serve.call_count, 1)

    @mock.patch('mkdocs.commands.build.build', autospec=True)
    def test_build(self, mock_build):

        result = self.runner.invoke(
            cli.cli, ["build", ], catch_exceptions=False)

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(mock_build.call_count, 1)

    @mock.patch('mkdocs.commands.build.build', autospec=True)
    def test_build_verbose(self, mock_build):

        result = self.runner.invoke(
            cli.cli, ["--verbose", "build"], catch_exceptions=False)

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(mock_build.call_count, 1)

    @mock.patch('mkdocs.commands.build.build', autospec=True)
    def test_json(self, mock_build):

        result = self.runner.invoke(
            cli.cli, ["json", ], catch_exceptions=False)

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(mock_build.call_count, 1)

    @mock.patch('mkdocs.commands.new.new', autospec=True)
    def test_new(self, mock_new):

        result = self.runner.invoke(
            cli.cli, ["new", "project"], catch_exceptions=False)

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(mock_new.call_count, 1)

    @mock.patch('mkdocs.commands.gh_deploy.gh_deploy', autospec=True)
    def test_gh_deploy(self, mock_gh_deploy):

        result = self.runner.invoke(
            cli.cli, ["gh-deploy"], catch_exceptions=False)

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(mock_gh_deploy.call_count, 1)

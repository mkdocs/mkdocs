#!/usr/bin/env python
# coding: utf-8

import unittest
import mock

from click.testing import CliRunner

from mkdocs import cli


class CLITests(unittest.TestCase):

    def setUp(self):
        self.runner = CliRunner()

    @mock.patch('mkdocs.serve.serve')
    def test_serve(self, mock_serve):

        result = self.runner.invoke(
            cli.cli, ["serve", ], catch_exceptions=False)

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(mock_serve.call_count, 1)

    @mock.patch('mkdocs.build.build')
    def test_build(self, mock_build):

        result = self.runner.invoke(
            cli.cli, ["build", ], catch_exceptions=False)

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(mock_build.call_count, 1)

    @mock.patch('mkdocs.build.build')
    def test_build_verbose(self, mock_build):

        result = self.runner.invoke(
            cli.cli, ["--verbose", "build"], catch_exceptions=False)

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(mock_build.call_count, 1)

    @mock.patch('mkdocs.build.build')
    def test_json(self, mock_build):

        result = self.runner.invoke(
            cli.cli, ["json", ], catch_exceptions=False)

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(mock_build.call_count, 1)

    @mock.patch('mkdocs.new.new')
    def test_new(self, mock_new):

        result = self.runner.invoke(
            cli.cli, ["new", "project"], catch_exceptions=False)

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(mock_new.call_count, 1)

    @mock.patch('mkdocs.gh_deploy.gh_deploy')
    def test_gh_deploy(self, mock_gh_deploy):

        result = self.runner.invoke(
            cli.cli, ["gh-deploy"], catch_exceptions=False)

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(mock_gh_deploy.call_count, 1)

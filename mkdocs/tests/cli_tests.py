#!/usr/bin/env python
# coding: utf-8

from __future__ import unicode_literals
import unittest
import mock
import logging
import sys
import io

from click.testing import CliRunner

from mkdocs import __main__ as cli

PY3 = sys.version_info[0] == 3


class CLITests(unittest.TestCase):

    def setUp(self):
        self.runner = CliRunner()

    @mock.patch('mkdocs.commands.serve.serve', autospec=True)
    def test_serve_default(self, mock_serve):

        result = self.runner.invoke(
            cli.cli, ["serve"], catch_exceptions=False)

        self.assertEqual(result.exit_code, 0)
        mock_serve.assert_called_once_with(
            config_file=None,
            dev_addr=None,
            strict=None,
            theme=None,
            theme_dir=None,
            livereload='livereload'
        )

    @mock.patch('mkdocs.commands.serve.serve', autospec=True)
    def test_serve_config_file(self, mock_serve):

        result = self.runner.invoke(
            cli.cli, ["serve", "--config-file", "mkdocs.yml"], catch_exceptions=False)

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(mock_serve.call_count, 1)
        args, kwargs = mock_serve.call_args
        self.assertTrue('config_file' in kwargs)
        if PY3:
            self.assertIsInstance(kwargs['config_file'], io.BufferedReader)
        else:
            self.assertTrue(isinstance(kwargs['config_file'], file))
        self.assertEqual(kwargs['config_file'].name, 'mkdocs.yml')

    @mock.patch('mkdocs.commands.serve.serve', autospec=True)
    def test_serve_dev_addr(self, mock_serve):

        result = self.runner.invoke(
            cli.cli, ["serve", '--dev-addr', '0.0.0.0:80'], catch_exceptions=False)

        self.assertEqual(result.exit_code, 0)
        mock_serve.assert_called_once_with(
            config_file=None,
            dev_addr='0.0.0.0:80',
            strict=None,
            theme=None,
            theme_dir=None,
            livereload='livereload'
        )

    @mock.patch('mkdocs.commands.serve.serve', autospec=True)
    def test_serve_strict(self, mock_serve):

        result = self.runner.invoke(
            cli.cli, ["serve", '--strict'], catch_exceptions=False)

        self.assertEqual(result.exit_code, 0)
        mock_serve.assert_called_once_with(
            config_file=None,
            dev_addr=None,
            strict=True,
            theme=None,
            theme_dir=None,
            livereload='livereload'
        )

    @mock.patch('mkdocs.commands.serve.serve', autospec=True)
    def test_serve_theme(self, mock_serve):

        result = self.runner.invoke(
            cli.cli, ["serve", '--theme', 'readthedocs'], catch_exceptions=False)

        self.assertEqual(result.exit_code, 0)
        mock_serve.assert_called_once_with(
            config_file=None,
            dev_addr=None,
            strict=None,
            theme='readthedocs',
            theme_dir=None,
            livereload='livereload'
        )

    @mock.patch('mkdocs.commands.serve.serve', autospec=True)
    def test_serve_theme_dir(self, mock_serve):

        result = self.runner.invoke(
            cli.cli, ["serve", '--theme-dir', 'custom'], catch_exceptions=False)

        self.assertEqual(result.exit_code, 0)
        mock_serve.assert_called_once_with(
            config_file=None,
            dev_addr=None,
            strict=None,
            theme=None,
            theme_dir='custom',
            livereload='livereload'
        )

    @mock.patch('mkdocs.commands.serve.serve', autospec=True)
    def test_serve_livereload(self, mock_serve):

        result = self.runner.invoke(
            cli.cli, ["serve", '--livereload'], catch_exceptions=False)

        self.assertEqual(result.exit_code, 0)
        mock_serve.assert_called_once_with(
            config_file=None,
            dev_addr=None,
            strict=None,
            theme=None,
            theme_dir=None,
            livereload='livereload'
        )

    @mock.patch('mkdocs.commands.serve.serve', autospec=True)
    def test_serve_no_livereload(self, mock_serve):

        result = self.runner.invoke(
            cli.cli, ["serve", '--no-livereload'], catch_exceptions=False)

        self.assertEqual(result.exit_code, 0)
        mock_serve.assert_called_once_with(
            config_file=None,
            dev_addr=None,
            strict=None,
            theme=None,
            theme_dir=None,
            livereload='no-livereload'
        )

    @mock.patch('mkdocs.commands.serve.serve', autospec=True)
    def test_serve_dirtyreload(self, mock_serve):

        result = self.runner.invoke(
            cli.cli, ["serve", '--dirtyreload'], catch_exceptions=False)

        self.assertEqual(result.exit_code, 0)
        mock_serve.assert_called_once_with(
            config_file=None,
            dev_addr=None,
            strict=None,
            theme=None,
            theme_dir=None,
            livereload='dirty'
        )

    @mock.patch('mkdocs.config.load_config', autospec=True)
    @mock.patch('mkdocs.commands.build.build', autospec=True)
    def test_build_defaults(self, mock_build, mock_load_config):

        result = self.runner.invoke(
            cli.cli, ['build'], catch_exceptions=False)

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(mock_build.call_count, 1)
        args, kwargs = mock_build.call_args
        self.assertTrue('dirty' in kwargs)
        self.assertFalse(kwargs['dirty'])
        mock_load_config.assert_called_once_with(
            config_file=None,
            strict=None,
            theme=None,
            theme_dir=None,
            site_dir=None
        )
        logger = logging.getLogger('mkdocs')
        self.assertEqual(logger.level, logging.INFO)

    @mock.patch('mkdocs.commands.build.build', autospec=True)
    def test_build_clean(self, mock_build):

        result = self.runner.invoke(
            cli.cli, ['build', '--clean'], catch_exceptions=False)

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(mock_build.call_count, 1)
        args, kwargs = mock_build.call_args
        self.assertTrue('dirty' in kwargs)
        self.assertFalse(kwargs['dirty'])

    @mock.patch('mkdocs.commands.build.build', autospec=True)
    def test_build_dirty(self, mock_build):

        result = self.runner.invoke(
            cli.cli, ['build', '--dirty'], catch_exceptions=False)

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(mock_build.call_count, 1)
        args, kwargs = mock_build.call_args
        self.assertTrue('dirty' in kwargs)
        self.assertTrue(kwargs['dirty'])

    @mock.patch('mkdocs.config.load_config', autospec=True)
    @mock.patch('mkdocs.commands.build.build', autospec=True)
    def test_build_config_file(self, mock_build, mock_load_config):

        result = self.runner.invoke(
            cli.cli, ['build', '--config-file', 'mkdocs.yml'], catch_exceptions=False)

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(mock_build.call_count, 1)
        self.assertEqual(mock_load_config.call_count, 1)
        args, kwargs = mock_load_config.call_args
        self.assertTrue('config_file' in kwargs)
        if PY3:
            self.assertIsInstance(kwargs['config_file'], io.BufferedReader)
        else:
            self.assertTrue(isinstance(kwargs['config_file'], file))
        self.assertEqual(kwargs['config_file'].name, 'mkdocs.yml')

    @mock.patch('mkdocs.config.load_config', autospec=True)
    @mock.patch('mkdocs.commands.build.build', autospec=True)
    def test_build_strict(self, mock_build, mock_load_config):

        result = self.runner.invoke(
            cli.cli, ['build', '--strict'], catch_exceptions=False)

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(mock_build.call_count, 1)
        mock_load_config.assert_called_once_with(
            config_file=None,
            strict=True,
            theme=None,
            theme_dir=None,
            site_dir=None
        )

    @mock.patch('mkdocs.config.load_config', autospec=True)
    @mock.patch('mkdocs.commands.build.build', autospec=True)
    def test_build_theme(self, mock_build, mock_load_config):

        result = self.runner.invoke(
            cli.cli, ['build', '--theme', 'readthedocs'], catch_exceptions=False)

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(mock_build.call_count, 1)
        mock_load_config.assert_called_once_with(
            config_file=None,
            strict=None,
            theme='readthedocs',
            theme_dir=None,
            site_dir=None
        )

    @mock.patch('mkdocs.config.load_config', autospec=True)
    @mock.patch('mkdocs.commands.build.build', autospec=True)
    def test_build_theme_dir(self, mock_build, mock_load_config):

        result = self.runner.invoke(
            cli.cli, ['build', '--theme-dir', 'custom'], catch_exceptions=False)

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(mock_build.call_count, 1)
        mock_load_config.assert_called_once_with(
            config_file=None,
            strict=None,
            theme=None,
            theme_dir='custom',
            site_dir=None
        )

    @mock.patch('mkdocs.config.load_config', autospec=True)
    @mock.patch('mkdocs.commands.build.build', autospec=True)
    def test_build_site_dir(self, mock_build, mock_load_config):

        result = self.runner.invoke(
            cli.cli, ['build', '--site-dir', 'custom'], catch_exceptions=False)

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(mock_build.call_count, 1)
        mock_load_config.assert_called_once_with(
            config_file=None,
            strict=None,
            theme=None,
            theme_dir=None,
            site_dir='custom'
        )

    @mock.patch('mkdocs.commands.build.build', autospec=True)
    def test_build_verbose(self, mock_build):

        result = self.runner.invoke(
            cli.cli, ['build', '--verbose'], catch_exceptions=False)

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(mock_build.call_count, 1)
        logger = logging.getLogger('mkdocs')
        self.assertEqual(logger.level, logging.DEBUG)

    @mock.patch('mkdocs.commands.build.build', autospec=True)
    def test_build_quiet(self, mock_build):

        result = self.runner.invoke(
            cli.cli, ['build', '--quiet'], catch_exceptions=False)

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(mock_build.call_count, 1)
        logger = logging.getLogger('mkdocs')
        self.assertEqual(logger.level, logging.ERROR)

    @mock.patch('mkdocs.commands.new.new', autospec=True)
    def test_new(self, mock_new):

        result = self.runner.invoke(
            cli.cli, ["new", "project"], catch_exceptions=False)

        self.assertEqual(result.exit_code, 0)
        mock_new.assert_called_once_with('project')

    @mock.patch('mkdocs.config.load_config', autospec=True)
    @mock.patch('mkdocs.commands.build.build', autospec=True)
    @mock.patch('mkdocs.commands.gh_deploy.gh_deploy', autospec=True)
    def test_gh_deploy_defaults(self, mock_gh_deploy, mock_build, mock_load_config):

        result = self.runner.invoke(
            cli.cli, ['gh-deploy'], catch_exceptions=False)

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(mock_gh_deploy.call_count, 1)
        g_args, g_kwargs = mock_gh_deploy.call_args
        self.assertTrue('message' in g_kwargs)
        self.assertEqual(g_kwargs['message'], None)
        self.assertTrue('force' in g_kwargs)
        self.assertEqual(g_kwargs['force'], False)
        self.assertEqual(mock_build.call_count, 1)
        b_args, b_kwargs = mock_build.call_args
        self.assertTrue('dirty' in b_kwargs)
        self.assertFalse(b_kwargs['dirty'])
        mock_load_config.assert_called_once_with(
            config_file=None,
            remote_branch=None,
            remote_name=None
        )

    @mock.patch('mkdocs.commands.build.build', autospec=True)
    @mock.patch('mkdocs.commands.gh_deploy.gh_deploy', autospec=True)
    def test_gh_deploy_clean(self, mock_gh_deploy, mock_build):

        result = self.runner.invoke(
            cli.cli, ['gh-deploy', '--clean'], catch_exceptions=False)

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(mock_gh_deploy.call_count, 1)
        self.assertEqual(mock_build.call_count, 1)
        args, kwargs = mock_build.call_args
        self.assertTrue('dirty' in kwargs)
        self.assertFalse(kwargs['dirty'])

    @mock.patch('mkdocs.commands.build.build', autospec=True)
    @mock.patch('mkdocs.commands.gh_deploy.gh_deploy', autospec=True)
    def test_gh_deploy_dirty(self, mock_gh_deploy, mock_build):

        result = self.runner.invoke(
            cli.cli, ['gh-deploy', '--dirty'], catch_exceptions=False)

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(mock_gh_deploy.call_count, 1)
        self.assertEqual(mock_build.call_count, 1)
        args, kwargs = mock_build.call_args
        self.assertTrue('dirty' in kwargs)
        self.assertTrue(kwargs['dirty'])

    @mock.patch('mkdocs.config.load_config', autospec=True)
    @mock.patch('mkdocs.commands.build.build', autospec=True)
    @mock.patch('mkdocs.commands.gh_deploy.gh_deploy', autospec=True)
    def test_gh_deploy_config_file(self, mock_gh_deploy, mock_build, mock_load_config):

        result = self.runner.invoke(
            cli.cli, ['gh-deploy', '--config-file', 'mkdocs.yml'], catch_exceptions=False)

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(mock_gh_deploy.call_count, 1)
        self.assertEqual(mock_build.call_count, 1)
        self.assertEqual(mock_load_config.call_count, 1)
        args, kwargs = mock_load_config.call_args
        self.assertTrue('config_file' in kwargs)
        if PY3:
            self.assertIsInstance(kwargs['config_file'], io.BufferedReader)
        else:
            self.assertTrue(isinstance(kwargs['config_file'], file))
        self.assertEqual(kwargs['config_file'].name, 'mkdocs.yml')

    @mock.patch('mkdocs.config.load_config', autospec=True)
    @mock.patch('mkdocs.commands.build.build', autospec=True)
    @mock.patch('mkdocs.commands.gh_deploy.gh_deploy', autospec=True)
    def test_gh_deploy_message(self, mock_gh_deploy, mock_build, mock_load_config):

        result = self.runner.invoke(
            cli.cli, ['gh-deploy', '--message', 'A commit message'], catch_exceptions=False)

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(mock_gh_deploy.call_count, 1)
        g_args, g_kwargs = mock_gh_deploy.call_args
        self.assertTrue('message' in g_kwargs)
        self.assertEqual(g_kwargs['message'], 'A commit message')
        self.assertEqual(mock_build.call_count, 1)
        self.assertEqual(mock_load_config.call_count, 1)

    @mock.patch('mkdocs.config.load_config', autospec=True)
    @mock.patch('mkdocs.commands.build.build', autospec=True)
    @mock.patch('mkdocs.commands.gh_deploy.gh_deploy', autospec=True)
    def test_gh_deploy_remote_branch(self, mock_gh_deploy, mock_build, mock_load_config):

        result = self.runner.invoke(
            cli.cli, ['gh-deploy', '--remote-branch', 'foo'], catch_exceptions=False)

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(mock_gh_deploy.call_count, 1)
        self.assertEqual(mock_build.call_count, 1)
        mock_load_config.assert_called_once_with(
            config_file=None,
            remote_branch='foo',
            remote_name=None
        )

    @mock.patch('mkdocs.config.load_config', autospec=True)
    @mock.patch('mkdocs.commands.build.build', autospec=True)
    @mock.patch('mkdocs.commands.gh_deploy.gh_deploy', autospec=True)
    def test_gh_deploy_remote_name(self, mock_gh_deploy, mock_build, mock_load_config):

        result = self.runner.invoke(
            cli.cli, ['gh-deploy', '--remote-name', 'foo'], catch_exceptions=False)

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(mock_gh_deploy.call_count, 1)
        self.assertEqual(mock_build.call_count, 1)
        mock_load_config.assert_called_once_with(
            config_file=None,
            remote_branch=None,
            remote_name='foo'
        )

    @mock.patch('mkdocs.config.load_config', autospec=True)
    @mock.patch('mkdocs.commands.build.build', autospec=True)
    @mock.patch('mkdocs.commands.gh_deploy.gh_deploy', autospec=True)
    def test_gh_deploy_force(self, mock_gh_deploy, mock_build, mock_load_config):

        result = self.runner.invoke(
            cli.cli, ['gh-deploy', '--force'], catch_exceptions=False)

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(mock_gh_deploy.call_count, 1)
        g_args, g_kwargs = mock_gh_deploy.call_args
        self.assertTrue('force' in g_kwargs)
        self.assertEqual(g_kwargs['force'], True)
        self.assertEqual(mock_build.call_count, 1)
        self.assertEqual(mock_load_config.call_count, 1)

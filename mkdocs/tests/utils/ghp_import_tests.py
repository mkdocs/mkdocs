#!/usr/bin/env python
# coding: utf-8

from __future__ import unicode_literals

import mock
import os
import subprocess
import tempfile
import unittest
import shutil

from mkdocs.utils import ghp_import


class UtilsTests(unittest.TestCase):

    @mock.patch('subprocess.call', auto_spec=True)
    @mock.patch('subprocess.Popen', auto_spec=True)
    def test_try_rebase(self, mock_popen, mock_call):

        popen = mock.Mock()
        mock_popen.return_value = popen
        popen.communicate.return_value = (
            '4c82346e4b1b816be89dd709d35a6b169aa3df61\n', '')
        popen.wait.return_value = 0

        ghp_import.try_rebase('origin', 'gh-pages')

        mock_popen.assert_called_once_with(
            ['git', 'rev-list', '--max-count=1', 'origin/gh-pages'],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        mock_call.assert_called_once_with(
            ['git', 'update-ref', 'refs/heads/gh-pages',
             '4c82346e4b1b816be89dd709d35a6b169aa3df61'])

    @mock.patch('subprocess.Popen', auto_spec=True)
    def test_get_prev_commit(self, mock_popen):

        popen = mock.Mock()
        mock_popen.return_value = popen
        popen.communicate.return_value = (
            b'4c82346e4b1b816be89dd709d35a6b169aa3df61\n', '')
        popen.wait.return_value = 0

        result = ghp_import.get_prev_commit('test-branch')

        self.assertEqual(result, u'4c82346e4b1b816be89dd709d35a6b169aa3df61')
        mock_popen.assert_called_once_with(
            ['git', 'rev-list', '--max-count=1', 'test-branch', '--'],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)

    @mock.patch('subprocess.Popen', auto_spec=True)
    def test_get_config(self, mock_popen):

        popen = mock.Mock()
        mock_popen.return_value = popen
        popen.communicate.return_value = (
            b'Dougal Matthews\n', '')

        result = ghp_import.get_config('user.name')

        self.assertEqual(result, u'Dougal Matthews')
        mock_popen.assert_called_once_with(
            ['git', 'config', 'user.name'],
            stdout=subprocess.PIPE, stdin=subprocess.PIPE)

    @mock.patch('mkdocs.utils.ghp_import.get_prev_commit')
    @mock.patch('mkdocs.utils.ghp_import.get_config')
    def test_start_commit(self, mock_get_config, mock_get_prev_commit):

        pipe = mock.Mock()
        mock_get_config.side_effect = ['username', 'email']
        mock_get_prev_commit.return_value = 'SHA'

        ghp_import.start_commit(pipe, 'test-branch', 'test-message')

        mock_get_prev_commit.assert_called_once_with('test-branch')
        self.assertEqual(pipe.stdin.write.call_count, 5)

    @mock.patch('mkdocs.utils.ghp_import.try_rebase', return_value=True)
    @mock.patch('mkdocs.utils.ghp_import.get_prev_commit', return_value='sha')
    @mock.patch('mkdocs.utils.ghp_import.get_config', return_value='config')
    @mock.patch('subprocess.call', auto_spec=True)
    @mock.patch('subprocess.Popen', auto_spec=True)
    def test_ghp_import(self, mock_popen, mock_call, mock_get_config,
                        mock_get_prev_commit, mock_try_rebase):

        directory = tempfile.mkdtemp()
        open(os.path.join(directory, 'file'), 'a').close()

        try:
            popen = mock.Mock()
            mock_popen.return_value = popen
            popen.communicate.return_value = ('', '')
            popen.wait.return_value = 0

            ghp_import.ghp_import(directory, "test message",
                                  remote='fake-remote-name',
                                  branch='fake-branch-name')

            self.assertEqual(mock_popen.call_count, 2)
            self.assertEqual(mock_call.call_count, 0)
        finally:
            shutil.rmtree(directory)

    @mock.patch('mkdocs.utils.ghp_import.try_rebase', return_value=True)
    @mock.patch('mkdocs.utils.ghp_import.get_prev_commit', return_value='sha')
    @mock.patch('mkdocs.utils.ghp_import.get_config', return_value='config')
    @mock.patch('mkdocs.utils.ghp_import.run_import')
    @mock.patch('subprocess.call', auto_spec=True)
    @mock.patch('subprocess.Popen', auto_spec=True)
    def test_ghp_import_error(self, mock_popen, mock_call, mock_get_config,
                              mock_run_import, mock_get_prev_commit, mock_try_rebase):

        directory = tempfile.mkdtemp()
        open(os.path.join(directory, 'file'), 'a').close()

        try:
            popen = mock.Mock()
            mock_popen.return_value = popen

            error_string = 'TestError123'
            popen.communicate.return_value = ('', error_string)
            popen.wait.return_value = 1

            result, ghp_error = ghp_import.ghp_import(directory, "test message",
                                                      remote='fake-remote-name',
                                                      branch='fake-branch-name')

            self.assertEqual(result, False)
            self.assertEqual(ghp_error, error_string)
        finally:
            shutil.rmtree(directory)

from __future__ import unicode_literals

import unittest
import mock

from mkdocs.config import load_config
from mkdocs.commands import gh_deploy


class TestGitHubDeploy(unittest.TestCase):

    @mock.patch('subprocess.Popen')
    def test_is_cwd_git_repo(self, mock_popeno):

        mock_popeno().wait.return_value = 0

        self.assertTrue(gh_deploy._is_cwd_git_repo())

    @mock.patch('subprocess.Popen')
    def test_is_cwd_not_git_repo(self, mock_popeno):

        mock_popeno().wait.return_value = 1

        self.assertFalse(gh_deploy._is_cwd_git_repo())

    @mock.patch('subprocess.Popen')
    def test_get_current_sha(self, mock_popeno):

        mock_popeno().communicate.return_value = (b'6d98394\n', b'')

        self.assertEqual(gh_deploy._get_current_sha(), u'6d98394')

    @mock.patch('subprocess.Popen')
    def test_get_remote_url_ssh(self, mock_popeno):

        mock_popeno().communicate.return_value = (
            b'git@github.com:mkdocs/mkdocs.git\n',
            b''
        )

        expected = (u'git@', u'mkdocs/mkdocs.git')
        self.assertEqual(expected, gh_deploy._get_remote_url('origin'))

    @mock.patch('subprocess.Popen')
    def test_get_remote_url_http(self, mock_popeno):

        mock_popeno().communicate.return_value = (
            b'https://github.com/mkdocs/mkdocs.git\n',
            b''
        )

        expected = (u'https://', u'mkdocs/mkdocs.git')
        self.assertEqual(expected, gh_deploy._get_remote_url('origin'))

    @mock.patch('subprocess.Popen')
    def test_get_remote_url_enterprise(self, mock_popeno):

        mock_popeno().communicate.return_value = (
            b'https://notgh.com/mkdocs/mkdocs.git\n',
            b''
        )

        expected = (None, None)
        self.assertEqual(expected, gh_deploy._get_remote_url('origin'))

    @mock.patch('mkdocs.commands.gh_deploy._is_cwd_git_repo', return_value=True)
    @mock.patch('mkdocs.commands.gh_deploy._get_current_sha', return_value='shashas')
    @mock.patch('mkdocs.commands.gh_deploy._get_remote_url', return_value=(None, None))
    @mock.patch('mkdocs.commands.gh_deploy.ghp_import.ghp_import', return_value=(True, ''))
    def test_deploy(self, mock_import, get_remote, get_sha, is_repo):

        config = load_config(
            remote_branch='test',
        )
        gh_deploy.gh_deploy(config)

    @mock.patch('mkdocs.commands.gh_deploy._is_cwd_git_repo', return_value=True)
    @mock.patch('mkdocs.commands.gh_deploy._get_current_sha', return_value='shashas')
    @mock.patch('mkdocs.commands.gh_deploy._get_remote_url', return_value=(None, None))
    @mock.patch('mkdocs.commands.gh_deploy.ghp_import.ghp_import', return_value=(True, ''))
    @mock.patch('os.path.isfile', return_value=False)
    def test_deploy_no_cname(self, mock_isfile, mock_import, get_remote,
                             get_sha, is_repo):

        config = load_config(
            remote_branch='test',
        )
        gh_deploy.gh_deploy(config)

    @mock.patch('mkdocs.commands.gh_deploy._is_cwd_git_repo', return_value=True)
    @mock.patch('mkdocs.commands.gh_deploy._get_current_sha', return_value='shashas')
    @mock.patch('mkdocs.commands.gh_deploy._get_remote_url', return_value=(
        u'git@', u'mkdocs/mkdocs.git'))
    @mock.patch('mkdocs.commands.gh_deploy.ghp_import.ghp_import', return_value=(True, ''))
    def test_deploy_hostname(self, mock_import, get_remote, get_sha, is_repo):

        config = load_config(
            remote_branch='test',
        )
        gh_deploy.gh_deploy(config)

    @mock.patch('mkdocs.utils.ghp_import.ghp_import')
    @mock.patch('mkdocs.commands.gh_deploy.log')
    def test_deploy_error(self, mock_log, mock_import):
        error_string = 'TestError123'
        mock_import.return_value = (False, error_string)

        config = load_config(
            remote_branch='test',
        )

        self.assertRaises(SystemExit, gh_deploy.gh_deploy, config)
        mock_log.error.assert_called_once_with('Failed to deploy to GitHub with error: \n%s',
                                               error_string)

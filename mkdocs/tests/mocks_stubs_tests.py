import unittest
from unittest.mock import call, patch, MagicMock

from mkdocs.config.base import ValidationError
from mkdocs.config.config_options import Hooks, Plugins
from mkdocs.exceptions import Abort
from mkdocs.utils import clean_directory
from click.testing import CliRunner
from mkdocs import __main__ as cli

class TestMocksAndStubs(unittest.TestCase):
    def test_clean_directory_with_hidden_files(self):
        """Test clean_directory function handles hidden files correctly without accessing the file system."""
        fake_dir = '/fake/dir'
        with patch('os.path.exists', return_value=True), \
            patch('os.listdir', return_value=['.hidden', '.gitignore', '.DS_Store']) as mock_listdir, \
            patch('shutil.rmtree') as mock_rmtree, \
            patch('os.unlink') as mock_unlink:
                clean_directory(fake_dir)
                mock_listdir.assert_called_once_with(fake_dir)
                # Ensure all hidden files are ignored and not deleted
                # Since all files returned by the mock_listdir are hidden, rmtree and unlink should not be called
                mock_rmtree.assert_not_called()
                mock_unlink.assert_not_called()

    def test_get_deps_command(self):
        """Test get-deps command logic with mocked dependencies."""
        runner = CliRunner()
        with patch('mkdocs_get_deps.get_deps') as mock_get_deps:
            mock_get_deps.return_value = ["some arbitrary val representing a plugin"]  # Simulate successful execution
            result = runner.invoke(cli.cli, ["get-deps", "-f", "mkdocs.yml"], catch_exceptions=False)

            self.assertEqual(result.exit_code, 0)
            mock_get_deps.assert_called_once()

    def test_get_deps_command_exit_if_warnings(self):
        """Test get-deps command logic if warnings occurred with mocked dependencies."""
        runner = CliRunner()
        with patch('mkdocs.utils.CountHandler') as mock_count_handler, \
            patch('logging.getLogger', return_value=MagicMock()), \
            patch('mkdocs_get_deps.get_deps') as mock_get_deps:
                    # Simulate warnings occurred
                    mock_count_handler.get_counts.return_value = [("WARN", 1)]
                    mock_get_deps.return_value = ["some arbitrary val representing a plugin"]  # Simulate successful execution
                    result = runner.invoke(cli.cli, ["get-deps", "-f", "mkdocs.yml"], catch_exceptions=False)

                    mock_get_deps.assert_called_once()
                    self.assertEqual(result.exit_code, 1)


    def test__load_hook_fail_spec_from_file(self):
        """Test improperly installed or configured hook with mocked importlib.util."""
        with patch('importlib.util') as mock_import_util:
            mock_import_util.spec_from_file_location.return_value = None # Simulate failure to load spec
            hooks = Hooks("some_fake_plugin_key")
            with self.assertRaises(ValidationError):
                hooks._load_hook("non_existent_hook", "non_existent_hook.py")

    def test__load_hook_fail_module_from_spec(self):
        """Test improperly installed or configured hook with mocked importlib.util."""
        with patch('importlib.util') as mock_import_util:
            mock_spec = MagicMock()
            mock_spec.loader = None  # Simulate missing loader
            mock_import_util.spec_from_file_location.return_value = mock_spec
            mock_import_util.module_from_spec.return_value = MagicMock()  # Simulate failure to load module
            hooks = Hooks("some_fake_plugin_key")
            with self.assertRaises(ValidationError):
                hooks._load_hook("non_existent_hook", "non_existent_hook.py")

    def test_load_invalid_plugin(self):
        """Test loading an invalid plugin with mocked plugin cache."""
        dummy_plugin_cache = {
            "valid_plugin": MagicMock(),
            "invalid_plugin": object()  # Simulate invalid plugin (not a subclass of BasePlugin)
        }
        plugins_config_option = Plugins()
        plugins_config_option.plugin_cache = dummy_plugin_cache
        with self.assertRaises(ValidationError):
            plugins_config_option.load_plugin("invalid_plugin", {})

    def test__is_cwd_git_repo_no_git(self):
        """Test _is_cwd_git_repo function when git is not installed or on PATH."""
        import logging
        logger = logging.getLogger('mkdocs.commands.gh_deploy')
        with patch.object(logger, 'error') as mock_log_error, \
            patch('subprocess.Popen') as mock_popen:
                from mkdocs.commands.gh_deploy import _is_cwd_git_repo
                mock_popen.side_effect = FileNotFoundError  # Simulate git not found
                with self.assertRaises(Abort):
                    _is_cwd_git_repo()
                mock_log_error.assert_called_once_with("Could not find git - is it installed and on your path?")

    @patch('mkdocs.commands.serve.build')
    @patch('mkdocs.commands.serve.load_config')
    def test_serve_function(self, mock_load_config, mock_build):
        """Test serve function with mocked dependencies."""
        expected_open_in_browser_val = False
        expected_site_url = 'http://somehost:8000/'
        expected_fake_dir = '/fake/dir'
        mock_config = MagicMock(dev_addr=('somehost', 8000),
                                site_url=expected_site_url,
                                watch=['mkdocs'])
        mock_load_config.return_value = mock_config
        mock_server = MagicMock()

        import logging
        logger = logging.getLogger('mkdocs.commands.serve')
        with patch.object(logger, 'info') as mock_log_info, \
            patch('tempfile.mkdtemp', return_value=expected_fake_dir), \
            patch('mkdocs.commands.serve.LiveReloadServer', return_value=mock_server), \
            patch('mkdocs.commands.serve.isdir', return_value=True), \
            patch('shutil.rmtree') as mock_rmtree:
                from mkdocs.commands.serve import serve
                serve(config_file='mkdocs.yml',
                    livereload=False,
                    build_type='clean',
                    watch_theme=True,
                    watch=['docs/'],
                    open_in_browser=expected_open_in_browser_val
                    )
                mock_load_config.assert_called_once()
                mock_config.plugins.on_startup.assert_called_once_with(command='build', dirty=False)
                self.assertEqual(mock_config.site_url, expected_site_url)
                mock_log_info.assert_called_once_with("Building documentation...")
                mock_build.assert_called_once_with(mock_config, serve_url=None, dirty=False)
                mock_server.serve.assert_called_once_with(open_in_browser=expected_open_in_browser_val)
                mock_server.shutdown.assert_called_once()
                mock_config.plugins.on_shutdown.assert_called_once()
                mock_rmtree.assert_called_once_with(expected_fake_dir)

    @patch('mkdocs.commands.serve.build')
    @patch('mkdocs.commands.serve.load_config')
    def test_serve_function_with_livereload(self, mock_load_config, mock_build):
        """Test serve function with mocked dependencies."""
        expected_open_in_browser_val = False
        expected_site_url = 'http://somehost:8000/'
        expected_fake_dir = '/fake/dir'
        mock_config = MagicMock(dev_addr=('somehost', 8000),
                                site_url=expected_site_url,
                                watch=['mkdocs'],
                                docs_dir='docs/',
                                config_file_path='mkdocs.yml')
        mock_config.theme.dirs = ['some_theme_dir']
        mock_server = MagicMock()
        mock_config.plugins.on_serve.return_value = mock_server
        mock_load_config.return_value = mock_config

        import logging
        logger = logging.getLogger('mkdocs.commands.serve')
        with patch.object(logger, 'info') as mock_log_info, \
            patch('tempfile.mkdtemp', return_value=expected_fake_dir), \
            patch('mkdocs.commands.serve.LiveReloadServer', return_value=mock_server), \
            patch('mkdocs.commands.serve.isdir', return_value=True), \
            patch('shutil.rmtree') as mock_rmtree:
                from mkdocs.commands.serve import serve
                serve(config_file='mkdocs.yml',
                    livereload=True,
                    build_type='clean',
                    watch_theme=True,
                    watch=['passed-in-dir/'],
                    open_in_browser=expected_open_in_browser_val
                    )
                mock_load_config.assert_called_once()
                mock_config.plugins.on_startup.assert_called_once_with(command='build', dirty=False)
                self.assertEqual(mock_config.site_url, expected_site_url)
                mock_log_info.assert_called_once_with("Building documentation...")
                mock_build.assert_called_once_with(mock_config, serve_url=None, dirty=False)
                mock_server.watch.assert_has_calls([call(i) for i in ['docs/', 'mkdocs.yml', 'some_theme_dir', 'mkdocs', 'passed-in-dir/']])
                mock_config.plugins.on_serve.assert_called_once()
                mock_server.serve.assert_called_once_with(open_in_browser=expected_open_in_browser_val)
                mock_server.shutdown.assert_called_once()
                mock_config.plugins.on_shutdown.assert_called_once()
                mock_rmtree.assert_called_once_with(expected_fake_dir)

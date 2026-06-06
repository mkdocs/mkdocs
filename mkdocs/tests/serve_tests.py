import io
import os
import unittest
from unittest import mock

from mkdocs.commands import serve
from mkdocs.tests.base import change_dir, tempdir


class FakeLiveReloadServer:
    rebuild_hook = None

    def __init__(self, *, builder, host, port, root, mount_path):
        self.builder = builder
        self.error_handler = None

    def watch(self, path):
        pass

    def serve(self, open_in_browser=False):
        rebuild_hook = type(self).rebuild_hook
        if rebuild_hook:
            rebuild_hook()
        self.builder()

    def shutdown(self):
        pass


class ServeTests(unittest.TestCase):
    def tearDown(self):
        FakeLiveReloadServer.rebuild_hook = None

    @mock.patch('mkdocs.commands.serve.LiveReloadServer', FakeLiveReloadServer)
    @mock.patch('mkdocs.commands.serve.build')
    @tempdir(
        files={
            'docs/index.md': '# Home\n',
        }
    )
    def test_serve_reuses_stdin_config_for_livereload(self, temp_dir, mock_build):
        config_file = io.BytesIO(b'site_name: Stdin Site\n')

        with change_dir(temp_dir):
            serve.serve(config_file=config_file)

        self.assertEqual(
            [call.args[0].site_name for call in mock_build.call_args_list],
            ['Stdin Site', 'Stdin Site'],
        )

    @mock.patch('mkdocs.commands.serve.LiveReloadServer', FakeLiveReloadServer)
    @mock.patch('mkdocs.commands.serve.build')
    @tempdir(
        files={
            'docs/index.md': '# Home\n',
            'mkdocs.yml': 'site_name: First Site\n',
        }
    )
    def test_serve_reloads_named_config_file_for_livereload(self, temp_dir, mock_build):
        def update_config():
            with open(os.path.join(temp_dir, 'mkdocs.yml'), 'w', encoding='utf-8') as f:
                f.write('site_name: Second Site\n')

        FakeLiveReloadServer.rebuild_hook = update_config

        with change_dir(temp_dir):
            with open('mkdocs.yml', 'rb') as config_file:
                serve.serve(config_file=config_file)

        self.assertEqual(
            [call.args[0].site_name for call in mock_build.call_args_list],
            ['First Site', 'Second Site'],
        )

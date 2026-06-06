#!/usr/bin/env python

import io
import unittest
from pathlib import Path
from unittest import mock

from mkdocs.commands import serve
from mkdocs.tests.base import tempdir


class NonSeekableStdin(io.BytesIO):
    name = '<stdin>'

    def seek(self, *args, **kwargs):
        raise OSError


class FakeLiveReloadServer:
    instance = None

    def __init__(self, builder, **kwargs):
        self.builder = builder
        self.watch_calls = []
        self.error_handler = None
        FakeLiveReloadServer.instance = self

    def watch(self, path, *args, **kwargs):
        self.watch_calls.append(path)

    def serve(self, **kwargs):
        self.builder()

    def shutdown(self):
        pass


class ServeTests(unittest.TestCase):
    @tempdir({'docs/index.md': '# Home'})
    def test_serve_reloads_config_read_from_stdin(self, docs_dir):
        docs_dir_path = Path(docs_dir, 'docs').as_posix()
        config_contents = f'site_name: Test\ndocs_dir: "{docs_dir_path}"\n'.encode()
        config_file = NonSeekableStdin(config_contents)
        FakeLiveReloadServer.instance = None

        with mock.patch('mkdocs.commands.serve.LiveReloadServer', FakeLiveReloadServer):
            with mock.patch('mkdocs.commands.serve.build') as build_mock:
                serve.serve(config_file=config_file, open_in_browser=False)

        self.assertIsNotNone(FakeLiveReloadServer.instance)
        self.assertEqual(build_mock.call_count, 2)
        self.assertEqual(
            [call.args[0].site_name for call in build_mock.call_args_list],
            ['Test', 'Test'],
        )
        self.assertNotIn('<stdin>', FakeLiveReloadServer.instance.watch_calls)


if __name__ == '__main__':
    unittest.main()

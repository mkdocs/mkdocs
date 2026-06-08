from __future__ import annotations

import unittest
from pathlib import Path
from unittest import mock

from mkdocs.commands import serve
from mkdocs.tests.base import dedent, tempdir


class FakeLiveReloadServer:
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def serve(self, **kwargs):
        self.kwargs['builder']()

    def shutdown(self):
        pass


class ServeTests(unittest.TestCase):
    @tempdir(
        {
            'docs/index.md': '# Home',
            'mkdocs.yml': dedent(
                """
                site_name: Example
                docs_dir: docs
                site_url: https://mydomain.de/
                use_directory_urls: false
                """
            ),
        }
    )
    def test_serve_preserves_explicit_site_url(self, project_dir):
        build_calls = []

        def fake_build(config, **kwargs):
            build_calls.append((config.site_url, kwargs['serve_url']))

        build_patch = mock.patch.object(serve, 'build', fake_build)
        server_patch = mock.patch.object(serve, 'LiveReloadServer', FakeLiveReloadServer)
        with build_patch, server_patch:
            serve.serve(
                config_file=str(Path(project_dir, 'mkdocs.yml')),
                livereload=False,
                dev_addr='0.0.0.0:8000',
            )

        self.assertEqual(
            build_calls,
            [
                ('https://mydomain.de/', 'http://0.0.0.0:8000/'),
                ('https://mydomain.de/', 'http://0.0.0.0:8000/'),
            ],
        )

    @tempdir(
        {
            'docs/index.md': '# Home',
            'mkdocs.yml': dedent(
                """
                site_name: Example
                docs_dir: docs
                use_directory_urls: false
                """
            ),
        }
    )
    def test_serve_uses_dev_url_when_site_url_is_unset(self, project_dir):
        build_calls = []

        def fake_build(config, **kwargs):
            build_calls.append((config.site_url, kwargs['serve_url']))

        build_patch = mock.patch.object(serve, 'build', fake_build)
        server_patch = mock.patch.object(serve, 'LiveReloadServer', FakeLiveReloadServer)
        with build_patch, server_patch:
            serve.serve(
                config_file=str(Path(project_dir, 'mkdocs.yml')),
                livereload=False,
                dev_addr='0.0.0.0:8000',
            )

        self.assertEqual(
            build_calls,
            [
                ('http://0.0.0.0:8000/', 'http://0.0.0.0:8000/'),
                ('http://0.0.0.0:8000/', 'http://0.0.0.0:8000/'),
            ],
        )

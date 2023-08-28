#!/usr/bin/env python
from __future__ import annotations

import contextlib
import io
import os.path
import re
import textwrap
import unittest
from pathlib import Path
from typing import TYPE_CHECKING
from unittest import mock

import markdown.preprocessors

from mkdocs.commands import build
from mkdocs.config import base
from mkdocs.exceptions import PluginError
from mkdocs.livereload import LiveReloadServer
from mkdocs.structure.files import File, Files
from mkdocs.structure.nav import get_navigation
from mkdocs.structure.pages import Page
from mkdocs.tests.base import PathAssertionMixin, load_config, tempdir
from mkdocs.utils import meta

if TYPE_CHECKING:
    from mkdocs.config.defaults import MkDocsConfig


def build_page(title, path, config, md_src=''):
    """Helper which returns a Page object."""

    files = Files([File(path, config.docs_dir, config.site_dir, config.use_directory_urls)])
    page = Page(title, list(files)[0], config)
    # Fake page.read_source()
    page.markdown, page.meta = meta.get_data(md_src)
    return page, files


def testing_server(root, builder=lambda: None, mount_path="/"):
    with mock.patch("socket.socket"):
        return LiveReloadServer(
            builder, host="localhost", port=123, root=root, mount_path=mount_path
        )


class BuildTests(PathAssertionMixin, unittest.TestCase):
    def _get_env_with_null_translations(self, config):
        env = config.theme.get_env()
        env.add_extension('jinja2.ext.i18n')
        env.install_null_translations()
        return env

    # Test build.get_context

    def test_context_base_url_homepage(self):
        nav_cfg = [
            {'Home': 'index.md'},
        ]
        cfg = load_config(nav=nav_cfg, use_directory_urls=False)
        fs = [File('index.md', cfg.docs_dir, cfg.site_dir, cfg.use_directory_urls)]
        files = Files(fs)
        nav = get_navigation(files, cfg)
        context = build.get_context(nav, files, cfg, nav.pages[0])
        self.assertEqual(context['base_url'], '.')

    def test_context_base_url_homepage_use_directory_urls(self):
        nav_cfg = [
            {'Home': 'index.md'},
        ]
        cfg = load_config(nav=nav_cfg)
        fs = [File('index.md', cfg.docs_dir, cfg.site_dir, cfg.use_directory_urls)]
        files = Files(fs)
        nav = get_navigation(files, cfg)
        context = build.get_context(nav, files, cfg, nav.pages[0])
        self.assertEqual(context['base_url'], '.')

    def test_context_base_url_nested_page(self):
        nav_cfg = [
            {'Home': 'index.md'},
            {'Nested': 'foo/bar.md'},
        ]
        cfg = load_config(nav=nav_cfg, use_directory_urls=False)
        fs = [
            File('index.md', cfg.docs_dir, cfg.site_dir, cfg.use_directory_urls),
            File('foo/bar.md', cfg.docs_dir, cfg.site_dir, cfg.use_directory_urls),
        ]
        files = Files(fs)
        nav = get_navigation(files, cfg)
        context = build.get_context(nav, files, cfg, nav.pages[1])
        self.assertEqual(context['base_url'], '..')

    def test_context_base_url_nested_page_use_directory_urls(self):
        nav_cfg = [
            {'Home': 'index.md'},
            {'Nested': 'foo/bar.md'},
        ]
        cfg = load_config(nav=nav_cfg)
        fs = [
            File('index.md', cfg.docs_dir, cfg.site_dir, cfg.use_directory_urls),
            File('foo/bar.md', cfg.docs_dir, cfg.site_dir, cfg.use_directory_urls),
        ]
        files = Files(fs)
        nav = get_navigation(files, cfg)
        context = build.get_context(nav, files, cfg, nav.pages[1])
        self.assertEqual(context['base_url'], '../..')

    def test_context_base_url_relative_no_page(self):
        cfg = load_config(use_directory_urls=False)
        context = build.get_context(mock.Mock(), mock.Mock(), cfg, base_url='..')
        self.assertEqual(context['base_url'], '..')

    def test_context_base_url_relative_no_page_use_directory_urls(self):
        cfg = load_config()
        context = build.get_context(mock.Mock(), mock.Mock(), cfg, base_url='..')
        self.assertEqual(context['base_url'], '..')

    def test_context_base_url_absolute_no_page(self):
        cfg = load_config(use_directory_urls=False)
        context = build.get_context(mock.Mock(), mock.Mock(), cfg, base_url='/')
        self.assertEqual(context['base_url'], '/')

    def test_context_base_url__absolute_no_page_use_directory_urls(self):
        cfg = load_config()
        context = build.get_context(mock.Mock(), mock.Mock(), cfg, base_url='/')
        self.assertEqual(context['base_url'], '/')

    def test_context_base_url_absolute_nested_no_page(self):
        cfg = load_config(use_directory_urls=False)
        context = build.get_context(mock.Mock(), mock.Mock(), cfg, base_url='/foo/')
        self.assertEqual(context['base_url'], '/foo/')

    def test_context_base_url__absolute_nested_no_page_use_directory_urls(self):
        cfg = load_config()
        context = build.get_context(mock.Mock(), mock.Mock(), cfg, base_url='/foo/')
        self.assertEqual(context['base_url'], '/foo/')

    def test_context_extra_css_js_from_homepage(self):
        nav_cfg = [
            {'Home': 'index.md'},
        ]
        cfg = load_config(
            nav=nav_cfg,
            extra_css=['style.css'],
            extra_javascript=['script.js'],
            use_directory_urls=False,
        )
        fs = [File('index.md', cfg.docs_dir, cfg.site_dir, cfg.use_directory_urls)]
        files = Files(fs)
        nav = get_navigation(files, cfg)
        context = build.get_context(nav, files, cfg, nav.pages[0])
        self.assertEqual(context['extra_css'], ['style.css'])
        self.assertEqual(context['extra_javascript'], ['script.js'])

    def test_context_extra_css_js_from_nested_page(self):
        nav_cfg = [
            {'Home': 'index.md'},
            {'Nested': 'foo/bar.md'},
        ]
        cfg = load_config(
            nav=nav_cfg,
            extra_css=['style.css'],
            extra_javascript=['script.js'],
            use_directory_urls=False,
        )
        fs = [
            File('index.md', cfg.docs_dir, cfg.site_dir, cfg.use_directory_urls),
            File('foo/bar.md', cfg.docs_dir, cfg.site_dir, cfg.use_directory_urls),
        ]
        files = Files(fs)
        nav = get_navigation(files, cfg)
        context = build.get_context(nav, files, cfg, nav.pages[1])
        self.assertEqual(context['extra_css'], ['../style.css'])
        self.assertEqual(context['extra_javascript'], ['../script.js'])

    def test_context_extra_css_js_from_nested_page_use_directory_urls(self):
        nav_cfg = [
            {'Home': 'index.md'},
            {'Nested': 'foo/bar.md'},
        ]
        cfg = load_config(
            nav=nav_cfg,
            extra_css=['style.css'],
            extra_javascript=['script.js'],
        )
        fs = [
            File('index.md', cfg.docs_dir, cfg.site_dir, cfg.use_directory_urls),
            File('foo/bar.md', cfg.docs_dir, cfg.site_dir, cfg.use_directory_urls),
        ]
        files = Files(fs)
        nav = get_navigation(files, cfg)
        context = build.get_context(nav, files, cfg, nav.pages[1])
        self.assertEqual(context['extra_css'], ['../../style.css'])
        self.assertEqual(context['extra_javascript'], ['../../script.js'])

    # TODO: This shouldn't pass on Linux
    # @unittest.skipUnless(sys.platform.startswith("win"), "requires Windows")
    def test_context_extra_css_path_warning(self):
        nav_cfg = [
            {'Home': 'index.md'},
        ]
        cfg = load_config(
            nav=nav_cfg,
            extra_css=['assets\\style.css'],
            use_directory_urls=False,
        )
        fs = [File('index.md', cfg.docs_dir, cfg.site_dir, cfg.use_directory_urls)]
        files = Files(fs)
        nav = get_navigation(files, cfg)
        with self.assertLogs('mkdocs') as cm:
            context = build.get_context(nav, files, cfg, nav.pages[0])
        self.assertEqual(context['extra_css'], ['assets/style.css'])
        self.assertEqual(
            '\n'.join(cm.output),
            "WARNING:mkdocs.utils:Path 'assets\\style.css' uses OS-specific separator '\\'. "
            "That will be unsupported in a future release. Please change it to '/'.",
        )

    def test_context_extra_css_js_no_page(self):
        cfg = load_config(extra_css=['style.css'], extra_javascript=['script.js'])
        context = build.get_context(mock.Mock(), mock.Mock(), cfg, base_url='..')
        self.assertEqual(context['extra_css'], ['../style.css'])
        self.assertEqual(context['extra_javascript'], ['../script.js'])

    def test_extra_context(self):
        cfg = load_config(extra={'a': 1})
        context = build.get_context(mock.Mock(), mock.Mock(), cfg)
        self.assertEqual(context['config']['extra']['a'], 1)

    # Test build._build_theme_template

    @mock.patch('mkdocs.utils.write_file')
    @mock.patch('mkdocs.commands.build._build_template', return_value='some content')
    def test_build_theme_template(self, mock_build_template, mock_write_file):
        cfg = load_config()
        env = cfg.theme.get_env()
        build._build_theme_template('main.html', env, mock.Mock(), cfg, mock.Mock())
        mock_write_file.assert_called_once()
        mock_build_template.assert_called_once()

    @mock.patch('mkdocs.utils.write_file')
    @mock.patch('mkdocs.commands.build._build_template', return_value='some content')
    @mock.patch('gzip.GzipFile')
    @tempdir()
    def test_build_sitemap_template(
        self, site_dir, mock_gzip_gzipfile, mock_build_template, mock_write_file
    ):
        cfg = load_config(site_dir=site_dir)
        env = cfg.theme.get_env()
        build._build_theme_template('sitemap.xml', env, mock.Mock(), cfg, mock.Mock())
        mock_write_file.assert_called_once()
        mock_build_template.assert_called_once()
        mock_gzip_gzipfile.assert_called_once()

    @mock.patch('mkdocs.utils.write_file')
    @mock.patch('mkdocs.commands.build._build_template', return_value='')
    def test_skip_missing_theme_template(self, mock_build_template, mock_write_file):
        cfg = load_config()
        env = cfg.theme.get_env()
        with self.assertLogs('mkdocs') as cm:
            build._build_theme_template('missing.html', env, mock.Mock(), cfg, mock.Mock())
        self.assertEqual(
            '\n'.join(cm.output),
            "WARNING:mkdocs.commands.build:Template skipped: 'missing.html' not found in theme directories.",
        )
        mock_write_file.assert_not_called()
        mock_build_template.assert_not_called()

    @mock.patch('mkdocs.utils.write_file')
    @mock.patch('mkdocs.commands.build._build_template', return_value='')
    def test_skip_theme_template_empty_output(self, mock_build_template, mock_write_file):
        cfg = load_config()
        env = cfg.theme.get_env()
        with self.assertLogs('mkdocs') as cm:
            build._build_theme_template('main.html', env, mock.Mock(), cfg, mock.Mock())
        self.assertEqual(
            '\n'.join(cm.output),
            "INFO:mkdocs.commands.build:Template skipped: 'main.html' generated empty output.",
        )
        mock_write_file.assert_not_called()
        mock_build_template.assert_called_once()

    # Test build._build_extra_template

    @tempdir()
    @mock.patch('mkdocs.commands.build.open', mock.mock_open(read_data='template content'))
    def test_build_extra_template(self, site_dir):
        cfg = load_config(site_dir=site_dir)
        fs = [File('foo.html', cfg.docs_dir, cfg.site_dir, cfg.use_directory_urls)]
        files = Files(fs)
        build._build_extra_template('foo.html', files, cfg, mock.Mock())

    @mock.patch('mkdocs.commands.build.open', mock.mock_open(read_data='template content'))
    def test_skip_missing_extra_template(self):
        cfg = load_config()
        fs = [File('foo.html', cfg.docs_dir, cfg.site_dir, cfg.use_directory_urls)]
        files = Files(fs)
        with self.assertLogs('mkdocs') as cm:
            build._build_extra_template('missing.html', files, cfg, mock.Mock())
        self.assertEqual(
            '\n'.join(cm.output),
            "WARNING:mkdocs.commands.build:Template skipped: 'missing.html' not found in docs_dir.",
        )

    @mock.patch('mkdocs.commands.build.open', side_effect=OSError('Error message.'))
    def test_skip_ioerror_extra_template(self, mock_open):
        cfg = load_config()
        fs = [File('foo.html', cfg.docs_dir, cfg.site_dir, cfg.use_directory_urls)]
        files = Files(fs)
        with self.assertLogs('mkdocs') as cm:
            build._build_extra_template('foo.html', files, cfg, mock.Mock())
        self.assertEqual(
            '\n'.join(cm.output),
            "WARNING:mkdocs.commands.build:Error reading template 'foo.html': Error message.",
        )

    @mock.patch('mkdocs.commands.build.open', mock.mock_open(read_data=''))
    def test_skip_extra_template_empty_output(self):
        cfg = load_config()
        fs = [File('foo.html', cfg.docs_dir, cfg.site_dir, cfg.use_directory_urls)]
        files = Files(fs)
        with self.assertLogs('mkdocs') as cm:
            build._build_extra_template('foo.html', files, cfg, mock.Mock())
        self.assertEqual(
            '\n'.join(cm.output),
            "INFO:mkdocs.commands.build:Template skipped: 'foo.html' generated empty output.",
        )

    # Test build._populate_page

    @tempdir(files={'index.md': 'page content'})
    def test_populate_page(self, docs_dir):
        cfg = load_config(docs_dir=docs_dir)
        file = File('index.md', cfg.docs_dir, cfg.site_dir, cfg.use_directory_urls)
        page = Page('Foo', file, cfg)
        build._populate_page(page, cfg, Files([file]))
        self.assertEqual(page.content, '<p>page content</p>')

    @tempdir(files={'testing.html': '<p>page content</p>'})
    def test_populate_page_dirty_modified(self, site_dir):
        cfg = load_config(site_dir=site_dir)
        file = File('testing.md', cfg.docs_dir, cfg.site_dir, cfg.use_directory_urls)
        page = Page('Foo', file, cfg)
        build._populate_page(page, cfg, Files([file]), dirty=True)
        self.assertTrue(page.markdown.startswith('# Welcome to MkDocs'))
        self.assertTrue(
            page.content.startswith('<h1 id="welcome-to-mkdocs">Welcome to MkDocs</h1>')
        )

    @tempdir(files={'index.md': 'page content'})
    @tempdir(files={'index.html': '<p>page content</p>'})
    def test_populate_page_dirty_not_modified(self, site_dir, docs_dir):
        cfg = load_config(docs_dir=docs_dir, site_dir=site_dir)
        file = File('index.md', cfg.docs_dir, cfg.site_dir, cfg.use_directory_urls)
        page = Page('Foo', file, cfg)
        build._populate_page(page, cfg, Files([file]), dirty=True)
        # Content is empty as file read was skipped
        self.assertEqual(page.markdown, None)
        self.assertEqual(page.content, None)

    @tempdir(files={'index.md': 'new page content'})
    @mock.patch('mkdocs.structure.pages.open', side_effect=OSError('Error message.'))
    def test_populate_page_read_error(self, docs_dir, mock_open):
        cfg = load_config(docs_dir=docs_dir)
        file = File('missing.md', cfg.docs_dir, cfg.site_dir, cfg.use_directory_urls)
        page = Page('Foo', file, cfg)
        with self.assertLogs('mkdocs') as cm:
            with self.assertRaises(OSError):
                build._populate_page(page, cfg, Files([file]))
        self.assertEqual(
            cm.output,
            [
                'ERROR:mkdocs.structure.pages:File not found: missing.md',
                "ERROR:mkdocs.commands.build:Error reading page 'missing.md': Error message.",
            ],
        )
        mock_open.assert_called_once()

    @tempdir(files={'index.md': 'page content'})
    def test_populate_page_read_plugin_error(self, docs_dir):
        def on_page_markdown(*args, **kwargs):
            raise PluginError('Error message.')

        cfg = load_config(docs_dir=docs_dir)
        cfg.plugins.events['page_markdown'].append(on_page_markdown)

        file = File('index.md', cfg.docs_dir, cfg.site_dir, cfg.use_directory_urls)
        page = Page('Foo', file, cfg)
        with self.assertLogs('mkdocs') as cm:
            with self.assertRaises(PluginError):
                build._populate_page(page, cfg, Files([file]))
        self.assertEqual(
            '\n'.join(cm.output),
            "ERROR:mkdocs.commands.build:Error reading page 'index.md':",
        )

    # Test build._build_page

    @tempdir()
    def test_build_page(self, site_dir):
        cfg = load_config(site_dir=site_dir, nav=['index.md'])
        fs = [File('index.md', cfg.docs_dir, cfg.site_dir, cfg.use_directory_urls)]
        files = Files(fs)
        nav = get_navigation(files, cfg)
        page = files.documentation_pages()[0].page
        # Fake populate page
        page.title = 'Title'
        page.markdown = 'page content'
        page.content = '<p>page content</p>'
        build._build_page(page, cfg, files, nav, self._get_env_with_null_translations(cfg))
        self.assertPathIsFile(site_dir, 'index.html')

    @tempdir()
    @mock.patch('jinja2.environment.Template.render', return_value='')
    def test_build_page_empty(self, site_dir, render_mock):
        cfg = load_config(site_dir=site_dir, nav=['index.md'])
        fs = [File('index.md', cfg.docs_dir, cfg.site_dir, cfg.use_directory_urls)]
        files = Files(fs)
        nav = get_navigation(files, cfg)
        with self.assertLogs('mkdocs') as cm:
            build._build_page(
                files.documentation_pages()[0].page, cfg, files, nav, cfg.theme.get_env()
            )
        self.assertEqual(
            '\n'.join(cm.output),
            "INFO:mkdocs.commands.build:Page skipped: 'index.md'. Generated empty output.",
        )
        self.assertPathNotExists(site_dir, 'index.html')
        render_mock.assert_called_once()

    @tempdir(files={'index.md': 'page content'})
    @tempdir(files={'index.html': '<p>page content</p>'})
    @mock.patch('mkdocs.utils.write_file')
    def test_build_page_dirty_modified(self, site_dir, docs_dir, mock_write_file):
        cfg = load_config(docs_dir=docs_dir, site_dir=site_dir, nav=['index.md'])
        fs = [File('index.md', cfg.docs_dir, cfg.site_dir, cfg.use_directory_urls)]
        files = Files(fs)
        nav = get_navigation(files, cfg)
        page = files.documentation_pages()[0].page
        # Fake populate page
        page.title = 'Title'
        page.markdown = 'new page content'
        page.content = '<p>new page content</p>'
        build._build_page(
            page, cfg, files, nav, self._get_env_with_null_translations(cfg), dirty=True
        )
        mock_write_file.assert_not_called()

    @tempdir(files={'testing.html': '<p>page content</p>'})
    @mock.patch('mkdocs.utils.write_file')
    def test_build_page_dirty_not_modified(self, site_dir, mock_write_file):
        cfg = load_config(site_dir=site_dir, nav=['testing.md'])
        fs = [File('testing.md', cfg.docs_dir, cfg.site_dir, cfg.use_directory_urls)]
        files = Files(fs)
        nav = get_navigation(files, cfg)
        page = files.documentation_pages()[0].page
        # Fake populate page
        page.title = 'Title'
        page.markdown = 'page content'
        page.content = '<p>page content</p>'
        build._build_page(
            page, cfg, files, nav, self._get_env_with_null_translations(cfg), dirty=True
        )
        mock_write_file.assert_called_once()

    @tempdir()
    def test_build_page_custom_template(self, site_dir):
        cfg = load_config(site_dir=site_dir, nav=['index.md'])
        fs = [File('index.md', cfg.docs_dir, cfg.site_dir, cfg.use_directory_urls)]
        files = Files(fs)
        nav = get_navigation(files, cfg)
        page = files.documentation_pages()[0].page
        # Fake populate page
        page.title = 'Title'
        page.meta = {'template': '404.html'}
        page.markdown = 'page content'
        page.content = '<p>page content</p>'
        build._build_page(page, cfg, files, nav, self._get_env_with_null_translations(cfg))
        self.assertPathIsFile(site_dir, 'index.html')

    @tempdir()
    @mock.patch('mkdocs.utils.write_file', side_effect=OSError('Error message.'))
    def test_build_page_error(self, site_dir, mock_write_file):
        cfg = load_config(site_dir=site_dir, nav=['index.md'])
        fs = [File('index.md', cfg.docs_dir, cfg.site_dir, cfg.use_directory_urls)]
        files = Files(fs)
        nav = get_navigation(files, cfg)
        page = files.documentation_pages()[0].page
        # Fake populate page
        page.title = 'Title'
        page.markdown = 'page content'
        page.content = '<p>page content</p>'
        with self.assertLogs('mkdocs') as cm:
            with self.assertRaises(OSError):
                build._build_page(page, cfg, files, nav, self._get_env_with_null_translations(cfg))
        self.assertEqual(
            '\n'.join(cm.output),
            "ERROR:mkdocs.commands.build:Error building page 'index.md': Error message.",
        )
        mock_write_file.assert_called_once()

    @tempdir()
    def test_build_page_plugin_error(self, site_dir):
        def on_page_context(*args, **kwargs):
            raise PluginError('Error message.')

        cfg = load_config(site_dir=site_dir, nav=['index.md'])
        cfg.plugins.events['page_context'].append(on_page_context)
        fs = [File('index.md', cfg.docs_dir, cfg.site_dir, cfg.use_directory_urls)]
        files = Files(fs)
        nav = get_navigation(files, cfg)
        page = files.documentation_pages()[0].page
        # Fake populate page
        page.title = 'Title'
        page.markdown = 'page content'
        page.content = '<p>page content</p>'
        with self.assertLogs('mkdocs') as cm:
            with self.assertRaises(PluginError):
                build._build_page(page, cfg, files, nav, cfg.theme.get_env())
        self.assertEqual(
            '\n'.join(cm.output),
            "ERROR:mkdocs.commands.build:Error building page 'index.md':",
        )

    # Test build.build

    @tempdir(
        files={
            'index.md': 'page content',
            'empty.md': '',
            'img.jpg': '',
            'static.html': 'content',
            '.hidden': 'content',
            '.git/hidden': 'content',
        }
    )
    @tempdir()
    def test_copying_media(self, site_dir, docs_dir):
        cfg = load_config(docs_dir=docs_dir, site_dir=site_dir)
        build.build(cfg)

        # Verify that only non-empty md file (converted to html), static HTML file and image are copied.
        self.assertPathIsFile(site_dir, 'index.html')
        self.assertPathIsFile(site_dir, 'img.jpg')
        self.assertPathIsFile(site_dir, 'static.html')
        self.assertPathNotExists(site_dir, 'empty.md')
        self.assertPathNotExists(site_dir, '.hidden')
        self.assertPathNotExists(site_dir, '.git/hidden')

    @tempdir(files={'index.md': 'page content'})
    @tempdir()
    def test_copy_theme_files(self, site_dir, docs_dir):
        cfg = load_config(docs_dir=docs_dir, site_dir=site_dir)
        build.build(cfg)

        # Verify only theme media are copied, not templates, Python or localization files.
        self.assertPathIsFile(site_dir, 'index.html')
        self.assertPathIsFile(site_dir, '404.html')
        self.assertPathIsDir(site_dir, 'js')
        self.assertPathIsDir(site_dir, 'css')
        self.assertPathIsDir(site_dir, 'img')
        self.assertPathIsDir(site_dir, 'fonts')
        self.assertPathNotExists(site_dir, '__init__.py')
        self.assertPathNotExists(site_dir, '__init__.pyc')
        self.assertPathNotExists(site_dir, 'base.html')
        self.assertPathNotExists(site_dir, 'content.html')
        self.assertPathNotExists(site_dir, 'main.html')
        self.assertPathNotExists(site_dir, 'locales')

    @contextlib.contextmanager
    def _assert_build_logs(self, expected):
        with self.assertLogs('mkdocs') as cm:
            yield
        msgs = [f'{r.levelname}:{r.message}' for r in cm.records]
        if msgs and msgs[0].startswith('INFO:Cleaning site directory'):
            del msgs[0]
        if msgs and msgs[0].startswith('INFO:Building documentation to directory'):
            del msgs[0]
        if msgs and msgs[-1].startswith('INFO:Documentation built'):
            del msgs[-1]
        self.assertEqual('\n'.join(msgs), textwrap.dedent(expected).strip('\n'))

    @tempdir(
        files={
            'test/foo.md': 'page1 content, [bar](bar.md)',
            'test/bar.md': 'page2 content, [baz](baz.md)',
            'test/baz.md': 'page3 content, [foo](foo.md)',
            '.zoo.md': 'page4 content',
        }
    )
    @tempdir()
    def test_exclude_pages_with_invalid_links(self, site_dir, docs_dir):
        cfg = load_config(
            docs_dir=docs_dir,
            site_dir=site_dir,
            use_directory_urls=False,
            exclude_docs='ba*.md',
        )

        with self.subTest(live_server=None):
            expected_logs = '''
                INFO:Doc file 'test/foo.md' contains a link to 'test/bar.md' which is excluded from the built site.
            '''
            with self._assert_build_logs(expected_logs):
                build.build(cfg)
            self.assertPathIsFile(site_dir, 'test', 'foo.html')
            self.assertPathNotExists(site_dir, 'test', 'baz.html')
            self.assertPathNotExists(site_dir, '.zoo.html')

        server = testing_server(site_dir, mount_path='/documentation/')
        with self.subTest(live_server=server):
            expected_logs = '''
                INFO:Doc file 'test/bar.md' contains a link to 'test/baz.md' which is excluded from the built site.
                INFO:Doc file 'test/foo.md' contains a link to 'test/bar.md' which is excluded from the built site.
                INFO:The following pages are being built only for the preview but will be excluded from `mkdocs build` per `exclude_docs`:
                  - http://localhost:123/documentation/.zoo.html
                  - http://localhost:123/documentation/test/bar.html
                  - http://localhost:123/documentation/test/baz.html
            '''
            with self._assert_build_logs(expected_logs):
                build.build(cfg, live_server=server)

            foo_path = Path(site_dir, 'test', 'foo.html')
            self.assertTrue(foo_path.is_file())
            self.assertNotIn('DRAFT', foo_path.read_text())

            baz_path = Path(site_dir, 'test', 'baz.html')
            self.assertPathIsFile(baz_path)
            self.assertIn('DRAFT', baz_path.read_text())

            self.assertPathIsFile(site_dir, '.zoo.html')

    @tempdir(
        files={
            'foo/README.md': 'page1 content',
            'foo/index.md': 'page2 content',
        }
    )
    @tempdir()
    def test_conflicting_readme_and_index(self, site_dir, docs_dir):
        cfg = load_config(docs_dir=docs_dir, site_dir=site_dir, use_directory_urls=False)

        for server in None, testing_server(site_dir):
            with self.subTest(live_server=server):
                expected_logs = '''
                    WARNING:Excluding 'foo/README.md' from the site because it conflicts with 'foo/index.md'.
                '''
                with self._assert_build_logs(expected_logs):
                    build.build(cfg, live_server=server)

                index_path = Path(site_dir, 'foo', 'index.html')
                self.assertPathIsFile(index_path)
                self.assertRegex(index_path.read_text(), r'page2 content')

    @tempdir(
        files={
            'foo/README.md': 'page1 content',
            'foo/index.md': 'page2 content',
        }
    )
    @tempdir()
    def test_exclude_readme_and_index(self, site_dir, docs_dir):
        cfg = load_config(
            docs_dir=docs_dir, site_dir=site_dir, use_directory_urls=False, exclude_docs='index.md'
        )

        for server in None, testing_server(site_dir):
            with self.subTest(live_server=server):
                with self._assert_build_logs(''):
                    build.build(cfg, live_server=server)

                index_path = Path(site_dir, 'foo', 'index.html')
                self.assertPathIsFile(index_path)
                self.assertRegex(index_path.read_text(), r'page1 content')

    @tempdir(
        files={
            'foo.md': 'page1 content',
            'bar.md': 'page2 content',
        }
    )
    @tempdir()
    @tempdir()
    def test_plugins_adding_files_and_interacting(self, tmp_dir, site_dir, docs_dir):
        def on_files_1(files: Files, config: MkDocsConfig) -> Files:
            # Plugin 1 generates a file.
            Path(tmp_dir, 'SUMMARY.md').write_text('foo.md\nbar.md\n')
            files.append(File('SUMMARY.md', tmp_dir, config.site_dir, config.use_directory_urls))
            return files

        def on_files_2(files: Files, config: MkDocsConfig) -> None:
            # Plugin 2 reads that file and uses it to configure the nav.
            f = files.get_file_from_path('SUMMARY.md')
            assert f is not None
            config.nav = Path(f.abs_src_path).read_text().splitlines()

        for server in None, testing_server(site_dir):
            for exclude in 'full', 'nav', None:
                with self.subTest(live_server=server, exclude=exclude):
                    cfg = load_config(
                        docs_dir=docs_dir,
                        site_dir=site_dir,
                        use_directory_urls=False,
                        exclude_docs='SUMMARY.md' if exclude == 'full' else '',
                        not_in_nav='SUMMARY.md' if exclude == 'nav' else '',
                    )
                    cfg.plugins.events['files'] += [on_files_1, on_files_2]

                    expected_logs = ''
                    if exclude is None:
                        expected_logs = '''
                            INFO:The following pages exist in the docs directory, but are not included in the "nav" configuration:
                              - SUMMARY.md
                        '''
                    if exclude == 'full' and server:
                        expected_logs = '''
                            INFO:The following pages are being built only for the preview but will be excluded from `mkdocs build` per `exclude_docs`:
                              - http://localhost:123/SUMMARY.html
                        '''
                    with self._assert_build_logs(expected_logs):
                        build.build(cfg, live_server=server)

                    foo_path = Path(site_dir, 'foo.html')
                    self.assertPathIsFile(foo_path)
                    self.assertRegex(
                        foo_path.read_text(),
                        r'href="foo.html"[\s\S]+href="bar.html"',  # Nav order is respected
                    )

                    summary_path = Path(site_dir, 'SUMMARY.html')
                    if exclude == 'full' and not server:
                        self.assertPathNotExists(summary_path)
                    else:
                        self.assertPathExists(summary_path)

    @tempdir(
        files={
            'README.md': 'CONFIG_README\n',
            'docs/foo.md': 'ROOT_FOO\n',
            'docs/test/bar.md': 'TEST_BAR\n',
            'docs/main/foo.md': 'MAIN_FOO\n',
            'docs/main/main.md': (
                '--8<-- "README.md"\n\n'
                '--8<-- "foo.md"\n\n'
                '--8<-- "test/bar.md"\n\n'
                '--8<-- "../foo.md"\n\n'
            ),
        }
    )
    def test_markdown_extension_with_relative(self, config_dir):
        for base_path, expected in {
            '!relative': '''
                <p>(Failed to read 'README.md')</p>
                <p>MAIN_FOO</p>
                <p>(Failed to read 'test/bar.md')</p>
                <p>ROOT_FOO</p>''',
            '!relative $docs_dir': '''
                <p>(Failed to read 'README.md')</p>
                <p>ROOT_FOO</p>
                <p>TEST_BAR</p>
                <p>(Failed to read '../foo.md')</p>''',
            '!relative $config_dir/docs': '''
                <p>(Failed to read 'README.md')</p>
                <p>ROOT_FOO</p>
                <p>TEST_BAR</p>
                <p>(Failed to read '../foo.md')</p>''',
            '!relative $config_dir': '''
                <p>CONFIG_README</p>
                <p>(Failed to read 'foo.md')</p>
                <p>(Failed to read 'test/bar.md')</p>
                <p>(Failed to read '../foo.md')</p>''',
        }.items():
            with self.subTest(base_path=base_path):
                cfg = f'''
                    site_name: test
                    use_directory_urls: false
                    markdown_extensions:
                      - mkdocs.tests.build_tests:
                          base_path: {base_path}
                '''
                config = base.load_config(
                    io.StringIO(cfg), config_file_path=os.path.join(config_dir, 'mkdocs.yml')
                )

                with self._assert_build_logs(''):
                    build.build(config)
                main_path = Path(config_dir, 'site', 'main', 'main.html')
                self.assertTrue(main_path.is_file())
                self.assertIn(textwrap.dedent(expected), main_path.read_text())

    # Test build.site_directory_contains_stale_files

    @tempdir(files=['index.html'])
    def test_site_dir_contains_stale_files(self, site_dir):
        self.assertTrue(build.site_directory_contains_stale_files(site_dir))

    @tempdir()
    def test_not_site_dir_contains_stale_files(self, site_dir):
        self.assertFalse(build.site_directory_contains_stale_files(site_dir))


class _TestPreprocessor(markdown.preprocessors.Preprocessor):
    def __init__(self, base_path: str) -> None:
        self.base_path = base_path

    def run(self, lines: list[str]) -> list[str]:
        for i, line in enumerate(lines):
            m = re.search(r'^--8<-- "(.+)"$', line)
            if m:
                try:
                    lines[i] = Path(self.base_path, m[1]).read_text()
                except OSError:
                    lines[i] = f"(Failed to read {m[1]!r})\n"
        return lines


class _TestExtension(markdown.extensions.Extension):
    def __init__(self, base_path: str) -> None:
        self.base_path = base_path

    def extendMarkdown(self, md: markdown.Markdown) -> None:
        md.preprocessors.register(_TestPreprocessor(self.base_path), "mkdocs_test", priority=32)


makeExtension = _TestExtension

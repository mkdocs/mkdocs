#!/usr/bin/env python


from unittest import mock
import os
import unittest
import tempfile
import shutil
import stat
import datetime
import logging

from mkdocs import utils, exceptions
from mkdocs.structure.files import File
from mkdocs.structure.pages import Page
from mkdocs.tests.base import dedent, load_config, tempdir

BASEYML = """
INHERIT: parent.yml
foo: bar
baz:
    sub1: replaced
    sub3: new
deep1:
    deep2-1:
        deep3-1: replaced
"""
PARENTYML = """
foo: foo
baz:
    sub1: 1
    sub2: 2
deep1:
    deep2-1:
        deep3-1: foo
        deep3-2: bar
    deep2-2: baz
"""


class UtilsTests(unittest.TestCase):
    def test_html_path(self):
        expected_results = {
            'index.md': 'index.html',
            'api-guide.md': 'api-guide/index.html',
            'api-guide/index.md': 'api-guide/index.html',
            'api-guide/testing.md': 'api-guide/testing/index.html',
        }
        for file_path, expected_html_path in expected_results.items():
            html_path = utils.get_html_path(file_path)
            self.assertEqual(html_path, expected_html_path)

    def test_url_path(self):
        expected_results = {
            'index.md': '/',
            'api-guide.md': '/api-guide/',
            'api-guide/index.md': '/api-guide/',
            'api-guide/testing.md': '/api-guide/testing/',
        }
        for file_path, expected_html_path in expected_results.items():
            html_path = utils.get_url_path(file_path)
            self.assertEqual(html_path, expected_html_path)

    def test_is_markdown_file(self):
        expected_results = {
            'index.md': True,
            'index.MARKDOWN': True,
            'index.txt': False,
            'indexmd': False
        }
        for path, expected_result in expected_results.items():
            is_markdown = utils.is_markdown_file(path)
            self.assertEqual(is_markdown, expected_result)

    def test_is_html_file(self):
        expected_results = {
            'index.htm': True,
            'index.HTML': True,
            'index.txt': False,
            'indexhtml': False
        }
        for path, expected_result in expected_results.items():
            is_html = utils.is_html_file(path)
            self.assertEqual(is_html, expected_result)

    def test_get_relative_url(self):
        expected_results = {
            ('foo/bar', 'foo'): 'bar',
            ('foo/bar.txt', 'foo'): 'bar.txt',
            ('foo', 'foo/bar'): '..',
            ('foo', 'foo/bar.txt'): '.',
            ('foo/../../bar', '.'): 'bar',
            ('foo/../../bar', 'foo'): '../bar',
            ('foo//./bar/baz', 'foo/bar/baz'): '.',
            ('a/b/.././../c', '.'): 'c',
            ('a/b/c/d/ee', 'a/b/c/d/e'): '../ee',
            ('a/b/c/d/ee', 'a/b/z/d/e'): '../../../c/d/ee',
            ('foo', 'bar.'): 'foo',
            ('foo', 'bar./'): '../foo',
            ('foo', 'foo/bar./'): '..',
            ('foo', 'foo/bar./.'): '..',
            ('foo', 'foo/bar././'): '..',
            ('foo/', 'foo/bar././'): '../',
            ('foo', 'foo'): '.',
            ('.foo', '.foo'): '.foo',
            ('.foo/', '.foo'): '.foo/',
            ('.foo', '.foo/'): '.',
            ('.foo/', '.foo/'): './',
            ('///', ''): './',
            ('a///', ''): 'a/',
            ('a///', 'a'): './',
            ('.', 'here'): '..',
            ('..', 'here'): '..',
            ('../..', 'here'): '..',
            ('../../a', 'here'): '../a',
            ('..', 'here.txt'): '.',
            ('a', ''): 'a',
            ('a', '..'): 'a',
            ('a', 'b'): '../a',
            ('a', 'b/..'): '../a',  # The dots are considered a file. Documenting a long-standing bug.
            ('a', 'b/../..'): 'a',
            ('a/..../b', 'a/../b'): '../a/..../b',
            ('a/я/b', 'a/я/c'): '../b',
            ('a/я/b', 'a/яя/c'): '../../я/b',
        }
        for (url, other), expected_result in expected_results.items():
            # Leading slash intentionally ignored
            self.assertEqual(utils.get_relative_url(url, other), expected_result)
            self.assertEqual(utils.get_relative_url('/' + url, other), expected_result)
            self.assertEqual(utils.get_relative_url(url, '/' + other), expected_result)
            self.assertEqual(utils.get_relative_url('/' + url, '/' + other), expected_result)

    def test_get_relative_url_empty(self):
        for url in ['', '.', '/.']:
            for other in ['', '.', '/', '/.']:
                self.assertEqual(utils.get_relative_url(url, other), '.')

        self.assertEqual(utils.get_relative_url('/', ''), './')
        self.assertEqual(utils.get_relative_url('/', '/'), './')
        self.assertEqual(utils.get_relative_url('/', '.'), './')
        self.assertEqual(utils.get_relative_url('/', '/.'), './')

    def test_create_media_urls(self):

        expected_results = {
            'https://media.cdn.org/jq.js': [
                'https://media.cdn.org/jq.js',
                'https://media.cdn.org/jq.js',
                'https://media.cdn.org/jq.js'
            ],
            'http://media.cdn.org/jquery.js': [
                'http://media.cdn.org/jquery.js',
                'http://media.cdn.org/jquery.js',
                'http://media.cdn.org/jquery.js'
            ],
            '//media.cdn.org/jquery.js': [
                '//media.cdn.org/jquery.js',
                '//media.cdn.org/jquery.js',
                '//media.cdn.org/jquery.js'
            ],
            'media.cdn.org/jquery.js': [
                'media.cdn.org/jquery.js',
                'media.cdn.org/jquery.js',
                '../media.cdn.org/jquery.js'
            ],
            'local/file/jquery.js': [
                'local/file/jquery.js',
                'local/file/jquery.js',
                '../local/file/jquery.js'
            ],
            'local\\windows\\file\\jquery.js': [
                'local/windows/file/jquery.js',
                'local/windows/file/jquery.js',
                '../local/windows/file/jquery.js'
            ],
            'image.png': [
                'image.png',
                'image.png',
                '../image.png'
            ],
            'style.css?v=20180308c': [
                'style.css?v=20180308c',
                'style.css?v=20180308c',
                '../style.css?v=20180308c'
            ],
            '#some_id': [
                '#some_id',
                '#some_id',
                '#some_id'
            ]
        }

        cfg = load_config(use_directory_urls=False)
        pages = [
            Page('Home', File('index.md',  cfg['docs_dir'], cfg['site_dir'], cfg['use_directory_urls']), cfg),
            Page('About', File('about.md',  cfg['docs_dir'], cfg['site_dir'], cfg['use_directory_urls']), cfg),
            Page('FooBar', File('foo/bar.md',  cfg['docs_dir'], cfg['site_dir'], cfg['use_directory_urls']), cfg)
        ]

        for i, page in enumerate(pages):
            urls = utils.create_media_urls(expected_results.keys(), page)
            self.assertEqual([v[i] for v in expected_results.values()], urls)

    def test_create_media_urls_use_directory_urls(self):

        expected_results = {
            'https://media.cdn.org/jq.js': [
                'https://media.cdn.org/jq.js',
                'https://media.cdn.org/jq.js',
                'https://media.cdn.org/jq.js'
            ],
            'http://media.cdn.org/jquery.js': [
                'http://media.cdn.org/jquery.js',
                'http://media.cdn.org/jquery.js',
                'http://media.cdn.org/jquery.js'
            ],
            '//media.cdn.org/jquery.js': [
                '//media.cdn.org/jquery.js',
                '//media.cdn.org/jquery.js',
                '//media.cdn.org/jquery.js'
            ],
            'media.cdn.org/jquery.js': [
                'media.cdn.org/jquery.js',
                '../media.cdn.org/jquery.js',
                '../../media.cdn.org/jquery.js'
            ],
            'local/file/jquery.js': [
                'local/file/jquery.js',
                '../local/file/jquery.js',
                '../../local/file/jquery.js'
            ],
            'local\\windows\\file\\jquery.js': [
                'local/windows/file/jquery.js',
                '../local/windows/file/jquery.js',
                '../../local/windows/file/jquery.js'
            ],
            'image.png': [
                'image.png',
                '../image.png',
                '../../image.png'
            ],
            'style.css?v=20180308c': [
                'style.css?v=20180308c',
                '../style.css?v=20180308c',
                '../../style.css?v=20180308c'
            ],
            '#some_id': [
                '#some_id',
                '#some_id',
                '#some_id'
            ]
        }

        cfg = load_config(use_directory_urls=True)
        pages = [
            Page('Home', File('index.md',  cfg['docs_dir'], cfg['site_dir'], cfg['use_directory_urls']), cfg),
            Page('About', File('about.md',  cfg['docs_dir'], cfg['site_dir'], cfg['use_directory_urls']), cfg),
            Page('FooBar', File('foo/bar.md',  cfg['docs_dir'], cfg['site_dir'], cfg['use_directory_urls']), cfg)
        ]

        for i, page in enumerate(pages):
            urls = utils.create_media_urls(expected_results.keys(), page)
            self.assertEqual([v[i] for v in expected_results.values()], urls)

    def test_reduce_list(self):
        self.assertEqual(
            utils.reduce_list([1, 2, 3, 4, 5, 5, 2, 4, 6, 7, 8]),
            [1, 2, 3, 4, 5, 6, 7, 8]
        )

    def test_get_themes(self):

        self.assertEqual(
            sorted(utils.get_theme_names()),
            ['mkdocs', 'readthedocs'])

    @mock.patch('importlib_metadata.entry_points', autospec=True)
    def test_get_theme_dir(self, mock_iter):

        path = 'some/path'

        theme = mock.Mock()
        theme.name = 'mkdocs2'
        theme.dist.name = 'mkdocs2'
        theme.load().__file__ = os.path.join(path, '__init__.py')

        mock_iter.return_value = [theme]

        self.assertEqual(utils.get_theme_dir(theme.name), os.path.abspath(path))

    def test_get_theme_dir_keyerror(self):

        with self.assertRaises(KeyError):
            utils.get_theme_dir('nonexistanttheme')

    @mock.patch('importlib_metadata.entry_points', autospec=True)
    def test_get_theme_dir_importerror(self, mock_iter):

        theme = mock.Mock()
        theme.name = 'mkdocs2'
        theme.dist.name = 'mkdocs2'
        theme.load.side_effect = ImportError()

        mock_iter.return_value = [theme]

        with self.assertRaises(ImportError):
            utils.get_theme_dir(theme.name)

    @mock.patch('importlib_metadata.entry_points', autospec=True)
    def test_get_themes_warning(self, mock_iter):

        theme1 = mock.Mock()
        theme1.name = 'mkdocs2'
        theme1.dist.name = 'mkdocs2'
        theme1.load().__file__ = "some/path1"

        theme2 = mock.Mock()
        theme2.name = 'mkdocs2'
        theme2.dist.name = 'mkdocs3'
        theme2.load().__file__ = "some/path2"

        mock_iter.return_value = [theme1, theme2]

        self.assertEqual(
            sorted(utils.get_theme_names()),
            sorted(['mkdocs2', ]))

    @mock.patch('importlib_metadata.entry_points', autospec=True)
    def test_get_themes_error(self, mock_iter):

        theme1 = mock.Mock()
        theme1.name = 'mkdocs'
        theme1.dist.name = 'mkdocs'
        theme1.load().__file__ = "some/path1"

        theme2 = mock.Mock()
        theme2.name = 'mkdocs'
        theme2.dist.name = 'mkdocs2'
        theme2.load().__file__ = "some/path2"

        mock_iter.return_value = [theme1, theme2]

        with self.assertRaises(exceptions.ConfigurationError):
            utils.get_theme_names()

    def test_nest_paths(self):

        j = os.path.join

        result = utils.nest_paths([
            'index.md',
            j('user-guide', 'configuration.md'),
            j('user-guide', 'styling-your-docs.md'),
            j('user-guide', 'writing-your-docs.md'),
            j('about', 'contributing.md'),
            j('about', 'license.md'),
            j('about', 'release-notes.md'),
        ])

        self.assertEqual(
            result,
            [
                'index.md',
                {'User guide': [
                    j('user-guide', 'configuration.md'),
                    j('user-guide', 'styling-your-docs.md'),
                    j('user-guide', 'writing-your-docs.md')]},
                {'About': [
                    j('about', 'contributing.md'),
                    j('about', 'license.md'),
                    j('about', 'release-notes.md')]}
            ]
        )

    def test_unicode_yaml(self):

        yaml_src = dedent(
            '''
            key: value
            key2:
              - value
            '''
        ).encode('utf-8')

        config = utils.yaml_load(yaml_src)
        self.assertTrue(isinstance(config['key'], str))
        self.assertTrue(isinstance(config['key2'][0], str))

    @mock.patch.dict(os.environ, {'VARNAME': 'Hello, World!', 'BOOLVAR': 'false'})
    def test_env_var_in_yaml(self):

        yaml_src = dedent(
            '''
            key1: !ENV VARNAME
            key2: !ENV UNDEFINED
            key3: !ENV [UNDEFINED, default]
            key4: !ENV [UNDEFINED, VARNAME, default]
            key5: !ENV BOOLVAR
            '''
        )
        config = utils.yaml_load(yaml_src)
        self.assertIsInstance(config['key1'], str)
        self.assertEqual(config['key1'], 'Hello, World!')
        self.assertIsNone(config['key2'])
        self.assertIsInstance(config['key3'], str)
        self.assertEqual(config['key3'], 'default')
        self.assertIsInstance(config['key4'], str)
        self.assertEqual(config['key4'], 'Hello, World!')
        self.assertIs(config['key5'], False)

    @tempdir(files={'base.yml': BASEYML, 'parent.yml': PARENTYML})
    def test_yaml_inheritance(self, tdir):
        expected = {
            'foo': 'bar',
            'baz': {
                'sub1': 'replaced',
                'sub2': 2,
                'sub3': 'new'
            },
            'deep1': {
                'deep2-1': {
                    'deep3-1': 'replaced',
                    'deep3-2': 'bar'
                },
                'deep2-2': 'baz'
            }
        }
        with open(os.path.join(tdir, 'base.yml')) as fd:
            result = utils.yaml_load(fd)
        self.assertEqual(result, expected)

    @tempdir(files={'base.yml': BASEYML})
    def test_yaml_inheritance_missing_parent(self, tdir):
        with open(os.path.join(tdir, 'base.yml')) as fd:
            with self.assertRaises(exceptions.ConfigurationError):
                utils.yaml_load(fd)

    def test_copy_files(self):
        src_paths = [
            'foo.txt',
            'bar.txt',
            'baz.txt',
        ]
        dst_paths = [
            'foo.txt',
            'foo/',             # ensure src filename is appended
            'foo/bar/baz.txt'   # ensure missing dirs are created
        ]
        expected = [
            'foo.txt',
            'foo/bar.txt',
            'foo/bar/baz.txt',
        ]

        src_dir = tempfile.mkdtemp()
        dst_dir = tempfile.mkdtemp()

        try:
            for i, src in enumerate(src_paths):
                src = os.path.join(src_dir, src)
                with open(src, 'w') as f:
                    f.write('content')
                dst = os.path.join(dst_dir, dst_paths[i])
                utils.copy_file(src, dst)
                self.assertTrue(os.path.isfile(os.path.join(dst_dir, expected[i])))
        finally:
            shutil.rmtree(src_dir)
            shutil.rmtree(dst_dir)

    def test_copy_files_without_permissions(self):
        src_paths = [
            'foo.txt',
            'bar.txt',
            'baz.txt',
        ]
        expected = [
            'foo.txt',
            'bar.txt',
            'baz.txt',
        ]

        src_dir = tempfile.mkdtemp()
        dst_dir = tempfile.mkdtemp()

        try:
            for i, src in enumerate(src_paths):
                src = os.path.join(src_dir, src)
                with open(src, 'w') as f:
                    f.write('content')
                # Set src file to read-only
                os.chmod(src, stat.S_IRUSR)
                utils.copy_file(src, dst_dir)
                self.assertTrue(os.path.isfile(os.path.join(dst_dir, expected[i])))
                self.assertNotEqual(os.stat(src).st_mode, os.stat(os.path.join(dst_dir, expected[i])).st_mode)
                # While src was read-only, dst must remain writable
                self.assertTrue(os.access(os.path.join(dst_dir, expected[i]), os.W_OK))
        finally:
            for src in src_paths:
                # Undo read-only so we can delete temp files
                src = os.path.join(src_dir, src)
                if os.path.exists(src):
                    os.chmod(src, stat.S_IRUSR | stat.S_IWUSR)
            shutil.rmtree(src_dir)
            shutil.rmtree(dst_dir)

    def test_mm_meta_data(self):
        doc = dedent(
            """
            Title: Foo Bar
            Date: 2018-07-10
            Summary: Line one
                Line two
            Tags: foo
            Tags: bar

            Doc body
            """
        )
        self.assertEqual(
            utils.meta.get_data(doc),
            (
                "Doc body",
                {
                    'title': 'Foo Bar',
                    'date': '2018-07-10',
                    'summary': 'Line one Line two',
                    'tags': 'foo bar'
                }
            )
        )

    def test_mm_meta_data_blank_first_line(self):
        doc = '\nfoo: bar\nDoc body'
        self.assertEqual(utils.meta.get_data(doc), (doc.lstrip(), {}))

    def test_yaml_meta_data(self):
        doc = dedent(
            """
            ---
            Title: Foo Bar
            Date: 2018-07-10
            Summary: Line one
                Line two
            Tags:
                - foo
                - bar
            ---
            Doc body
            """
        )
        self.assertEqual(
            utils.meta.get_data(doc),
            (
                "Doc body",
                {
                    'Title': 'Foo Bar',
                    'Date': datetime.date(2018, 7, 10),
                    'Summary': 'Line one Line two',
                    'Tags': ['foo', 'bar']
                }
            )
        )

    def test_yaml_meta_data_not_dict(self):
        doc = dedent(
            """
            ---
            - List item
            ---
            Doc body
            """
        )
        self.assertEqual(utils.meta.get_data(doc), (doc, {}))

    def test_yaml_meta_data_invalid(self):
        doc = dedent(
            """
            ---
            foo: bar: baz
            ---
            Doc body
            """
        )
        self.assertEqual(utils.meta.get_data(doc), (doc, {}))

    def test_no_meta_data(self):
        doc = dedent(
            """
            Doc body
            """
        )
        self.assertEqual(utils.meta.get_data(doc), (doc, {}))


class LogCounterTests(unittest.TestCase):
    def setUp(self):
        self.log = logging.getLogger('dummy')
        self.log.propagate = False
        self.log.setLevel(1)
        self.counter = utils.CountHandler()
        self.log.addHandler(self.counter)

    def tearDown(self):
        self.log.removeHandler(self.counter)

    def test_default_values(self):
        self.assertEqual(self.counter.get_counts(), [])

    def test_count_critical(self):
        self.assertEqual(self.counter.get_counts(), [])
        self.log.critical('msg')
        self.assertEqual(self.counter.get_counts(), [('CRITICAL', 1)])

    def test_count_error(self):
        self.assertEqual(self.counter.get_counts(), [])
        self.log.error('msg')
        self.assertEqual(self.counter.get_counts(), [('ERROR', 1)])

    def test_count_warning(self):
        self.assertEqual(self.counter.get_counts(), [])
        self.log.warning('msg')
        self.assertEqual(self.counter.get_counts(), [('WARNING', 1)])

    def test_count_info(self):
        self.assertEqual(self.counter.get_counts(), [])
        self.log.info('msg')
        self.assertEqual(self.counter.get_counts(), [('INFO', 1)])

    def test_count_debug(self):
        self.assertEqual(self.counter.get_counts(), [])
        self.log.debug('msg')
        self.assertEqual(self.counter.get_counts(), [('DEBUG', 1)])

    def test_count_multiple(self):
        self.assertEqual(self.counter.get_counts(), [])
        self.log.warning('msg 1')
        self.assertEqual(self.counter.get_counts(), [('WARNING', 1)])
        self.log.warning('msg 2')
        self.assertEqual(self.counter.get_counts(), [('WARNING', 2)])
        self.log.debug('msg 3')
        self.assertEqual(self.counter.get_counts(), [('WARNING', 2), ('DEBUG', 1)])
        self.log.error('mdg 4')
        self.assertEqual(self.counter.get_counts(), [('ERROR', 1), ('WARNING', 2), ('DEBUG', 1)])

    def test_log_level(self):
        self.assertEqual(self.counter.get_counts(), [])
        self.counter.setLevel(logging.ERROR)
        self.log.error('counted')
        self.log.warning('not counted')
        self.log.info('not counted')
        self.assertEqual(self.counter.get_counts(), [('ERROR', 1)])
        self.counter.setLevel(logging.WARNING)
        self.log.error('counted')
        self.log.warning('counted')
        self.log.info('not counted')
        self.assertEqual(self.counter.get_counts(), [('ERROR', 2), ('WARNING', 1)])

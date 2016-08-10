from __future__ import unicode_literals

import os
import tempfile
import unittest

import mkdocs
from mkdocs import utils
from mkdocs.config import config_options


class OptionallyRequiredTest(unittest.TestCase):

    def test_empty(self):

        option = config_options.OptionallyRequired()
        value = option.validate(None)
        self.assertEqual(value, None)

        self.assertEqual(option.is_required(), False)

    def test_required(self):

        option = config_options.OptionallyRequired(required=True)
        self.assertRaises(config_options.ValidationError,
                          option.validate, None)

        self.assertEqual(option.is_required(), True)

    def test_required_no_default(self):

        option = config_options.OptionallyRequired(required=True)
        value = option.validate(2)
        self.assertEqual(2, value)

    def test_default(self):

        option = config_options.OptionallyRequired(default=1)
        value = option.validate(None)
        self.assertEqual(1, value)

    def test_replace_default(self):

        option = config_options.OptionallyRequired(default=1)
        value = option.validate(2)
        self.assertEqual(2, value)


class TypeTest(unittest.TestCase):

    def test_single_type(self):

        option = config_options.Type(utils.string_types)
        value = option.validate("Testing")
        self.assertEqual(value, "Testing")

    def test_multiple_types(self):
        option = config_options.Type((list, tuple))

        value = option.validate([1, 2, 3])
        self.assertEqual(value, [1, 2, 3])

        value = option.validate((1, 2, 3))
        self.assertEqual(value, (1, 2, 3))

        self.assertRaises(config_options.ValidationError,
                          option.validate, {'a': 1})

    def test_length(self):
        option = config_options.Type(utils.string_types, length=7)

        value = option.validate("Testing")
        self.assertEqual(value, "Testing")

        self.assertRaises(config_options.ValidationError,
                          option.validate, "Testing Long")


class URLTest(unittest.TestCase):

    def test_valid_url(self):

        url = "http://mkdocs.org"

        option = config_options.URL()
        value = option.validate(url)
        self.assertEqual(value, url)

    def test_invalid_url(self):

        option = config_options.URL()
        self.assertRaises(config_options.ValidationError,
                          option.validate, "www.mkdocs.org")

    def test_invalid(self):

        option = config_options.URL()
        self.assertRaises(config_options.ValidationError,
                          option.validate, 1)


class RepoURLTest(unittest.TestCase):

    def test_repo_name_github(self):

        option = config_options.RepoURL()
        config = {'repo_url': "https://github.com/mkdocs/mkdocs"}
        option.post_validation(config, 'repo_url')
        self.assertEqual(config['repo_url'], config['repo_url'])
        self.assertEqual(config['repo_name'], "GitHub")

    def test_repo_name_bitbucket(self):

        option = config_options.RepoURL()
        config = {'repo_url': "https://bitbucket.org/gutworth/six/"}
        option.post_validation(config, 'repo_url')
        self.assertEqual(config['repo_url'], config['repo_url'])
        self.assertEqual(config['repo_name'], "Bitbucket")

    def test_repo_name_custom(self):

        option = config_options.RepoURL()
        config = {'repo_url': "https://launchpad.net/python-tuskarclient"}
        option.post_validation(config, 'repo_url')
        self.assertEqual(config['repo_url'], config['repo_url'])
        self.assertEqual(config['repo_name'], "Launchpad")

    def test_edit_uri_github(self):

        option = config_options.RepoURL()
        config = {'repo_url': "https://github.com/mkdocs/mkdocs"}
        option.post_validation(config, 'repo_url')
        self.assertEqual(config['edit_uri'], 'edit/master/docs/')

    def test_edit_uri_bitbucket(self):

        option = config_options.RepoURL()
        config = {'repo_url': "https://bitbucket.org/gutworth/six/"}
        option.post_validation(config, 'repo_url')
        self.assertEqual(config['edit_uri'], 'src/default/docs/')

    def test_edit_uri_custom(self):

        option = config_options.RepoURL()
        config = {'repo_url': "https://launchpad.net/python-tuskarclient"}
        option.post_validation(config, 'repo_url')
        self.assertEqual(config.get('edit_uri'), None)


class DirTest(unittest.TestCase):

    def test_valid_dir(self):

        d = os.path.dirname(__file__)
        option = config_options.Dir(exists=True)
        value = option.validate(d)
        self.assertEqual(d, value)

    def test_missing_dir(self):

        d = os.path.join("not", "a", "real", "path", "I", "hope")
        option = config_options.Dir()
        value = option.validate(d)
        self.assertEqual(os.path.abspath(d), value)

    def test_missing_dir_but_required(self):

        d = os.path.join("not", "a", "real", "path", "I", "hope")
        option = config_options.Dir(exists=True)
        self.assertRaises(config_options.ValidationError,
                          option.validate, d)

    def test_file(self):
        d = __file__
        option = config_options.Dir(exists=True)
        self.assertRaises(config_options.ValidationError,
                          option.validate, d)

    def test_incorrect_type_attribute_error(self):
        option = config_options.Dir()
        self.assertRaises(config_options.ValidationError,
                          option.validate, 1)

    def test_incorrect_type_type_error(self):
        option = config_options.Dir()
        self.assertRaises(config_options.ValidationError,
                          option.validate, [])

    def test_doc_dir_is_config_dir(self):

        test_config = {
            'config_file_path': os.path.join(os.path.abspath('.'), 'mkdocs.yml'),
            'docs_dir': '.'
        }

        docs_dir = config_options.Dir()

        test_config['docs_dir'] = docs_dir.validate(test_config['docs_dir'])

        self.assertRaises(config_options.ValidationError,
                          docs_dir.post_validation, test_config, 'docs_dir')


class SiteDirTest(unittest.TestCase):

    def test_doc_dir_in_site_dir(self):

        j = os.path.join
        option = config_options.SiteDir()
        docs_dir = config_options.Dir()
        # The parent dir is not the same on every system, so use the actual dir name
        parent_dir = mkdocs.__file__.split(os.sep)[-3]

        test_configs = (
            {'docs_dir': j('site', 'docs'), 'site_dir': 'site'},
            {'docs_dir': 'docs', 'site_dir': '.'},
            {'docs_dir': '.', 'site_dir': '.'},
            {'docs_dir': 'docs', 'site_dir': ''},
            {'docs_dir': '', 'site_dir': ''},
            {'docs_dir': j('..', parent_dir, 'docs'), 'site_dir': 'docs'},
        )

        for test_config in test_configs:
            test_config['config_file_path'] = j(os.path.abspath('..'), 'mkdocs.yml')

            test_config['docs_dir'] = docs_dir.validate(test_config['docs_dir'])
            test_config['site_dir'] = option.validate(test_config['site_dir'])

            self.assertRaises(config_options.ValidationError,
                              option.post_validation, test_config, 'site_dir')

    def test_site_dir_in_docs_dir(self):

        j = os.path.join

        test_configs = (
            {'docs_dir': 'docs', 'site_dir': j('docs', 'site')},
            {'docs_dir': '.', 'site_dir': 'site'},
            {'docs_dir': '', 'site_dir': 'site'},
        )

        for test_config in test_configs:
            test_config['config_file_path'] = j(os.path.abspath('..'), 'mkdocs.yml')

            docs_dir = config_options.Dir()
            option = config_options.SiteDir()

            test_config['docs_dir'] = docs_dir.validate(test_config['docs_dir'])
            test_config['site_dir'] = option.validate(test_config['site_dir'])

            self.assertRaises(config_options.ValidationError,
                              option.post_validation, test_config, 'site_dir')


class ThemeTest(unittest.TestCase):

    def test_theme(self):

        option = config_options.Theme()
        value = option.validate("mkdocs")
        self.assertEqual("mkdocs", value)

    def test_theme_invalid(self):

        option = config_options.Theme()
        self.assertRaises(config_options.ValidationError,
                          option.validate, "mkdocs2")


class ExtrasTest(unittest.TestCase):

    def test_provided(self):

        option = config_options.Extras(utils.is_markdown_file)
        value = option.validate([])
        self.assertEqual([], value)

        option.post_validation({'extra_stuff': []}, 'extra_stuff')

    def test_empty(self):

        option = config_options.Extras(utils.is_template_file)
        value = option.validate(None)
        self.assertEqual(None, value)

    def test_invalid(self):

        option = config_options.Extras(utils.is_html_file)
        self.assertRaises(config_options.ValidationError,
                          option.validate, {})

    def test_walk(self):

        option = config_options.Extras(utils.is_markdown_file)

        tmp_dir = tempfile.mkdtemp()

        f1 = os.path.join(tmp_dir, 'file1.md')
        f2 = os.path.join(tmp_dir, 'file2.md')

        open(f1, 'a').close()

        # symlink isn't available on Python 2 on Windows.
        if hasattr(os, 'symlink'):
            os.symlink('/path/that/doesnt/exist', f2)

        files = list(option.walk_docs_dir(tmp_dir))

        self.assertEqual(['file1.md', ], files)


class PagesTest(unittest.TestCase):

    def test_provided(self):

        option = config_options.Pages()
        value = option.validate([['index.md', ], ])
        self.assertEqual(['index.md', ], value)

        option.post_validation({'extra_stuff': []}, 'extra_stuff')

    def test_provided_dict(self):

        option = config_options.Pages()
        value = option.validate([
            'index.md',
            {"Page": "page.md"}
        ])
        self.assertEqual(['index.md', {'Page': 'page.md'}], value)

        option.post_validation({'extra_stuff': []}, 'extra_stuff')

    def test_provided_empty(self):

        option = config_options.Pages()
        value = option.validate([])
        self.assertEqual(None, value)

        option.post_validation({'extra_stuff': []}, 'extra_stuff')

    def test_invalid_type(self):

        option = config_options.Pages()
        self.assertRaises(config_options.ValidationError,
                          option.validate, {})

    def test_invalid_config(self):

        option = config_options.Pages()
        self.assertRaises(config_options.ValidationError,
                          option.validate, [[], 1])


class NumPagesTest(unittest.TestCase):

    def test_one_page(self):

        option = config_options.NumPages()
        config = {
            'key': None,
            'pages': [1, ]
        }
        option.post_validation(config, 'key')
        self.assertEqual({
            'key': False,
            'pages': [1, ]
        }, config)

    def test_many_pages(self):

        option = config_options.NumPages()
        config = {
            'key': None,
            'pages': [1, 2, 3]
        }
        option.post_validation(config, 'key')
        self.assertEqual({
            'key': True,
            'pages': [1, 2, 3]
        }, config)

    def test_invalid_pages(self):

        option = config_options.NumPages()
        config = {
            'key': None,
            'pages': None
        }
        option.post_validation(config, 'key')
        self.assertEqual({
            'key': False,
            'pages': None
        }, config)

    def test_provided(self):

        option = config_options.NumPages()
        config = {
            'key': True,
            'pages': None
        }
        option.post_validation(config, 'key')
        self.assertEqual({
            'key': True,
            'pages': None
        }, config)


class PrivateTest(unittest.TestCase):

    def test_defined(self):

        option = config_options.Private()
        self.assertRaises(config_options.ValidationError,
                          option.validate, 'somevalue')


class MarkdownExtensionsTest(unittest.TestCase):

    def test_simple_list(self):
        option = config_options.MarkdownExtensions()
        config = {
            'markdown_extensions': ['foo', 'bar']
        }
        config['markdown_extensions'] = option.validate(config['markdown_extensions'])
        option.post_validation(config, 'markdown_extensions')
        self.assertEqual({
            'markdown_extensions': ['foo', 'bar'],
            'mdx_configs': {}
        }, config)

    def test_list_dicts(self):
        option = config_options.MarkdownExtensions()
        config = {
            'markdown_extensions': [
                {'foo': {'foo_option': 'foo value'}},
                {'bar': {'bar_option': 'bar value'}},
                {'baz': None}
            ]
        }
        config['markdown_extensions'] = option.validate(config['markdown_extensions'])
        option.post_validation(config, 'markdown_extensions')
        self.assertEqual({
            'markdown_extensions': ['foo', 'bar', 'baz'],
            'mdx_configs': {
                'foo': {'foo_option': 'foo value'},
                'bar': {'bar_option': 'bar value'}
            }
        }, config)

    def test_mixed_list(self):
        option = config_options.MarkdownExtensions()
        config = {
            'markdown_extensions': [
                'foo',
                {'bar': {'bar_option': 'bar value'}}
            ]
        }
        config['markdown_extensions'] = option.validate(config['markdown_extensions'])
        option.post_validation(config, 'markdown_extensions')
        self.assertEqual({
            'markdown_extensions': ['foo', 'bar'],
            'mdx_configs': {
                'bar': {'bar_option': 'bar value'}
            }
        }, config)

    def test_builtins(self):
        option = config_options.MarkdownExtensions(builtins=['meta', 'toc'])
        config = {
            'markdown_extensions': ['foo', 'bar']
        }
        config['markdown_extensions'] = option.validate(config['markdown_extensions'])
        option.post_validation(config, 'markdown_extensions')
        self.assertEqual({
            'markdown_extensions': ['meta', 'toc', 'foo', 'bar'],
            'mdx_configs': {}
        }, config)

    def test_duplicates(self):
        option = config_options.MarkdownExtensions(builtins=['meta', 'toc'])
        config = {
            'markdown_extensions': ['meta', 'toc']
        }
        config['markdown_extensions'] = option.validate(config['markdown_extensions'])
        option.post_validation(config, 'markdown_extensions')
        self.assertEqual({
            'markdown_extensions': ['meta', 'toc'],
            'mdx_configs': {}
        }, config)

    def test_builtins_config(self):
        option = config_options.MarkdownExtensions(builtins=['meta', 'toc'])
        config = {
            'markdown_extensions': [
                {'toc': {'permalink': True}}
            ]
        }
        config['markdown_extensions'] = option.validate(config['markdown_extensions'])
        option.post_validation(config, 'markdown_extensions')
        self.assertEqual({
            'markdown_extensions': ['meta', 'toc'],
            'mdx_configs': {'toc': {'permalink': True}}
        }, config)

    def test_configkey(self):
        option = config_options.MarkdownExtensions(configkey='bar')
        config = {
            'markdown_extensions': [
                {'foo': {'foo_option': 'foo value'}}
            ]
        }
        config['markdown_extensions'] = option.validate(config['markdown_extensions'])
        option.post_validation(config, 'markdown_extensions')
        self.assertEqual({
            'markdown_extensions': ['foo'],
            'bar': {
                'foo': {'foo_option': 'foo value'}
            }
        }, config)

    def test_none(self):
        option = config_options.MarkdownExtensions(default=[])
        config = {
            'markdown_extensions': None
        }
        config['markdown_extensions'] = option.validate(config['markdown_extensions'])
        option.post_validation(config, 'markdown_extensions')
        self.assertEqual({
            'markdown_extensions': [],
            'mdx_configs': {}
        }, config)

    def test_not_list(self):
        option = config_options.MarkdownExtensions()
        self.assertRaises(config_options.ValidationError,
                          option.validate, 'not a list')

    def test_invalid_config_option(self):
        option = config_options.MarkdownExtensions()
        config = {
            'markdown_extensions': [
                {'foo': 'not a dict'}
            ]
        }
        self.assertRaises(
            config_options.ValidationError,
            option.validate, config['markdown_extensions']
        )

    def test_invalid_config_item(self):
        option = config_options.MarkdownExtensions()
        config = {
            'markdown_extensions': [
                ['not a dict']
            ]
        }
        self.assertRaises(
            config_options.ValidationError,
            option.validate, config['markdown_extensions']
        )

    def test_invalid_dict_item(self):
        option = config_options.MarkdownExtensions()
        config = {
            'markdown_extensions': [
                {'key1': 'value', 'key2': 'too many keys'}
            ]
        }
        self.assertRaises(
            config_options.ValidationError,
            option.validate, config['markdown_extensions']
        )

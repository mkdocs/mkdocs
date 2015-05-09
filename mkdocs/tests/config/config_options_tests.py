import os
import unittest

from mkdocs import utils, legacy
from mkdocs.config import config_options


class BaseConfigOptionTest(unittest.TestCase):

    def test_empty(self):

        option = config_options.BaseConfigOption()
        value = option.validate(None)
        self.assertEqual(value, None)

        self.assertEqual(option.is_required(), False)

    def test_required(self):

        option = config_options.BaseConfigOption(required=True)
        self.assertRaises(config_options.ValidationError, option.validate, None)

        self.assertEqual(option.is_required(), True)

    def test_required_no_default(self):

        option = config_options.BaseConfigOption(required=True)
        value = option.validate(2)
        self.assertEqual(2, value)

    def test_default(self):

        option = config_options.BaseConfigOption(default=1)
        value = option.validate(None)
        self.assertEqual(1, value)

    def test_replace_default(self):

        option = config_options.BaseConfigOption(default=1)
        value = option.validate(2)
        self.assertEqual(2, value)


class TypeTest(unittest.TestCase):

    def test_single_type(self):

        option = config_options.Type(str)
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
        option = config_options.Type(str, length=7)

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


class SiteDirTest(unittest.TestCase):

    def test_doc_dir_in_site_dir(self):

        j = os.path.join
        option = config_options.SiteDir()
        docs_dir = config_options.Dir()

        test_configs = (
            {'docs_dir': 'docs', 'site_dir': j('docs', 'site')},
            {'docs_dir': j('site', 'docs'), 'site_dir': 'site'},
            {'docs_dir': 'docs', 'site_dir': '.'},
            {'docs_dir': '.', 'site_dir': 'site'},
            {'docs_dir': '.', 'site_dir': '.'},
            {'docs_dir': 'docs', 'site_dir': ''},
            {'docs_dir': '', 'site_dir': 'site'},
            {'docs_dir': '', 'site_dir': ''},
            {'docs_dir': j('..', 'mkdocs', 'docs'), 'site_dir': 'docs'},
        )

        for test_config in test_configs:

            test_config['docs_dir'] = docs_dir.validate(test_config['docs_dir'])
            test_config['site_dir'] = option.validate(test_config['site_dir'])

            self.assertRaises(config_options.ValidationError,
                              option.post_validation, test_config, 'key')


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
            legacy.OrderedDict((
                ('Page', 'page.md', ),
            ))
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

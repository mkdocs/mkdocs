import os
import sys
import textwrap
import unittest
from unittest.mock import patch

import mkdocs
from mkdocs.config import config_options
from mkdocs.config.base import Config
from mkdocs.tests.base import tempdir
from mkdocs.utils import yaml_load


class OptionallyRequiredTest(unittest.TestCase):

    def test_empty(self):

        option = config_options.OptionallyRequired()
        value = option.validate(None)
        self.assertEqual(value, None)

        self.assertEqual(option.is_required(), False)

    def test_required(self):

        option = config_options.OptionallyRequired(required=True)
        with self.assertRaises(config_options.ValidationError):
            option.validate(None)

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

        option = config_options.Type(str)
        value = option.validate("Testing")
        self.assertEqual(value, "Testing")

    def test_multiple_types(self):
        option = config_options.Type((list, tuple))

        value = option.validate([1, 2, 3])
        self.assertEqual(value, [1, 2, 3])

        value = option.validate((1, 2, 3))
        self.assertEqual(value, (1, 2, 3))

        with self.assertRaises(config_options.ValidationError):
            option.validate({'a': 1})

    def test_length(self):
        option = config_options.Type(str, length=7)

        value = option.validate("Testing")
        self.assertEqual(value, "Testing")

        with self.assertRaises(config_options.ValidationError):
            option.validate("Testing Long")


class ChoiceTest(unittest.TestCase):

    def test_valid_choice(self):
        option = config_options.Choice(('python', 'node'))
        value = option.validate('python')
        self.assertEqual(value, 'python')

    def test_invalid_choice(self):
        option = config_options.Choice(('python', 'node'))
        with self.assertRaises(config_options.ValidationError):
            option.validate('go')

    def test_invalid_choices(self):
        self.assertRaises(ValueError, config_options.Choice, '')
        self.assertRaises(ValueError, config_options.Choice, [])
        self.assertRaises(ValueError, config_options.Choice, 5)


class DeprecatedTest(unittest.TestCase):

    def test_deprecated_option_simple(self):
        option = config_options.Deprecated()
        option.pre_validation({'d': 'value'}, 'd')
        self.assertEqual(len(option.warnings), 1)
        option.validate('value')

    def test_deprecated_option_message(self):
        msg = 'custom message for {} key'
        option = config_options.Deprecated(message=msg)
        option.pre_validation({'d': 'value'}, 'd')
        self.assertEqual(len(option.warnings), 1)
        self.assertEqual(option.warnings[0], msg.format('d'))

    def test_deprecated_option_with_type(self):
        option = config_options.Deprecated(option_type=config_options.Type(str))
        option.pre_validation({'d': 'value'}, 'd')
        self.assertEqual(len(option.warnings), 1)
        option.validate('value')

    def test_deprecated_option_with_invalid_type(self):
        option = config_options.Deprecated(option_type=config_options.Type(list))
        config = {'d': 'string'}
        option.pre_validation({'d': 'value'}, 'd')
        self.assertEqual(len(option.warnings), 1)
        with self.assertRaises(config_options.ValidationError):
            option.validate(config['d'])

    def test_removed_option(self):
        option = config_options.Deprecated(removed=True, moved_to='foo')
        with self.assertRaises(config_options.ValidationError):
            option.pre_validation({'d': 'value'}, 'd')

    def test_deprecated_option_with_type_undefined(self):
        option = config_options.Deprecated(option_type=config_options.Type(str))
        option.validate(None)

    def test_deprecated_option_move(self):
        option = config_options.Deprecated(moved_to='new')
        config = {'old': 'value'}
        option.pre_validation(config, 'old')
        self.assertEqual(len(option.warnings), 1)
        self.assertEqual(config, {'new': 'value'})

    def test_deprecated_option_move_complex(self):
        option = config_options.Deprecated(moved_to='foo.bar')
        config = {'old': 'value'}
        option.pre_validation(config, 'old')
        self.assertEqual(len(option.warnings), 1)
        self.assertEqual(config, {'foo': {'bar': 'value'}})

    def test_deprecated_option_move_existing(self):
        option = config_options.Deprecated(moved_to='foo.bar')
        config = {'old': 'value', 'foo': {'existing': 'existing'}}
        option.pre_validation(config, 'old')
        self.assertEqual(len(option.warnings), 1)
        self.assertEqual(config, {'foo': {'existing': 'existing', 'bar': 'value'}})

    def test_deprecated_option_move_invalid(self):
        option = config_options.Deprecated(moved_to='foo.bar')
        config = {'old': 'value', 'foo': 'wrong type'}
        option.pre_validation(config, 'old')
        self.assertEqual(len(option.warnings), 1)
        self.assertEqual(config, {'old': 'value', 'foo': 'wrong type'})


class IpAddressTest(unittest.TestCase):

    def test_valid_address(self):
        addr = '127.0.0.1:8000'

        option = config_options.IpAddress()
        value = option.validate(addr)
        self.assertEqual(str(value), addr)
        self.assertEqual(value.host, '127.0.0.1')
        self.assertEqual(value.port, 8000)

    def test_valid_IPv6_address(self):
        addr = '::1:8000'

        option = config_options.IpAddress()
        value = option.validate(addr)
        self.assertEqual(str(value), addr)
        self.assertEqual(value.host, '::1')
        self.assertEqual(value.port, 8000)

    def test_named_address(self):
        addr = 'localhost:8000'

        option = config_options.IpAddress()
        value = option.validate(addr)
        self.assertEqual(str(value), addr)
        self.assertEqual(value.host, 'localhost')
        self.assertEqual(value.port, 8000)

    def test_default_address(self):
        addr = '127.0.0.1:8000'

        option = config_options.IpAddress(default=addr)
        value = option.validate(None)
        self.assertEqual(str(value), addr)
        self.assertEqual(value.host, '127.0.0.1')
        self.assertEqual(value.port, 8000)

    @unittest.skipIf(
        sys.version_info < (3, 9, 5),
        "Leading zeros allowed in IP addresses before Python3.9.5",
    )
    def test_invalid_leading_zeros(self):
        addr = '127.000.000.001:8000'
        option = config_options.IpAddress(default=addr)
        with self.assertRaises(config_options.ValidationError):
            option.validate(addr)

    def test_invalid_address_range(self):
        option = config_options.IpAddress()
        with self.assertRaises(config_options.ValidationError):
            option.validate('277.0.0.1:8000')

    def test_invalid_address_format(self):
        option = config_options.IpAddress()
        with self.assertRaises(config_options.ValidationError):
            option.validate('127.0.0.18000')

    def test_invalid_address_type(self):
        option = config_options.IpAddress()
        with self.assertRaises(config_options.ValidationError):
            option.validate(123)

    def test_invalid_address_port(self):
        option = config_options.IpAddress()
        with self.assertRaises(config_options.ValidationError):
            option.validate('127.0.0.1:foo')

    def test_invalid_address_missing_port(self):
        option = config_options.IpAddress()
        with self.assertRaises(config_options.ValidationError):
            option.validate('127.0.0.1')

    def test_unsupported_address(self):
        option = config_options.IpAddress()
        value = option.validate('0.0.0.0:8000')
        option.post_validation({'dev_addr': value}, 'dev_addr')
        self.assertEqual(len(option.warnings), 1)

    def test_unsupported_IPv6_address(self):
        option = config_options.IpAddress()
        value = option.validate(':::8000')
        option.post_validation({'dev_addr': value}, 'dev_addr')
        self.assertEqual(len(option.warnings), 1)

    def test_invalid_IPv6_address(self):
        # The server will error out with this so we treat it as invalid.
        option = config_options.IpAddress()
        with self.assertRaises(config_options.ValidationError):
            option.validate('[::1]:8000')


class URLTest(unittest.TestCase):

    def test_valid_url(self):
        option = config_options.URL()

        self.assertEqual(option.validate("https://mkdocs.org"), "https://mkdocs.org")
        self.assertEqual(option.validate(""), "")

    def test_valid_url_is_dir(self):
        option = config_options.URL(is_dir=True)

        self.assertEqual(option.validate("http://mkdocs.org/"), "http://mkdocs.org/")
        self.assertEqual(option.validate("https://mkdocs.org"), "https://mkdocs.org/")

    def test_invalid_url(self):
        option = config_options.URL()

        with self.assertRaises(config_options.ValidationError):
            option.validate("www.mkdocs.org")
        with self.assertRaises(config_options.ValidationError):
            option.validate("//mkdocs.org/test")
        with self.assertRaises(config_options.ValidationError):
            option.validate("http:/mkdocs.org/")
        with self.assertRaises(config_options.ValidationError):
            option.validate("/hello/")

    def test_invalid_type(self):
        option = config_options.URL()
        with self.assertRaises(config_options.ValidationError):
            option.validate(1)


class RepoURLTest(unittest.TestCase):

    def test_repo_name_github(self):

        option = config_options.RepoURL()
        config = {'repo_url': "https://github.com/mkdocs/mkdocs"}
        option.post_validation(config, 'repo_url')
        self.assertEqual(config['repo_name'], "GitHub")

    def test_repo_name_bitbucket(self):

        option = config_options.RepoURL()
        config = {'repo_url': "https://bitbucket.org/gutworth/six/"}
        option.post_validation(config, 'repo_url')
        self.assertEqual(config['repo_name'], "Bitbucket")

    def test_repo_name_gitlab(self):

        option = config_options.RepoURL()
        config = {'repo_url': "https://gitlab.com/gitlab-org/gitlab-ce/"}
        option.post_validation(config, 'repo_url')
        self.assertEqual(config['repo_name'], "GitLab")

    def test_repo_name_custom(self):

        option = config_options.RepoURL()
        config = {'repo_url': "https://launchpad.net/python-tuskarclient"}
        option.post_validation(config, 'repo_url')
        self.assertEqual(config['repo_name'], "Launchpad")

    def test_edit_uri_github(self):

        option = config_options.RepoURL()
        config = {'repo_url': "https://github.com/mkdocs/mkdocs"}
        option.post_validation(config, 'repo_url')
        self.assertEqual(config['edit_uri'], 'edit/master/docs/')
        self.assertEqual(config['repo_url'], "https://github.com/mkdocs/mkdocs")

    def test_edit_uri_bitbucket(self):

        option = config_options.RepoURL()
        config = {'repo_url': "https://bitbucket.org/gutworth/six/"}
        option.post_validation(config, 'repo_url')
        self.assertEqual(config['edit_uri'], 'src/default/docs/')
        self.assertEqual(config['repo_url'], "https://bitbucket.org/gutworth/six/")

    def test_edit_uri_gitlab(self):

        option = config_options.RepoURL()
        config = {'repo_url': "https://gitlab.com/gitlab-org/gitlab-ce/"}
        option.post_validation(config, 'repo_url')
        self.assertEqual(config['edit_uri'], 'edit/master/docs/')

    def test_edit_uri_custom(self):

        option = config_options.RepoURL()
        config = {'repo_url': "https://launchpad.net/python-tuskarclient"}
        option.post_validation(config, 'repo_url')
        self.assertEqual(config.get('edit_uri'), '')
        self.assertEqual(config['repo_url'], "https://launchpad.net/python-tuskarclient")

    def test_repo_name_custom_and_empty_edit_uri(self):

        option = config_options.RepoURL()
        config = {'repo_url': "https://github.com/mkdocs/mkdocs",
                  'repo_name': 'mkdocs'}
        option.post_validation(config, 'repo_url')
        self.assertEqual(config.get('edit_uri'), 'edit/master/docs/')


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
        with self.assertRaises(config_options.ValidationError):
            option.validate(d)

    def test_file(self):
        d = __file__
        option = config_options.Dir(exists=True)
        with self.assertRaises(config_options.ValidationError):
            option.validate(d)

    def test_incorrect_type_attribute_error(self):
        option = config_options.Dir()
        with self.assertRaises(config_options.ValidationError):
            option.validate(1)

    def test_incorrect_type_type_error(self):
        option = config_options.Dir()
        with self.assertRaises(config_options.ValidationError):
            option.validate([])

    def test_dir_unicode(self):
        cfg = Config(
            [('dir', config_options.Dir())],
            config_file_path=os.path.join(os.path.abspath('.'), 'mkdocs.yml'),
        )

        test_config = {
            'dir': 'юникод'
        }

        cfg.load_dict(test_config)

        fails, warns = cfg.validate()

        self.assertEqual(len(fails), 0)
        self.assertEqual(len(warns), 0)
        self.assertIsInstance(cfg['dir'], str)

    def test_dir_filesystemencoding(self):
        cfg = Config(
            [('dir', config_options.Dir())],
            config_file_path=os.path.join(os.path.abspath('.'), 'mkdocs.yml'),
        )

        test_config = {
            'dir': 'Übersicht'.encode(encoding=sys.getfilesystemencoding())
        }

        cfg.load_dict(test_config)

        fails, warns = cfg.validate()

        # str does not include byte strings so validation fails
        self.assertEqual(len(fails), 1)
        self.assertEqual(len(warns), 0)

    def test_dir_bad_encoding_fails(self):
        cfg = Config(
            [('dir', config_options.Dir())],
            config_file_path=os.path.join(os.path.abspath('.'), 'mkdocs.yml'),
        )

        test_config = {
            'dir': 'юникод'.encode(encoding='ISO 8859-5')
        }

        cfg.load_dict(test_config)

        fails, warns = cfg.validate()

        self.assertEqual(len(fails), 1)
        self.assertEqual(len(warns), 0)

    def test_config_dir_prepended(self):
        base_path = os.path.abspath('.')
        cfg = Config(
            [('dir', config_options.Dir())],
            config_file_path=os.path.join(base_path, 'mkdocs.yml'),
        )

        test_config = {
            'dir': 'foo'
        }

        cfg.load_dict(test_config)

        fails, warns = cfg.validate()

        self.assertEqual(len(fails), 0)
        self.assertEqual(len(warns), 0)
        self.assertIsInstance(cfg['dir'], str)
        self.assertEqual(cfg['dir'], os.path.join(base_path, 'foo'))

    def test_dir_is_config_dir_fails(self):
        cfg = Config(
            [('dir', config_options.Dir())],
            config_file_path=os.path.join(os.path.abspath('.'), 'mkdocs.yml'),
        )

        test_config = {
            'dir': '.'
        }

        cfg.load_dict(test_config)

        fails, warns = cfg.validate()

        self.assertEqual(len(fails), 1)
        self.assertEqual(len(warns), 0)


class ListOfPathsTest(unittest.TestCase):

    def test_valid_path(self):
        paths = [os.path.dirname(__file__)]
        option = config_options.ListOfPaths()
        option.validate(paths)

    def test_missing_path(self):
        paths = [os.path.join("does", "not", "exist", "i", "hope")]
        option = config_options.ListOfPaths()
        with self.assertRaises(config_options.ValidationError):
            option.validate(paths)

    def test_empty_list(self):
        paths = []
        option = config_options.ListOfPaths()
        option.validate(paths)

    def test_non_list(self):
        paths = os.path.dirname(__file__)
        option = config_options.ListOfPaths()
        with self.assertRaises(config_options.ValidationError):
            option.validate(paths)

    def test_file(self):
        paths = [__file__]
        option = config_options.ListOfPaths()
        option.validate(paths)

    def test_paths_localized_to_config(self):
        base_path = os.path.abspath('.')
        cfg = Config(
            [('watch', config_options.ListOfPaths())],
            config_file_path=os.path.join(base_path, 'mkdocs.yml'),
        )
        test_config = {
            'watch': ['foo']
        }
        cfg.load_dict(test_config)
        fails, warns = cfg.validate()
        self.assertEqual(len(fails), 0)
        self.assertEqual(len(warns), 0)
        self.assertIsInstance(cfg['watch'], list)
        self.assertEqual(cfg['watch'], [os.path.join(base_path, 'foo')])


class SiteDirTest(unittest.TestCase):

    def validate_config(self, config):
        """ Given a config with values for site_dir and doc_dir, run site_dir post_validation. """
        site_dir = config_options.SiteDir()
        docs_dir = config_options.Dir()

        fname = os.path.join(os.path.abspath('..'), 'mkdocs.yml')

        config['docs_dir'] = docs_dir.validate(config['docs_dir'])
        config['site_dir'] = site_dir.validate(config['site_dir'])

        schema = [
            ('site_dir', site_dir),
            ('docs_dir', docs_dir),
        ]
        cfg = Config(schema, fname)
        cfg.load_dict(config)
        failed, warned = cfg.validate()

        if failed:
            raise config_options.ValidationError(failed)

        return True

    def test_doc_dir_in_site_dir(self):

        j = os.path.join
        # The parent dir is not the same on every system, so use the actual dir name
        parent_dir = mkdocs.__file__.split(os.sep)[-3]

        test_configs = (
            {'docs_dir': j('site', 'docs'), 'site_dir': 'site'},
            {'docs_dir': 'docs', 'site_dir': '.'},
            {'docs_dir': '.', 'site_dir': '.'},
            {'docs_dir': 'docs', 'site_dir': ''},
            {'docs_dir': '', 'site_dir': ''},
            {'docs_dir': j('..', parent_dir, 'docs'), 'site_dir': 'docs'},
            {'docs_dir': 'docs', 'site_dir': '/'}
        )

        for test_config in test_configs:
            with self.assertRaises(config_options.ValidationError):
                self.validate_config(test_config)

    def test_site_dir_in_docs_dir(self):

        j = os.path.join

        test_configs = (
            {'docs_dir': 'docs', 'site_dir': j('docs', 'site')},
            {'docs_dir': '.', 'site_dir': 'site'},
            {'docs_dir': '', 'site_dir': 'site'},
            {'docs_dir': '/', 'site_dir': 'site'},
        )

        for test_config in test_configs:
            with self.assertRaises(config_options.ValidationError):
                self.validate_config(test_config)

    def test_common_prefix(self):
        """ Legitimate settings with common prefixes should not fail validation. """

        test_configs = (
            {'docs_dir': 'docs', 'site_dir': 'docs-site'},
            {'docs_dir': 'site-docs', 'site_dir': 'site'},
        )

        for test_config in test_configs:
            assert self.validate_config(test_config)


class ThemeTest(unittest.TestCase):

    def test_theme_as_string(self):

        option = config_options.Theme()
        value = option.validate("mkdocs")
        self.assertEqual({'name': 'mkdocs'}, value)

    def test_uninstalled_theme_as_string(self):

        option = config_options.Theme()
        with self.assertRaises(config_options.ValidationError):
            option.validate("mkdocs2")

    def test_theme_default(self):
        option = config_options.Theme(default='mkdocs')
        value = option.validate(None)
        self.assertEqual({'name': 'mkdocs'}, value)

    def test_theme_as_simple_config(self):

        config = {
            'name': 'mkdocs'
        }
        option = config_options.Theme()
        value = option.validate(config)
        self.assertEqual(config, value)

    def test_theme_as_complex_config(self):

        config = {
            'name': 'mkdocs',
            'custom_dir': 'custom',
            'static_templates': ['sitemap.html'],
            'show_sidebar': False
        }
        option = config_options.Theme()
        value = option.validate(config)
        self.assertEqual(config, value)

    def test_theme_name_is_none(self):

        config = {
            'name': None
        }
        option = config_options.Theme()
        value = option.validate(config)
        self.assertEqual(config, value)

    def test_theme_config_missing_name(self):

        config = {
            'custom_dir': 'custom',
        }
        option = config_options.Theme()
        with self.assertRaises(config_options.ValidationError):
            option.validate(config)

    def test_uninstalled_theme_as_config(self):

        config = {
            'name': 'mkdocs2'
        }
        option = config_options.Theme()
        with self.assertRaises(config_options.ValidationError):
            option.validate(config)

    def test_theme_invalid_type(self):

        config = ['mkdocs2']
        option = config_options.Theme()
        with self.assertRaises(config_options.ValidationError):
            option.validate(config)

    def test_post_validation_none_theme_name_and_missing_custom_dir(self):

        config = {
            'theme': {
                'name': None
            }
        }
        option = config_options.Theme()
        with self.assertRaises(config_options.ValidationError):
            option.post_validation(config, 'theme')

    @tempdir()
    def test_post_validation_inexisting_custom_dir(self, abs_base_path):

        config = {
            'theme': {
                'name': None,
                'custom_dir': abs_base_path + '/inexisting_custom_dir',
            }
        }
        option = config_options.Theme()
        with self.assertRaises(config_options.ValidationError):
            option.post_validation(config, 'theme')

    def test_post_validation_locale_none(self):

        config = {
            'theme': {
                'name': 'mkdocs',
                'locale': None
            }
        }
        option = config_options.Theme()
        with self.assertRaises(config_options.ValidationError):
            option.post_validation(config, 'theme')

    def test_post_validation_locale_invalid_type(self):

        config = {
            'theme': {
                'name': 'mkdocs',
                'locale': 0
            }
        }
        option = config_options.Theme()
        with self.assertRaises(config_options.ValidationError):
            option.post_validation(config, 'theme')

    def test_post_validation_locale(self):

        config = {
            'theme': {
                'name': 'mkdocs',
                'locale': 'fr'
            }
        }
        option = config_options.Theme()
        option.post_validation(config, 'theme')
        self.assertEqual('fr', config['theme']['locale'].language)


class NavTest(unittest.TestCase):

    def test_old_format(self):
        option = config_options.Nav()
        with self.assertRaises(config_options.ValidationError) as cm:
            option.validate([['index.md']])
        self.assertEqual(str(cm.exception), "Expected nav item to be a string or dict, got a list: ['index.md']")

    def test_provided_dict(self):
        option = config_options.Nav()
        value = option.validate([
            'index.md',
            {"Page": "page.md"}
        ])
        self.assertEqual(['index.md', {'Page': 'page.md'}], value)

        option.post_validation({'extra_stuff': []}, 'extra_stuff')
        self.assertEqual(option.warnings, [])

    def test_provided_empty(self):
        option = config_options.Nav()
        value = option.validate([])
        self.assertEqual(None, value)

        option.post_validation({'extra_stuff': []}, 'extra_stuff')
        self.assertEqual(option.warnings, [])

    def test_normal_nav(self):
        nav = yaml_load(textwrap.dedent('''\
            - Home: index.md
            - getting-started.md
            - User Guide:
                - Overview: user-guide/index.md
                - Installation: user-guide/installation.md
        ''').encode())

        option = config_options.Nav()
        self.assertEqual(option.validate(nav), nav)
        self.assertEqual(option.warnings, [])

    def test_invalid_type_dict(self):
        option = config_options.Nav()
        with self.assertRaises(config_options.ValidationError) as cm:
            option.validate({})
        self.assertEqual(str(cm.exception), "Expected nav to be a list, got a dict: {}")

    def test_invalid_type_int(self):
        option = config_options.Nav()
        with self.assertRaises(config_options.ValidationError) as cm:
            option.validate(5)
        self.assertEqual(str(cm.exception), "Expected nav to be a list, got a int: 5")

    def test_invalid_item_int(self):
        option = config_options.Nav()
        with self.assertRaises(config_options.ValidationError) as cm:
            option.validate([1])
        self.assertEqual(str(cm.exception), "Expected nav item to be a string or dict, got a int: 1")

    def test_invalid_item_none(self):
        option = config_options.Nav()
        with self.assertRaises(config_options.ValidationError) as cm:
            option.validate([None])
        self.assertEqual(str(cm.exception), "Expected nav item to be a string or dict, got None")

    def test_invalid_children_config_int(self):
        option = config_options.Nav()
        with self.assertRaises(config_options.ValidationError) as cm:
            option.validate([{"foo.md": [{"bar.md": 1}]}])
        self.assertEqual(str(cm.exception), "Expected nav to be a list, got a int: 1")

    def test_invalid_children_config_none(self):
        option = config_options.Nav()
        with self.assertRaises(config_options.ValidationError) as cm:
            option.validate([{"foo.md": None}])
        self.assertEqual(str(cm.exception), "Expected nav to be a list, got None")

    def test_invalid_children_empty_dict(self):
        option = config_options.Nav()
        nav = ['foo', {}]
        with self.assertRaises(config_options.ValidationError) as cm:
            option.validate(nav)
        self.assertEqual(str(cm.exception), "Expected nav item to be a dict of size 1, got a dict: {}")

    def test_invalid_nested_list(self):
        option = config_options.Nav()
        nav = [{'aaa': [[{"bbb": "user-guide/index.md"}]]}]
        with self.assertRaises(config_options.ValidationError) as cm:
            option.validate(nav)
        msg = "Expected nav item to be a string or dict, got a list: [{'bbb': 'user-guide/index.md'}]"
        self.assertEqual(str(cm.exception), msg)

    def test_invalid_children_oversized_dict(self):
        option = config_options.Nav()
        nav = [{"aaa": [{"bbb": "user-guide/index.md", "ccc": "user-guide/installation.md"}]}]
        with self.assertRaises(config_options.ValidationError) as cm:
            option.validate(nav)
        msg = "Expected nav item to be a dict of size 1, got dict with keys ('bbb', 'ccc')"
        self.assertEqual(str(cm.exception), msg)

    def test_warns_for_dict(self):
        option = config_options.Nav()
        option.validate([{"a": {"b": "c.md", "d": "e.md"}}])
        self.assertEqual(option.warnings, ["Expected nav to be a list, got dict with keys ('b', 'd')"])


class PrivateTest(unittest.TestCase):

    def test_defined(self):

        option = config_options.Private()
        with self.assertRaises(config_options.ValidationError):
            option.validate('somevalue')


class MarkdownExtensionsTest(unittest.TestCase):

    @patch('markdown.Markdown')
    def test_simple_list(self, mockMd):
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

    @patch('markdown.Markdown')
    def test_list_dicts(self, mockMd):
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

    @patch('markdown.Markdown')
    def test_mixed_list(self, mockMd):
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

    @patch('markdown.Markdown')
    def test_dict_of_dicts(self, mockMd):
        option = config_options.MarkdownExtensions()
        config = {
            'markdown_extensions': {
                'foo': {'foo_option': 'foo value'},
                'bar': {'bar_option': 'bar value'},
                'baz': {}
            }
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

    @patch('markdown.Markdown')
    def test_builtins(self, mockMd):
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

    @patch('markdown.Markdown')
    def test_configkey(self, mockMd):
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

    @patch('markdown.Markdown')
    def test_not_list(self, mockMd):
        option = config_options.MarkdownExtensions()
        with self.assertRaises(config_options.ValidationError):
            option.validate('not a list')

    @patch('markdown.Markdown')
    def test_invalid_config_option(self, mockMd):
        option = config_options.MarkdownExtensions()
        config = {
            'markdown_extensions': [
                {'foo': 'not a dict'}
            ]
        }
        with self.assertRaises(config_options.ValidationError):
            option.validate(config['markdown_extensions'])

    @patch('markdown.Markdown')
    def test_invalid_config_item(self, mockMd):
        option = config_options.MarkdownExtensions()
        config = {
            'markdown_extensions': [
                ['not a dict']
            ]
        }
        with self.assertRaises(config_options.ValidationError):
            option.validate(config['markdown_extensions'])

    @patch('markdown.Markdown')
    def test_invalid_dict_item(self, mockMd):
        option = config_options.MarkdownExtensions()
        config = {
            'markdown_extensions': [
                {'key1': 'value', 'key2': 'too many keys'}
            ]
        }
        with self.assertRaises(config_options.ValidationError):
            option.validate(config['markdown_extensions'])

    def test_unknown_extension(self):
        option = config_options.MarkdownExtensions()
        config = {
            'markdown_extensions': ['unknown']
        }
        with self.assertRaises(config_options.ValidationError):
            option.validate(config['markdown_extensions'])

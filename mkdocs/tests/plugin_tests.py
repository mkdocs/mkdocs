#!/usr/bin/env python


import unittest
from unittest import mock
import os

from mkdocs import plugins
from mkdocs import config


class DummyPlugin(plugins.BasePlugin):
    config_scheme = (
        ('foo', config.config_options.Type(str, default='default foo')),
        ('bar', config.config_options.Type(int, default=0)),
        ('dir', config.config_options.Dir(exists=False)),
    )

    def on_pre_page(self, content, **kwargs):
        """ modify page content by prepending `foo` config value. """
        return '{} {}'.format(self.config['foo'], content)

    def on_nav(self, item, **kwargs):
        """ do nothing (return None) to not modify item. """
        return None

    def on_page_read_source(self, **kwargs):
        """ create new source by prepending `foo` config value to 'source'. """
        return '{} {}'.format(self.config['foo'], 'source')

    def on_pre_build(self, **kwargs):
        """ do nothing (return None). """
        return None


class TestPluginClass(unittest.TestCase):

    def test_valid_plugin_options(self):
        test_dir = 'test'

        options = {
            'foo': 'some value',
            'dir': test_dir,
        }

        cfg_fname = os.path.join('tmp', 'test', 'fname.yml')
        cfg_fname = os.path.abspath(cfg_fname)

        cfg_dirname = os.path.dirname(cfg_fname)
        expected = os.path.join(cfg_dirname, test_dir)

        expected = {
            'foo': 'some value',
            'bar': 0,
            'dir': expected,
        }

        plugin = DummyPlugin()
        errors, warnings = plugin.load_config(options, config_file_path=cfg_fname)
        self.assertEqual(plugin.config, expected)
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])

    def test_invalid_plugin_options(self):

        plugin = DummyPlugin()
        errors, warnings = plugin.load_config({'foo': 42})
        self.assertEqual(len(errors), 1)
        self.assertIn('foo', errors[0])
        self.assertEqual(warnings, [])

        errors, warnings = plugin.load_config({'bar': 'a string'})
        self.assertEqual(len(errors), 1)
        self.assertIn('bar', errors[0])
        self.assertEqual(warnings, [])

        errors, warnings = plugin.load_config({'invalid_key': 'value'})
        self.assertEqual(errors, [])
        self.assertEqual(len(warnings), 1)
        self.assertIn('invalid_key', warnings[0])


class TestPluginCollection(unittest.TestCase):

    def test_set_plugin_on_collection(self):
        collection = plugins.PluginCollection()
        plugin = DummyPlugin()
        collection['foo'] = plugin
        self.assertEqual([(k, v) for k, v in collection.items()], [('foo', plugin)])

    def test_set_multiple_plugins_on_collection(self):
        collection = plugins.PluginCollection()
        plugin1 = DummyPlugin()
        collection['foo'] = plugin1
        plugin2 = DummyPlugin()
        collection['bar'] = plugin2
        self.assertEqual([(k, v) for k, v in collection.items()], [('foo', plugin1), ('bar', plugin2)])

    def test_run_event_on_collection(self):
        collection = plugins.PluginCollection()
        plugin = DummyPlugin()
        plugin.load_config({'foo': 'new'})
        collection['foo'] = plugin
        self.assertEqual(collection.run_event('pre_page', 'page content'), 'new page content')

    def test_run_event_twice_on_collection(self):
        collection = plugins.PluginCollection()
        plugin1 = DummyPlugin()
        plugin1.load_config({'foo': 'new'})
        collection['foo'] = plugin1
        plugin2 = DummyPlugin()
        plugin2.load_config({'foo': 'second'})
        collection['bar'] = plugin2
        self.assertEqual(collection.run_event('pre_page', 'page content'),
                         'second new page content')

    def test_event_returns_None(self):
        collection = plugins.PluginCollection()
        plugin = DummyPlugin()
        plugin.load_config({'foo': 'new'})
        collection['foo'] = plugin
        self.assertEqual(collection.run_event('nav', 'nav item'), 'nav item')

    def test_event_empty_item(self):
        collection = plugins.PluginCollection()
        plugin = DummyPlugin()
        plugin.load_config({'foo': 'new'})
        collection['foo'] = plugin
        self.assertEqual(collection.run_event('page_read_source'), 'new source')

    def test_event_empty_item_returns_None(self):
        collection = plugins.PluginCollection()
        plugin = DummyPlugin()
        plugin.load_config({'foo': 'new'})
        collection['foo'] = plugin
        self.assertEqual(collection.run_event('pre_build'), None)

    def test_run_undefined_event_on_collection(self):
        collection = plugins.PluginCollection()
        self.assertEqual(collection.run_event('pre_page', 'page content'), 'page content')

    def test_run_unknown_event_on_collection(self):
        collection = plugins.PluginCollection()
        self.assertRaises(KeyError, collection.run_event, 'unknown', 'page content')


MockEntryPoint = mock.Mock()
MockEntryPoint.configure_mock(**{'name': 'sample', 'load.return_value': DummyPlugin})


@mock.patch('pkg_resources.iter_entry_points', return_value=[MockEntryPoint])
class TestPluginConfig(unittest.TestCase):

    def test_plugin_config_without_options(self, mock_class):

        cfg = {'plugins': ['sample']}
        option = config.config_options.Plugins()
        cfg['plugins'] = option.validate(cfg['plugins'])

        self.assertIsInstance(cfg['plugins'], plugins.PluginCollection)
        self.assertIn('sample', cfg['plugins'])
        self.assertIsInstance(cfg['plugins']['sample'], plugins.BasePlugin)
        expected = {
            'foo': 'default foo',
            'bar': 0,
            'dir': None,
        }
        self.assertEqual(cfg['plugins']['sample'].config, expected)

    def test_plugin_config_with_options(self, mock_class):

        cfg = {
            'plugins': [{
                'sample': {
                    'foo': 'foo value',
                    'bar': 42
                }
            }]
        }
        option = config.config_options.Plugins()
        cfg['plugins'] = option.validate(cfg['plugins'])

        self.assertIsInstance(cfg['plugins'], plugins.PluginCollection)
        self.assertIn('sample', cfg['plugins'])
        self.assertIsInstance(cfg['plugins']['sample'], plugins.BasePlugin)
        expected = {
            'foo': 'foo value',
            'bar': 42,
            'dir': None,
        }
        self.assertEqual(cfg['plugins']['sample'].config, expected)

    def test_plugin_config_empty_list_with_empty_default(self, mock_class):
        cfg = {'plugins': []}
        option = config.config_options.Plugins(default=[])
        cfg['plugins'] = option.validate(cfg['plugins'])

        self.assertIsInstance(cfg['plugins'], plugins.PluginCollection)
        self.assertEqual(len(cfg['plugins']), 0)

    def test_plugin_config_empty_list_with_default(self, mock_class):
        # Default is ignored
        cfg = {'plugins': []}
        option = config.config_options.Plugins(default=['sample'])
        cfg['plugins'] = option.validate(cfg['plugins'])

        self.assertIsInstance(cfg['plugins'], plugins.PluginCollection)
        self.assertEqual(len(cfg['plugins']), 0)

    def test_plugin_config_none_with_empty_default(self, mock_class):
        cfg = {'plugins': None}
        option = config.config_options.Plugins(default=[])
        cfg['plugins'] = option.validate(cfg['plugins'])

        self.assertIsInstance(cfg['plugins'], plugins.PluginCollection)
        self.assertEqual(len(cfg['plugins']), 0)

    def test_plugin_config_none_with_default(self, mock_class):
        # Default is used.
        cfg = {'plugins': None}
        option = config.config_options.Plugins(default=['sample'])
        cfg['plugins'] = option.validate(cfg['plugins'])

        self.assertIsInstance(cfg['plugins'], plugins.PluginCollection)
        self.assertIn('sample', cfg['plugins'])
        self.assertIsInstance(cfg['plugins']['sample'], plugins.BasePlugin)
        expected = {
            'foo': 'default foo',
            'bar': 0,
            'dir': None,
        }
        self.assertEqual(cfg['plugins']['sample'].config, expected)

    def test_plugin_config_uninstalled(self, mock_class):

        cfg = {'plugins': ['uninstalled']}
        option = config.config_options.Plugins()
        self.assertRaises(config.base.ValidationError, option.validate, cfg['plugins'])

    def test_plugin_config_not_list(self, mock_class):

        cfg = {'plugins': 'sample'}  # should be a list
        option = config.config_options.Plugins()
        self.assertRaises(config.base.ValidationError, option.validate, cfg['plugins'])

    def test_plugin_config_multivalue_dict(self, mock_class):

        cfg = {
            'plugins': [{
                'sample': {
                    'foo': 'foo value',
                    'bar': 42
                },
                'extra_key': 'baz'
            }]
        }
        option = config.config_options.Plugins()
        self.assertRaises(config.base.ValidationError, option.validate, cfg['plugins'])

    def test_plugin_config_not_string_or_dict(self, mock_class):

        cfg = {
            'plugins': [('not a string or dict',)]
        }
        option = config.config_options.Plugins()
        self.assertRaises(config.base.ValidationError, option.validate, cfg['plugins'])

    def test_plugin_config_options_not_dict(self, mock_class):

        cfg = {
            'plugins': [{
                'sample': 'not a dict'
            }]
        }
        option = config.config_options.Plugins()
        self.assertRaises(config.base.ValidationError, option.validate, cfg['plugins'])

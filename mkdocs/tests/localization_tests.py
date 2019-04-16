#!/usr/bin/env python
# coding: utf-8

from __future__ import unicode_literals

import unittest
import mock

from mkdocs.localization import install_translations
from mkdocs.tests.base import load_config, tempdir


class LocalizationTests(unittest.TestCase):

    def setUp(self):
        self.env = mock.Mock()

    def test_jinja_extension_installed(self):
        config = load_config()
        install_translations(self.env, config)
        self.env.add_extension.assert_called_once_with('jinja2.ext.i18n')

    @tempdir()
    def test_no_translations_found(self, dir_without_translations):
        config = load_config()
        config['theme']['locale'] = 'fr_CA'
        config['theme'].dirs = [dir_without_translations]

        install_translations(self.env, config)

        self.env.install_null_translations.assert_called_once()

    def test_translations_found(self):
        config = load_config()
        config['theme']['locale'] = 'en'
        translations = mock.Mock()

        with mock.patch('mkdocs.localization.Translations.load', return_value=translations):
            install_translations(self.env, config)

        self.env.install_gettext_translations.assert_called_once_with(translations)

    @tempdir()
    @tempdir()
    def test_merge_translations(self, custom_dir, theme_dir):
        config = load_config()
        custom_dir_translations = mock.Mock()
        theme_dir_translations = mock.Mock()
        config['theme'].dirs = [custom_dir, theme_dir]

        def side_effet(*args, **kwargs):
            dirname = args[0]
            if dirname.startswith(custom_dir):
                return custom_dir_translations
            elif dirname.startswith(theme_dir):
                return theme_dir_translations
            else:
                self.fail()

        with mock.patch('mkdocs.localization.Translations.load', side_effect=side_effet):
            install_translations(self.env, config)

        theme_dir_translations.merge.assert_called_once_with(custom_dir_translations)

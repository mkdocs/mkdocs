import unittest
from distutils.dist import Distribution
from distutils.errors import DistutilsOptionError
from os import path

from mkdocs.commands import babel

BASE_DIR = path.normpath(path.join(path.abspath(path.dirname(__file__)), '../../'))


class ThemeMixinTests(unittest.TestCase):

    def test_dict_entry_point(self):
        inst = babel.ThemeMixin()
        inst.distribution = Distribution()
        inst.distribution.entry_points = {
            'mkdocs.themes': [
                'mkdocs = mkdocs.themes.mkdocs'
            ]
        }
        inst.theme = 'mkdocs'
        self.assertEqual(inst.get_theme_dir(), path.join(BASE_DIR, 'mkdocs', 'themes', 'mkdocs'))

    def test_ini_entry_point(self):
        inst = babel.ThemeMixin()
        inst.distribution = Distribution()
        inst.distribution.entry_points = '''
            [mkdocs.themes]
            mkdocs = mkdocs.themes.mkdocs
        '''
        inst.theme = 'mkdocs'
        self.assertEqual(inst.get_theme_dir(), path.join(BASE_DIR, 'mkdocs', 'themes', 'mkdocs'))

    def test_multiple_entry_points(self):
        inst = babel.ThemeMixin()
        inst.distribution = Distribution()
        inst.distribution.entry_points = {
            'mkdocs.themes': [
                'mkdocs = mkdocs.themes.mkdocs',
                'readthedocs = mkdocs.themes.readthedocs',
            ]
        }
        inst.theme = 'readthedocs'
        self.assertEqual(inst.get_theme_dir(), path.join(BASE_DIR, 'mkdocs', 'themes', 'readthedocs'))

    def test_no_entry_points(self):
        inst = babel.ThemeMixin()
        inst.distribution = Distribution()
        inst.distribution.entry_points = {}
        inst.theme = 'mkdocs'
        self.assertRaises(DistutilsOptionError, inst.get_theme_dir)

    def test_undefined_entry_point(self):
        inst = babel.ThemeMixin()
        inst.distribution = Distribution()
        inst.distribution.entry_points = {
            'mkdocs.themes': [
                'mkdocs = mkdocs.themes.mkdocs'
            ]
        }
        inst.theme = 'undefined'
        self.assertRaises(DistutilsOptionError, inst.get_theme_dir)


class CommandTests(unittest.TestCase):

    def test_compile_catalog(self):
        dist = Distribution()
        dist.entry_points = '''
            [mkdocs.themes]
            mkdocs = mkdocs.themes.mkdocs
        '''
        cmd = babel.compile_catalog(dist)
        cmd.initialize_options()
        cmd.theme = 'mkdocs'
        cmd.finalize_options()
        self.assertEqual(cmd.directory, path.join(BASE_DIR, 'mkdocs', 'themes', 'mkdocs/locales'))

    def test_extract_messages(self):
        dist = Distribution(dict(name='foo', version='1.2'))
        dist.entry_points = '''
            [mkdocs.themes]
            mkdocs = mkdocs.themes.mkdocs
        '''
        cmd = babel.extract_messages(dist)
        cmd.initialize_options()
        cmd.theme = 'mkdocs'
        cmd.finalize_options()
        self.assertEqual(cmd.input_paths, [path.join(BASE_DIR, 'mkdocs', 'themes', 'mkdocs')])
        self.assertEqual(cmd.output_file, path.join(BASE_DIR, 'mkdocs', 'themes', 'mkdocs/messages.pot'))
        self.assertEqual(cmd.mapping_file, babel.DEFAULT_MAPPING_FILE)
        self.assertEqual(cmd.project, 'foo')
        self.assertEqual(cmd.version, '1.2')

    def test_init_catalog(self):
        dist = Distribution()
        dist.entry_points = '''
            [mkdocs.themes]
            mkdocs = mkdocs.themes.mkdocs
        '''
        cmd = babel.init_catalog(dist)
        cmd.initialize_options()
        cmd.theme = 'mkdocs'
        cmd.locale = 'en'
        cmd.finalize_options()
        self.assertEqual(cmd.input_file, path.join(BASE_DIR, 'mkdocs', 'themes', 'mkdocs/messages.pot'))
        self.assertEqual(cmd.output_dir, path.join(BASE_DIR, 'mkdocs', 'themes', 'mkdocs/locales'))

    def test_update_catalog(self):
        dist = Distribution()
        dist.entry_points = '''
            [mkdocs.themes]
            mkdocs = mkdocs.themes.mkdocs
        '''
        cmd = babel.update_catalog(dist)
        cmd.initialize_options()
        cmd.theme = 'mkdocs'
        cmd.finalize_options()
        self.assertEqual(cmd.input_file, path.join(BASE_DIR, 'mkdocs', 'themes', 'mkdocs/messages.pot'))
        self.assertEqual(cmd.output_dir, path.join(BASE_DIR, 'mkdocs', 'themes', 'mkdocs/locales'))

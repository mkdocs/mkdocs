import os
import unittest
from unittest import mock

import mkdocs
from mkdocs.localization import parse_locale
from mkdocs.tests.base import tempdir
from mkdocs.theme import Theme

abs_path = os.path.abspath(os.path.dirname(__file__))
mkdocs_dir = os.path.abspath(os.path.dirname(mkdocs.__file__))
mkdocs_templates_dir = os.path.join(mkdocs_dir, 'templates')
theme_dir = os.path.abspath(os.path.join(mkdocs_dir, 'themes'))


class ThemeTests(unittest.TestCase):
    def test_simple_theme(self):
        theme = Theme(name='mkdocs')
        self.assertEqual(
            theme.dirs,
            [os.path.join(theme_dir, 'mkdocs'), mkdocs_templates_dir],
        )
        self.assertEqual(theme.static_templates, {'404.html', 'sitemap.xml'})
        self.assertEqual(
            dict(theme),
            {
                'name': 'mkdocs',
                'color_mode': 'light',
                'user_color_mode_toggle': False,
                'locale': parse_locale('en'),
                'include_search_page': False,
                'search_index_only': False,
                'analytics': {'gtag': None},
                'highlightjs': True,
                'hljs_style': 'github',
                'hljs_style_dark': 'github-dark',
                'hljs_languages': [],
                'navigation_depth': 2,
                'nav_style': 'primary',
                'shortcuts': {'help': 191, 'next': 78, 'previous': 80, 'search': 83},
            },
        )

    @tempdir()
    def test_custom_dir(self, custom):
        theme = Theme(name='mkdocs', custom_dir=custom)
        self.assertEqual(
            theme.dirs,
            [
                custom,
                os.path.join(theme_dir, 'mkdocs'),
                mkdocs_templates_dir,
            ],
        )

    @tempdir()
    def test_custom_dir_only(self, custom):
        theme = Theme(name=None, custom_dir=custom)
        self.assertEqual(
            theme.dirs,
            [custom, mkdocs_templates_dir],
        )

    def static_templates(self):
        theme = Theme(name='mkdocs', static_templates='foo.html')
        self.assertEqual(
            theme.static_templates,
            {'404.html', 'sitemap.xml', 'foo.html'},
        )

    def test_vars(self):
        theme = Theme(name='mkdocs', foo='bar', baz=True)
        self.assertEqual(theme['foo'], 'bar')
        self.assertTrue(theme['baz'])
        self.assertTrue('new' not in theme)
        with self.assertRaises(KeyError):
            theme['new']
        theme['new'] = 42
        self.assertTrue('new' in theme)
        self.assertEqual(theme['new'], 42)

    @mock.patch('yaml.load', return_value={})
    def test_no_theme_config(self, m):
        theme = Theme(name='mkdocs')
        self.assertEqual(m.call_count, 1)
        self.assertEqual(theme.static_templates, {'sitemap.xml'})

    def test_inherited_theme(self):
        m = mock.Mock(
            side_effect=[
                {'extends': 'readthedocs', 'static_templates': ['child.html']},
                {'static_templates': ['parent.html']},
            ]
        )
        with mock.patch('yaml.load', m) as m:
            theme = Theme(name='mkdocs')
            self.assertEqual(m.call_count, 2)
            self.assertEqual(
                theme.dirs,
                [
                    os.path.join(theme_dir, 'mkdocs'),
                    os.path.join(theme_dir, 'readthedocs'),
                    mkdocs_templates_dir,
                ],
            )
            self.assertEqual(theme.static_templates, {'sitemap.xml', 'child.html', 'parent.html'})

    def test_empty_config_file(self):
        # Test for themes with *empty* mkdocs_theme.yml.
        # See https://github.com/mkdocs/mkdocs/issues/3699
        m = mock.Mock(
            # yaml.load returns "None" for an empty file
            side_effect=[None]
        )
        with mock.patch('yaml.load', m) as m:
            theme = Theme(name='mkdocs')
            # Should only have the default name and locale __vars set in
            # Theme.__init__()
            self.assertEqual(
                dict(theme),
                {
                    'name': 'mkdocs',
                    'locale': parse_locale('en'),
                },
            )

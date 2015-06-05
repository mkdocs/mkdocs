from __future__ import unicode_literals
import unittest

from mkdocs import legacy, utils


class TestCompatabilityShim(unittest.TestCase):

    # TODO: Remove in 1.0

    def test_convert(self):

        self.maxDiff = None

        pages_yaml_old = """
        pages:
        - ['index.md', 'Home']
        - ['user-guide/writing-your-docs.md', 'User Guide']
        - ['user-guide/styling-your-docs.md', 'User Guide']
        - ['about/license.md', 'About', 'License']
        - ['about/release-notes.md', 'About']
        - ['about/contributing.md', 'About', 'Contributing']
        - ['help/contributing.md', 'Help', 'Contributing']
        - ['support.md']
        - ['cli.md', 'CLI Guide']
        """

        pages_yaml_new = """
        pages:
        - Home: index.md
        - User Guide:
            - user-guide/writing-your-docs.md
            - user-guide/styling-your-docs.md
        - About:
            - License: about/license.md
            - about/release-notes.md
            - Contributing: about/contributing.md
        - Help:
            - Contributing: help/contributing.md
        - support.md
        - CLI Guide: cli.md
        """
        self.assertEqual(
            legacy.pages_compat_shim(utils.yaml_load(pages_yaml_old)['pages']),
            utils.yaml_load(pages_yaml_new)['pages'])

    def test_convert_no_home(self):

        self.maxDiff = None

        pages_yaml_old = """
        pages:
        - ['index.md']
        - ['about.md', 'About']
        """

        pages_yaml_new = """
        pages:
        - index.md
        - About: about.md
        """
        self.assertEqual(
            legacy.pages_compat_shim(utils.yaml_load(pages_yaml_old)['pages']),
            utils.yaml_load(pages_yaml_new)['pages'])

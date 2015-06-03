from __future__ import unicode_literals
import os
import tempfile
import unittest

from mkdocs import exceptions
from mkdocs.config import base, defaults


class ConfigBaseTests(unittest.TestCase):

    def test_unrecognised_keys(self):

        c = base.Config(schema=defaults.DEFAULT_SCHEMA)
        c.load_dict({
            'not_a_valid_config_option': "test"
        })

        failed, warnings = c.validate()

        self.assertEqual(warnings, [
            ('not_a_valid_config_option',
                'Unrecognised configuration name: not_a_valid_config_option')
        ])

    def test_missing_required(self):

        c = base.Config(schema=defaults.DEFAULT_SCHEMA)

        errors, warnings = c.validate()

        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0][0], 'site_name')
        self.assertEqual(str(errors[0][1]), 'Required configuration not provided.')

        self.assertEqual(len(warnings), 0)

    def test_load_missing_required(self):
        """
        Users can explicitly set the config file using the '--config' option.
        Allows users to specify a config other than the default `mkdocs.yml`.
        """

        config_file = tempfile.NamedTemporaryFile('w', delete=False)
        try:
            config_file.write(
                "site_dir: output\nsite_uri: http://www.mkdocs.org\n")
            config_file.flush()
            config_file.close()

            self.assertRaises(exceptions.ConfigurationError,
                              base.load_config, config_file=config_file.name)
        finally:
            os.remove(config_file.name)

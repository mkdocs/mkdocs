import os
import unittest

from mkdocs import exceptions
from mkdocs.config import base, defaults
from mkdocs.config.config_options import BaseConfigOption
from mkdocs.tests.base import change_dir, tempdir


class ConfigBaseTests(unittest.TestCase):
    def test_unrecognised_keys(self):
        c = base.Config(schema=defaults.get_schema())
        c.load_dict(
            {
                'not_a_valid_config_option': "test",
            }
        )

        failed, warnings = c.validate()

        self.assertEqual(
            warnings,
            [
                (
                    'not_a_valid_config_option',
                    'Unrecognised configuration name: not_a_valid_config_option',
                )
            ],
        )

    def test_missing_required(self):
        c = base.Config(schema=defaults.get_schema())

        errors, warnings = c.validate()

        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0][0], 'site_name')
        self.assertEqual(str(errors[0][1]), 'Required configuration not provided.')

        self.assertEqual(len(warnings), 0)

    @tempdir()
    def test_load_from_file(self, temp_dir):
        """
        Users can explicitly set the config file using the '--config' option.
        Allows users to specify a config other than the default `mkdocs.yml`.
        """
        with open(os.path.join(temp_dir, 'mkdocs.yml'), 'w') as config_file:
            config_file.write("site_name: MkDocs Test\n")
        os.mkdir(os.path.join(temp_dir, 'docs'))

        cfg = base.load_config(config_file=config_file.name)
        self.assertTrue(isinstance(cfg, base.Config))
        self.assertEqual(cfg['site_name'], 'MkDocs Test')

    @tempdir()
    def test_load_default_file(self, temp_dir):
        """
        test that `mkdocs.yml` will be loaded when '--config' is not set.
        """
        with open(os.path.join(temp_dir, 'mkdocs.yml'), 'w') as config_file:
            config_file.write("site_name: MkDocs Test\n")
        os.mkdir(os.path.join(temp_dir, 'docs'))
        with change_dir(temp_dir):
            cfg = base.load_config(config_file=None)
            self.assertTrue(isinstance(cfg, base.Config))
            self.assertEqual(cfg['site_name'], 'MkDocs Test')

    @tempdir
    def test_load_default_file_with_yaml(self, temp_dir):
        """
        test that `mkdocs.yml` will be loaded when '--config' is not set.
        """
        with open(os.path.join(temp_dir, 'mkdocs.yaml'), 'w') as config_file:
            config_file.write("site_name: MkDocs Test\n")
        os.mkdir(os.path.join(temp_dir, 'docs'))
        with change_dir(temp_dir):
            cfg = base.load_config(config_file=None)
            self.assertTrue(isinstance(cfg, base.Config))
            self.assertEqual(cfg['site_name'], 'MkDocs Test')

    @tempdir()
    def test_load_default_file_prefer_yml(self, temp_dir):
        """
        test that `mkdocs.yml` will be loaded when '--config' is not set.
        """
        with open(os.path.join(temp_dir, 'mkdocs.yml'), 'w') as config_file1:
            config_file1.write("site_name: MkDocs Test1\n")
        with open(os.path.join(temp_dir, 'mkdocs.yaml'), 'w') as config_file2:
            config_file2.write("site_name: MkDocs Test2\n")

        os.mkdir(os.path.join(temp_dir, 'docs'))
        with change_dir(temp_dir):
            cfg = base.load_config(config_file=None)
            self.assertTrue(isinstance(cfg, base.Config))
            self.assertEqual(cfg['site_name'], 'MkDocs Test1')

    def test_load_from_missing_file(self):
        with self.assertRaisesRegex(
            exceptions.ConfigurationError, "Config file 'missing_file.yml' does not exist."
        ):
            base.load_config(config_file='missing_file.yml')

    @tempdir()
    def test_load_from_open_file(self, temp_path):
        """
        `load_config` can accept an open file descriptor.
        """
        config_fname = os.path.join(temp_path, 'mkdocs.yml')
        config_file = open(config_fname, 'w+')
        config_file.write("site_name: MkDocs Test\n")
        config_file.flush()
        os.mkdir(os.path.join(temp_path, 'docs'))

        cfg = base.load_config(config_file=config_file)
        self.assertTrue(isinstance(cfg, base.Config))
        self.assertEqual(cfg['site_name'], 'MkDocs Test')
        # load_config will always close the file
        self.assertTrue(config_file.closed)

    @tempdir()
    def test_load_from_closed_file(self, temp_dir):
        """
        The `serve` command with auto-reload may pass in a closed file descriptor.
        Ensure `load_config` reloads the closed file.
        """
        with open(os.path.join(temp_dir, 'mkdocs.yml'), 'w') as config_file:
            config_file.write("site_name: MkDocs Test\n")
        os.mkdir(os.path.join(temp_dir, 'docs'))

        cfg = base.load_config(config_file=config_file)
        self.assertTrue(isinstance(cfg, base.Config))
        self.assertEqual(cfg['site_name'], 'MkDocs Test')

    @tempdir
    def test_load_missing_required(self, temp_dir):
        """
        `site_name` is a required setting.
        """
        with open(os.path.join(temp_dir, 'mkdocs.yml'), 'w') as config_file:
            config_file.write("site_dir: output\nsite_url: https://www.mkdocs.org\n")
        os.mkdir(os.path.join(temp_dir, 'docs'))

        with self.assertLogs('mkdocs') as cm:
            with self.assertRaises(exceptions.Abort):
                base.load_config(config_file=config_file.name)
        self.assertEqual(
            '\n'.join(cm.output),
            "ERROR:mkdocs.config:Config value: 'site_name'. Error: Required configuration not provided.",
        )

    def test_pre_validation_error(self):
        class InvalidConfigOption(BaseConfigOption):
            def pre_validation(self, config, key_name):
                raise base.ValidationError('pre_validation error')

        c = base.Config(schema=(('invalid_option', InvalidConfigOption()),))

        errors, warnings = c.validate()

        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0][0], 'invalid_option')
        self.assertEqual(str(errors[0][1]), 'pre_validation error')
        self.assertTrue(isinstance(errors[0][1], base.ValidationError))
        self.assertEqual(len(warnings), 0)

    def test_run_validation_error(self):
        class InvalidConfigOption(BaseConfigOption):
            def run_validation(self, value):
                raise base.ValidationError('run_validation error')

        c = base.Config(schema=(('invalid_option', InvalidConfigOption()),))

        errors, warnings = c.validate()

        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0][0], 'invalid_option')
        self.assertEqual(str(errors[0][1]), 'run_validation error')
        self.assertTrue(isinstance(errors[0][1], base.ValidationError))
        self.assertEqual(len(warnings), 0)

    def test_post_validation_error(self):
        class InvalidConfigOption(BaseConfigOption):
            def post_validation(self, config, key_name):
                raise base.ValidationError('post_validation error')

        c = base.Config(schema=(('invalid_option', InvalidConfigOption()),))

        errors, warnings = c.validate()

        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0][0], 'invalid_option')
        self.assertEqual(str(errors[0][1]), 'post_validation error')
        self.assertTrue(isinstance(errors[0][1], base.ValidationError))
        self.assertEqual(len(warnings), 0)

    def test_pre_and_run_validation_errors(self):
        """A pre_validation error does not stop run_validation from running."""

        class InvalidConfigOption(BaseConfigOption):
            def pre_validation(self, config, key_name):
                raise base.ValidationError('pre_validation error')

            def run_validation(self, value):
                raise base.ValidationError('run_validation error')

        c = base.Config(schema=(('invalid_option', InvalidConfigOption()),))

        errors, warnings = c.validate()

        self.assertEqual(len(errors), 2)
        self.assertEqual(errors[0][0], 'invalid_option')
        self.assertEqual(str(errors[0][1]), 'pre_validation error')
        self.assertTrue(isinstance(errors[0][1], base.ValidationError))
        self.assertEqual(errors[1][0], 'invalid_option')
        self.assertEqual(str(errors[1][1]), 'run_validation error')
        self.assertTrue(isinstance(errors[1][1], base.ValidationError))
        self.assertEqual(len(warnings), 0)

    def test_run_and_post_validation_errors(self):
        """A run_validation error stops post_validation from running."""

        class InvalidConfigOption(BaseConfigOption):
            def run_validation(self, value):
                raise base.ValidationError('run_validation error')

            def post_validation(self, config, key_name):
                raise base.ValidationError('post_validation error')

        c = base.Config(schema=(('invalid_option', InvalidConfigOption()),))

        errors, warnings = c.validate()

        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0][0], 'invalid_option')
        self.assertEqual(str(errors[0][1]), 'run_validation error')
        self.assertTrue(isinstance(errors[0][1], base.ValidationError))
        self.assertEqual(len(warnings), 0)

    def test_validation_warnings(self):
        class InvalidConfigOption(BaseConfigOption):
            def pre_validation(self, config, key_name):
                self.warnings.append('pre_validation warning')

            def run_validation(self, value):
                self.warnings.append('run_validation warning')

            def post_validation(self, config, key_name):
                self.warnings.append('post_validation warning')

        c = base.Config(schema=(('invalid_option', InvalidConfigOption()),))

        errors, warnings = c.validate()

        self.assertEqual(len(errors), 0)
        self.assertEqual(
            warnings,
            [
                ('invalid_option', 'pre_validation warning'),
                ('invalid_option', 'run_validation warning'),
                ('invalid_option', 'post_validation warning'),
            ],
        )

    @tempdir()
    def test_load_from_file_with_relative_paths(self, config_dir):
        """
        When explicitly setting a config file, paths should be relative to the
        config file, not the working directory.
        """
        config_fname = os.path.join(config_dir, 'mkdocs.yml')
        with open(config_fname, 'w') as config_file:
            config_file.write("docs_dir: src\nsite_name: MkDocs Test\n")
        docs_dir = os.path.join(config_dir, 'src')
        os.mkdir(docs_dir)

        cfg = base.load_config(config_file=config_file)
        self.assertTrue(isinstance(cfg, base.Config))
        self.assertEqual(cfg['site_name'], 'MkDocs Test')
        self.assertEqual(cfg['docs_dir'], docs_dir)
        self.assertEqual(cfg.config_file_path, config_fname)
        self.assertIsInstance(cfg.config_file_path, str)

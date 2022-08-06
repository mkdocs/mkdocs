import os
import tempfile
import unittest
from tempfile import TemporaryDirectory

from mkdocs import exceptions
from mkdocs.config import base, defaults
from mkdocs.config.config_options import BaseConfigOption


class ConfigBaseTests(unittest.TestCase):

    def test_unrecognised_keys(self):

        c = base.Config(schema=defaults.get_schema())
        c.load_dict({
            'not_a_valid_config_option': "test"
        })

        failed, warnings = c.validate()

        self.assertEqual(warnings, [
            ('not_a_valid_config_option',
                'Unrecognised configuration name: not_a_valid_config_option')
        ])

    def test_missing_required(self):

        c = base.Config(schema=defaults.get_schema())

        errors, warnings = c.validate()

        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0][0], 'site_name')
        self.assertEqual(str(errors[0][1]), 'Required configuration not provided.')

        self.assertEqual(len(warnings), 0)

    def test_load_from_file(self):
        """
        Users can explicitly set the config file using the '--config' option.
        Allows users to specify a config other than the default `mkdocs.yml`.
        """

        temp_dir = TemporaryDirectory()
        config_file = open(os.path.join(temp_dir.name, 'mkdocs.yml'), 'w')
        os.mkdir(os.path.join(temp_dir.name, 'docs'))
        try:
            config_file.write("site_name: MkDocs Test\n")
            config_file.flush()
            config_file.close()

            cfg = base.load_config(config_file=config_file.name)
            self.assertTrue(isinstance(cfg, base.Config))
            self.assertEqual(cfg['site_name'], 'MkDocs Test')
        finally:
            temp_dir.cleanup()

    def test_load_default_file(self):
        """
        test that `mkdocs.yml` will be loaded when '--config' is not set.
        """

        temp_dir = TemporaryDirectory()
        config_file = open(os.path.join(temp_dir.name, 'mkdocs.yml'), 'w')
        os.mkdir(os.path.join(temp_dir.name, 'docs'))
        old_dir = os.getcwd()
        try:
            os.chdir(temp_dir.name)
            config_file.write("site_name: MkDocs Test\n")
            config_file.flush()
            config_file.close()

            cfg = base.load_config(config_file=None)
            self.assertTrue(isinstance(cfg, base.Config))
            self.assertEqual(cfg['site_name'], 'MkDocs Test')
        finally:
            os.chdir(old_dir)
            temp_dir.cleanup()

    def test_load_default_file_with_yaml(self):
        """
        test that `mkdocs.yml` will be loaded when '--config' is not set.
        """

        temp_dir = TemporaryDirectory()
        config_file = open(os.path.join(temp_dir.name, 'mkdocs.yaml'), 'w')
        os.mkdir(os.path.join(temp_dir.name, 'docs'))
        old_dir = os.getcwd()
        try:
            os.chdir(temp_dir.name)
            config_file.write("site_name: MkDocs Test\n")
            config_file.flush()
            config_file.close()

            cfg = base.load_config(config_file=None)
            self.assertTrue(isinstance(cfg, base.Config))
            self.assertEqual(cfg['site_name'], 'MkDocs Test')
        finally:
            os.chdir(old_dir)
            temp_dir.cleanup()

    def test_load_default_file_prefer_yml(self):
        """
        test that `mkdocs.yml` will be loaded when '--config' is not set.
        """

        temp_dir = TemporaryDirectory()
        config_file1 = open(os.path.join(temp_dir.name, 'mkdocs.yml'), 'w')
        config_file2 = open(os.path.join(temp_dir.name, 'mkdocs.yaml'), 'w')
        os.mkdir(os.path.join(temp_dir.name, 'docs'))
        old_dir = os.getcwd()
        try:
            os.chdir(temp_dir.name)
            config_file1.write("site_name: MkDocs Test1\n")
            config_file1.flush()
            config_file1.close()
            config_file2.write("site_name: MkDocs Test2\n")
            config_file2.flush()
            config_file2.close()

            cfg = base.load_config(config_file=None)
            self.assertTrue(isinstance(cfg, base.Config))
            self.assertEqual(cfg['site_name'], 'MkDocs Test1')
        finally:
            os.chdir(old_dir)
            temp_dir.cleanup()

    def test_load_from_missing_file(self):

        with self.assertRaises(exceptions.ConfigurationError):
            base.load_config(config_file='missing_file.yml')

    def test_load_from_open_file(self):
        """
        `load_config` can accept an open file descriptor.
        """

        temp_dir = TemporaryDirectory()
        temp_path = temp_dir.name
        config_fname = os.path.join(temp_path, 'mkdocs.yml')

        config_file = open(config_fname, 'w+')
        os.mkdir(os.path.join(temp_path, 'docs'))
        try:
            config_file.write("site_name: MkDocs Test\n")
            config_file.flush()

            cfg = base.load_config(config_file=config_file)
            self.assertTrue(isinstance(cfg, base.Config))
            self.assertEqual(cfg['site_name'], 'MkDocs Test')
            # load_config will always close the file
            self.assertTrue(config_file.closed)
        finally:
            temp_dir.cleanup()

    def test_load_from_closed_file(self):
        """
        The `serve` command with auto-reload may pass in a closed file descriptor.
        Ensure `load_config` reloads the closed file.
        """

        temp_dir = TemporaryDirectory()
        config_file = open(os.path.join(temp_dir.name, 'mkdocs.yml'), 'w')
        os.mkdir(os.path.join(temp_dir.name, 'docs'))

        try:
            config_file.write("site_name: MkDocs Test\n")
            config_file.flush()
            config_file.close()

            cfg = base.load_config(config_file=config_file)
            self.assertTrue(isinstance(cfg, base.Config))
            self.assertEqual(cfg['site_name'], 'MkDocs Test')
        finally:
            temp_dir.cleanup()

    def test_load_from_deleted_file(self):
        """
        Deleting the config file could trigger a server reload.
        """

        config_file = tempfile.NamedTemporaryFile('w', delete=False)
        try:
            config_file.write("site_name: MkDocs Test\n")
            config_file.flush()
            config_file.close()
        finally:
            os.remove(config_file.name)
        with self.assertRaises(exceptions.ConfigurationError):
            base.load_config(config_file=config_file)

    def test_load_missing_required(self):
        """
        `site_name` is a required setting.
        """

        config_file = tempfile.NamedTemporaryFile('w', delete=False)
        try:
            config_file.write(
                "site_dir: output\nsite_uri: https://www.mkdocs.org\n")
            config_file.flush()
            config_file.close()

            with self.assertRaises(exceptions.Abort):
                base.load_config(config_file=config_file.name)
        finally:
            os.remove(config_file.name)

    def test_pre_validation_error(self):
        class InvalidConfigOption(BaseConfigOption):
            def pre_validation(self, config, key_name):
                raise base.ValidationError('pre_validation error')

        c = base.Config(schema=(('invalid_option', InvalidConfigOption()), ))

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

        c = base.Config(schema=(('invalid_option', InvalidConfigOption()), ))

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

        c = base.Config(schema=(('invalid_option', InvalidConfigOption()), ))

        errors, warnings = c.validate()

        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0][0], 'invalid_option')
        self.assertEqual(str(errors[0][1]), 'post_validation error')
        self.assertTrue(isinstance(errors[0][1], base.ValidationError))
        self.assertEqual(len(warnings), 0)

    def test_pre_and_run_validation_errors(self):
        """ A pre_validation error does not stop run_validation from running. """
        class InvalidConfigOption(BaseConfigOption):
            def pre_validation(self, config, key_name):
                raise base.ValidationError('pre_validation error')

            def run_validation(self, value):
                raise base.ValidationError('run_validation error')

        c = base.Config(schema=(('invalid_option', InvalidConfigOption()), ))

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
        """ A run_validation error stops post_validation from running. """
        class InvalidConfigOption(BaseConfigOption):
            def run_validation(self, value):
                raise base.ValidationError('run_validation error')

            def post_validation(self, config, key_name):
                raise base.ValidationError('post_validation error')

        c = base.Config(schema=(('invalid_option', InvalidConfigOption()), ))

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

        c = base.Config(schema=(('invalid_option', InvalidConfigOption()), ))

        errors, warnings = c.validate()

        self.assertEqual(len(errors), 0)
        self.assertEqual(warnings, [
            ('invalid_option', 'pre_validation warning'),
            ('invalid_option', 'run_validation warning'),
            ('invalid_option', 'post_validation warning'),
        ])

    def test_load_from_file_with_relative_paths(self):
        """
        When explicitly setting a config file, paths should be relative to the
        config file, not the working directory.
        """

        config_dir = TemporaryDirectory()
        config_fname = os.path.join(config_dir.name, 'mkdocs.yml')
        docs_dir = os.path.join(config_dir.name, 'src')
        os.mkdir(docs_dir)

        config_file = open(config_fname, 'w')

        try:
            config_file.write("docs_dir: src\nsite_name: MkDocs Test\n")
            config_file.flush()
            config_file.close()

            cfg = base.load_config(config_file=config_file)
            self.assertTrue(isinstance(cfg, base.Config))
            self.assertEqual(cfg['site_name'], 'MkDocs Test')
            self.assertEqual(cfg['docs_dir'], docs_dir)
            self.assertEqual(cfg.config_file_path, config_fname)
            self.assertIsInstance(cfg.config_file_path, str)
        finally:
            config_dir.cleanup()

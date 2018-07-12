from __future__ import unicode_literals
import logging
import os
import sys
from yaml import YAMLError

from mkdocs import exceptions
from mkdocs import utils


log = logging.getLogger('mkdocs.config')


class ValidationError(Exception):
    """Raised during the validation process of the config on errors."""


class Config(utils.UserDict):
    """
    MkDocs Configuration dict

    This is a fairly simple extension of a standard dictionary. It adds methods
    for running validation on the structure and contents.
    """

    def __init__(self, schema, config_file_path=None):
        """
        The schema is a Python dict which maps the config name to a validator.
        """

        self._schema = schema
        self._schema_keys = set(dict(schema).keys())
        # Ensure config_file_path is a Unicode string
        if config_file_path is not None and not isinstance(config_file_path, utils.text_type):
            try:
                # Assume config_file_path is encoded with the file system encoding.
                config_file_path = config_file_path.decode(encoding=sys.getfilesystemencoding())
            except UnicodeDecodeError:
                raise ValidationError("config_file_path is not a Unicode string.")
        self.config_file_path = config_file_path
        self.data = {}

        self.user_configs = []
        self.set_defaults()

    def set_defaults(self):
        """
        Set the base config by going through each validator and getting the
        default if it has one.
        """

        for key, config_option in self._schema:
            self[key] = config_option.default

    def _validate(self):

        failed, warnings = [], []

        for key, config_option in self._schema:
            try:
                value = self.get(key)
                self[key] = config_option.validate(value)
                warnings.extend([(key, w) for w in config_option.warnings])
                config_option.reset_warnings()
            except ValidationError as e:
                failed.append((key, e))

        for key in (set(self.keys()) - self._schema_keys):
            warnings.append((
                key, "Unrecognised configuration name: {0}".format(key)
            ))

        return failed, warnings

    def _pre_validate(self):

        failed, warnings = [], []

        for key, config_option in self._schema:
            try:
                config_option.pre_validation(self, key_name=key)
                warnings.extend([(key, w) for w in config_option.warnings])
                config_option.reset_warnings()
            except ValidationError as e:
                failed.append((key, e))

        return failed, warnings

    def _post_validate(self):

        failed, warnings = [], []

        for key, config_option in self._schema:
            try:
                config_option.post_validation(self, key_name=key)
                warnings.extend([(key, w) for w in config_option.warnings])
                config_option.reset_warnings()
            except ValidationError as e:
                failed.append((key, e))

        return failed, warnings

    def validate(self):

        failed, warnings = self._pre_validate()

        run_failed, run_warnings = self._validate()

        failed.extend(run_failed)
        warnings.extend(run_warnings)

        # Only run the post validation steps if there are no failures, warnings
        # are okay.
        if len(failed) == 0:
            post_failed, post_warnings = self._post_validate()
            failed.extend(post_failed)
            warnings.extend(post_warnings)

        return failed, warnings

    def load_dict(self, patch):

        if not isinstance(patch, dict):
            raise exceptions.ConfigurationError(
                "The configuration is invalid. The expected type was a key "
                "value mapping (a python dict) but we got an object of type: "
                "{0}".format(type(patch)))

        self.user_configs.append(patch)
        self.data.update(patch)

    def load_file(self, config_file):
        try:
            return self.load_dict(utils.yaml_load(config_file))
        except YAMLError as e:
            # MkDocs knows and understands ConfigurationErrors
            raise exceptions.ConfigurationError(
                "MkDocs encountered as error parsing the configuration file: {}".format(e)
            )


def _open_config_file(config_file):

    # Default to the standard config filename.
    if config_file is None:
        config_file = os.path.abspath('mkdocs.yml')

    # If closed file descriptor, get file path to reopen later.
    if hasattr(config_file, 'closed') and config_file.closed:
        config_file = config_file.name

    log.debug("Loading configuration file: {0}".format(config_file))

    # If it is a string, we can assume it is a path and attempt to open it.
    if isinstance(config_file, utils.string_types):
        if os.path.exists(config_file):
            config_file = open(config_file, 'rb')
        else:
            raise exceptions.ConfigurationError(
                "Config file '{0}' does not exist.".format(config_file))

    # Ensure file descriptor is at begining
    config_file.seek(0)

    return config_file


def load_config(config_file=None, **kwargs):
    """
    Load the configuration for a given file object or name

    The config_file can either be a file object, string or None. If it is None
    the default `mkdocs.yml` filename will loaded.

    Extra kwargs are passed to the configuration to replace any default values
    unless they themselves are None.
    """
    options = kwargs.copy()

    # Filter None values from the options. This usually happens with optional
    # parameters from Click.
    for key, value in options.copy().items():
        if value is None:
            options.pop(key)

    config_file = _open_config_file(config_file)
    options['config_file_path'] = getattr(config_file, 'name', '')

    # Initialise the config with the default schema .
    from mkdocs import config
    cfg = Config(schema=config.DEFAULT_SCHEMA, config_file_path=options['config_file_path'])
    # First load the config file
    cfg.load_file(config_file)
    # Then load the options to overwrite anything in the config.
    cfg.load_dict(options)

    errors, warnings = cfg.validate()

    for config_name, warning in warnings:
        log.warning("Config value: '%s'. Warning: %s", config_name, warning)

    for config_name, error in errors:
        log.error("Config value: '%s'. Error: %s", config_name, error)

    for key, value in cfg.items():
        log.debug("Config value: '%s' = %r", key, value)

    if len(errors) > 0:
        raise exceptions.ConfigurationError(
            "Aborted with {0} Configuration Errors!".format(len(errors))
        )
    elif cfg['strict'] and len(warnings) > 0:
        raise exceptions.ConfigurationError(
            "Aborted with {0} Configuration Warnings in 'strict' mode!".format(len(warnings))
        )

    return cfg

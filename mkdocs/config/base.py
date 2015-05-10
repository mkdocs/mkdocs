import six
import logging
import os

from mkdocs import exceptions
from mkdocs import utils
from mkdocs.config import config_options, defaults

log = logging.getLogger('mkdocs.config')


class Config(six.moves.UserDict):
    """
    MkDocs Configuration dict

    This is a fairly simple extension of a standard dictionary. It adds methods
    for running validation on the structure and contents.
    """

    def __init__(self, schema):
        """
        The schema is a Python dict which maps the config name to a validator.
        """

        self._schema = schema
        self._schema_keys = set(dict(schema).keys())
        self.data = {}

        self.set_defaults()
        self.user_configs = []

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
                warnings.extend(config_option.warnings)
            except config_options.ValidationError as e:
                failed.append((key, str(e)))

        for key in (set(self.keys()) - self._schema_keys):
            warnings.append((
                key, "Unrecognised configuration name: {0}".format(key)
            ))

        return failed, warnings

    def _post_validate(self):

        for key, config_option in self._schema:
            config_option.post_validation(self, key_name=key)

    def validate(self):

        failed, warnings = self._validate()

        self._post_validate()

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
        return self.load_dict(utils.yaml_load(config_file))


def _open_config_file(config_file):

    # Default to the standard config filename.
    if config_file is None:
        config_file = os.path.abspath('mkdocs.yml')

    log.debug("Loading configuration file: %s", config_file)

    # If it is a string, we can assume it is a path and attempt to open it.
    if isinstance(config_file, six.string_types):
        if os.path.exists(config_file):
            config_file = open(config_file, 'rb')
        else:
            raise exceptions.ConfigurationError(
                "Config file '{0}' does not exist.".format(config_file))

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
    config = Config(schema=defaults.DEFAULT_SCHEMA)
    # First load the config file
    config.load_file(config_file)
    # Then load the options to overwrite anything in the config.
    config.load_dict(options)

    errors, warnings = config.validate()

    if len(warnings) > 0:
        for config_name, warning in warnings:
            log.warning("Config value: %s. Warning: %s", config_name, warning)
        if config['strict']:
            raise exceptions.ConfigurationError(
                "Warnings found in the config file")

    if len(errors) > 0:
        for config_name, error in errors:
            log.error("Config value: %s. Error: %s", config_name, error)
        raise exceptions.ConfigurationError("Errors found in the config file.")

    for key, value in config.items():

        log.debug("Config value: %s = %r", key, value)

    return config

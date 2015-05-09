import six
import logging
import os

from mkdocs import exceptions
from mkdocs import utils
from mkdocs.config import config_options, defaults

log = logging.getLogger(__name__)


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
        self.data = {}

        self.set_defaults()
        self.user_configs = []

    def set_defaults(self):
        """
        Set the base config by going through each validator and getting the
        default if it has one.
        """

        for key, config_option in self._schema.items():
            self[key] = config_option.default

    def _validate(self):

        failed, warnings = [], []

        for key, config_option in self._schema.items():
            try:
                value = self.get(key)
                self[key] = config_option.validate(value)
                warnings.extend(config_option.warnings)
            except config_options.ValidationError as e:
                failed.append((key, str(e)))

        for key in (set(self.keys()) - set(self._schema.keys())):
            warnings.append((
                key, "Unrecognised configuration name: {0}".format(key)
            ))

        return failed, warnings

    def _post_validate(self):

        for key in self._schema.keys():
            config_option = self._schema[key]
            config_option.post_validation(self, key_name=key)

    def validate(self):

        failed, warnings = self._validate()

        self._post_validate()

        return failed, warnings

    def update(self, patch):

        if not isinstance(patch, dict):
            raise exceptions.ConfigurationError(
                "The configuration is invalid. The expected type was a key "
                "value mapping (a python dict) but we got an object of type: "
                "{0}".format(type(patch)))

        self.user_configs.append(patch)
        self.data.update(patch)

    def load_file(self, config_file):
        return self.update(utils.yaml_load(config_file))

    def load_dict(self, data):
        return self.update(data)


def _open_config_file(config_file):

    # Default to the standard config filename.
    if config_file is None:
        config_file = 'mkdocs.yml'

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

    options['config'] = config_file = _open_config_file(config_file)

    # Initialise the config with the default schema .
    config = Config(schema=defaults.DEFAULT_CONFIG)
    # First load the config file
    config.load_file(config_file)
    # Then load the options to overwrite anything in the config.
    config.load_dict(options)

    errors, warnings = config.validate()

    for config_name, warning in warnings:
        log.warning("%s - %s", config_name, warning)

    if len(errors) > 0:
        for config_name, error in errors:
            log.error("%s - %s", config_name, error)
        raise exceptions.ConfigurationError("Errors found in the config file.")

    return config

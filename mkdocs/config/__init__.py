import logging
import os

import six

from mkdocs import exceptions
from mkdocs.config import base, defaults

log = logging.getLogger(__name__)


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
    config = base.Config(schema=defaults.DEFAULT_CONFIG)
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

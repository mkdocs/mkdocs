import logging
import os
import sys
from yaml import YAMLError
from collections import UserDict
from contextlib import contextmanager

from mkdocs import exceptions
from mkdocs import utils


log = logging.getLogger('mkdocs.config')


class ValidationError(Exception):
    """Raised during the validation process of the config on errors."""


class Config(UserDict):
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
        if config_file_path is not None and not isinstance(config_file_path, str):
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
                key, f"Unrecognised configuration name: {key}"
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
        """ Load config options from a dictionary. """

        if not isinstance(patch, dict):
            raise exceptions.ConfigurationError(
                "The configuration is invalid. The expected type was a key "
                "value mapping (a python dict) but we got an object of type: "
                f"{type(patch)}")

        self.user_configs.append(patch)
        self.data.update(patch)

    def load_file(self, config_file):
        """ Load config options from the open file descriptor of a YAML file. """
        try:
            return self.load_dict(utils.yaml_load(config_file))
        except YAMLError as e:
            # MkDocs knows and understands ConfigurationErrors
            raise exceptions.ConfigurationError(
                f"MkDocs encountered an error parsing the configuration file: {e}"
            )


@contextmanager
def _open_config_file(config_file):
    """
    A context manager which yields an open file descriptor ready to be read.

    Accepts a filename as a string, an open or closed file descriptor, or None.
    When None, it defaults to `mkdocs.yml` in the CWD. If a closed file descriptor
    is received, a new file descriptor is opened for the same file.

    The file descriptor is automatically closed when the context manager block is existed.
    """

    # Default to the standard config filename.
    if config_file is None:
        paths_to_try = ['mkdocs.yml', 'mkdocs.yaml']
    # If it is a string, we can assume it is a path and attempt to open it.
    elif isinstance(config_file, str):
        paths_to_try = [config_file]
    # If closed file descriptor, get file path to reopen later.
    elif getattr(config_file, 'closed', False):
        paths_to_try = [config_file.name]
    else:
        paths_to_try = None

    if paths_to_try:
        # config_file is not a file descriptor, so open it as a path.
        for path in paths_to_try:
            path = os.path.abspath(path)
            log.debug(f"Loading configuration file: {path}")
            try:
                config_file = open(path, 'rb')
                break
            except FileNotFoundError:
                continue
        else:
            raise exceptions.ConfigurationError(
                f"Config file '{paths_to_try[0]}' does not exist.")
    else:
        log.debug(f"Loading configuration file: {config_file}")
        # Ensure file descriptor is at beginning
        config_file.seek(0)

    try:
        yield config_file
    finally:
        if hasattr(config_file, 'close'):
            config_file.close()


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

    with _open_config_file(config_file) as fd:
        options['config_file_path'] = getattr(fd, 'name', '')

        # Initialize the config with the default schema.
        from mkdocs.config.defaults import get_schema
        cfg = Config(schema=get_schema(), config_file_path=options['config_file_path'])
        # load the config file
        cfg.load_file(fd)

    # Then load the options to overwrite anything in the config.
    cfg.load_dict(options)

    errors, warnings = cfg.validate()

    for config_name, warning in warnings:
        log.warning(f"Config value: '{config_name}'. Warning: {warning}")

    for config_name, error in errors:
        log.error(f"Config value: '{config_name}'. Error: {error}")

    for key, value in cfg.items():
        log.debug(f"Config value: '{key}' = {value!r}")

    if len(errors) > 0:
        raise exceptions.Abort(
            f"Aborted with {len(errors)} Configuration Errors!"
        )
    elif cfg['strict'] and len(warnings) > 0:
        raise exceptions.Abort(
            f"Aborted with {len(warnings)} Configuration Warnings in 'strict' mode!"
        )

    return cfg

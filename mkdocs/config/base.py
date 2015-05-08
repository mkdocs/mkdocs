import six

from mkdocs import exceptions
from mkdocs import utils
from mkdocs.config import config_options


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
            raise exceptions.ConfigurationError("Invalid config.")

        self.user_configs.append(patch)
        self.data.update(patch)

    def load_file(self, config_file):
        return self.update(utils.yaml_load(config_file))

    def load_dict(self, data):
        return self.update(data)

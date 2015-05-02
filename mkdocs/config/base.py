import os

import six

from mkdocs import exceptions
from mkdocs import utils
from mkdocs.config import validators


class Config(six.moves.UserDict):

    def __init__(self, schema):

        self._schema = schema
        self.data = {}

    def validate_update(self, update):

        if update is None:
            update = self

        failed = []

        for key, value in update.items():

            if key not in self._schema:
                failed.append((key, "Unrecognised configuration name."))
                continue

            validator = self._schema[key]

            try:
                value = validator.check(update, value)
            except validators.ValidationError as e:
                failed.append((key, str(e)))

        return failed

    def validate(self):

        failed = self.validate_update(self)

        for key in set(self._schema.keys()) - set(self.keys()):
            validator = self._schema[key]
            if validator.is_required():
                failed.append((key, "Required configuration not provided."))
            else:
                self[key] = validator.default

        for key in self._schema.keys():
            validator = self._schema[key]
            validator.post_process(self, key_name=key)

        return failed

    def _patch(self, patch):
        self.data.update(patch)

    def load_file(self, config_file):
        return self._patch(utils.yaml_load(config_file))

    def load_path(self, path):

        if not os.path.exists(path):
            raise exceptions.ConfigurationError("Bad path.")

        config_file = open(path, 'rb')

        return self.load_file(config_file)

    def load_dict(self, data):
        return self._patch(data)

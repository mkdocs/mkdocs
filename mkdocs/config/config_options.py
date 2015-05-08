import os

import six

from mkdocs import utils, legacy
from mkdocs.legacy import OrderedDict


class ValidationError(Exception):
    """Raised during the validation process of the config on errors."""


class BaseConfigOption(object):
    """
    The BaseConfigOption adds support for default values and required values

    It then delegates the validation and (optional) post processing to
    subclasses.
    """

    def __init__(self, default=None, required=False):
        self.default = default
        self.required = required
        self.warnings = []

    def is_required(self):
        return self.required

    def validate(self, value):
        """
        Perform some initial validation.

        If the option is empty (None) and isn't required, leave it as such. If
        it is empty but has a default, use that. Finally, call the
        run_validatuon method on the subclass unless.
        """

        if value is None:
            if self.default is not None:
                value = self.default
            elif not self.required:
                return
            elif self.required:
                raise ValidationError("Required configuration not provided.")

        return self.run_validatuon(value)

    def run_validatuon(self, value):
        """
        Perform validation for a value.

        The run_validatuon method should be implemented by subclasses.
        """
        return value

    def post_process(self, config, key_name):
        """
        After all options have passed validation, perform a post process to
        do any additional changes dependant on other config values.

        The post process method should be implemented by subclasses.
        """


class Type(BaseConfigOption):
    """
    Type Config Option

    Validate the type of a config option against a given Python type.
    """

    def __init__(self, type_, length=None, **kwargs):
        super(Type, self).__init__(**kwargs)
        self._type = type_
        self.length = length

    def run_validatuon(self, value):

        if not isinstance(value, self._type):
            msg = ("Expected type: {0} but recieved: {1}"
                   .format(self._type, type(value)))
        elif self.length is not None and len(value) != self.length:
            msg = ("Expected type: {0} with lenght {2} but recieved: {1} with "
                   "length {3}").format(self._type, value, self.length,
                                        len(value))
        else:
            return value

        raise ValidationError(msg)


class URL(BaseConfigOption):
    """
    URL Config Option

    Validate a URL by requiring a scheme is present.
    """

    def run_validatuon(self, value):

        parsed_url = six.moves.urllib.parse.urlparse(value)

        if parsed_url.scheme:
            return value

        raise ValidationError("Invalid URL.")


class RepoURL(URL):
    """
    Repo URL Config Option

    A small extension to the URL config that sets the repo_name, based on the
    url if it hasn't already been provided.
    """

    def post_process(self, config, key_name):

        if config['repo_url'] is not None and config.get('repo_name') is None:
            repo_host = six.moves.urllib.parse.urlparse(
                config['repo_url']).netloc.lower()
            if repo_host == 'github.com':
                config['repo_name'] = 'GitHub'
            elif repo_host == 'bitbucket.org':
                config['repo_name'] = 'Bitbucket'
            else:
                config['repo_name'] = repo_host.split('.')[0].title()


class Dir(BaseConfigOption):
    """
    Dir Config Option

    Validate a path to a directory, optionally verifying that it exists.
    """

    def __init__(self, exists=False, **kwargs):
        super(Dir, self).__init__(**kwargs)
        self.exists = exists

    def run_validatuon(self, value):

        if self.exists and not os.path.isdir(value):
            raise ValidationError("The path {0} doesn't exist".format(value))

        return value


class SiteDir(Dir):
    """
    SiteDir Config Option

    Validates the site_dir and docs_dir directories do not contain each other.
    """

    def post_process(self, config, key_name):

        # Validate that the docs_dir and site_dir don't contain the
        # other as this will lead to copying back and forth on each
        # and eventually make a deep nested mess.
        abs_site_dir = os.path.abspath(config['site_dir'])
        abs_docs_dir = os.path.abspath(config['docs_dir'])
        if abs_docs_dir.startswith(abs_site_dir):
            raise ValidationError(
                "The 'docs_dir' can't be within the 'site_dir'.")
        elif abs_site_dir.startswith(abs_docs_dir):
            raise ValidationError(
                "The 'site_dir' can't be within the 'docs_dir'.")


class ThemeDir(Dir):
    """
    ThemeDir Config Option

    Post process the theme_dir to do some path munging.

    TODO: This could probably be improved and/or moved from here. It's a tad
    gross really.
    """

    def post_process(self, config, key_name):

        theme_in_config = any(['theme' in c for c in config.user_configs])

        package_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..'))
        theme_dir = [os.path.join(package_dir, 'themes', config['theme']), ]
        config['mkdocs_templates'] = os.path.join(package_dir, 'templates')

        if config['theme_dir'] is not None:
            # If the user has given us a custom theme but not a
            # builtin theme name then we don't want to merge them.
            if not theme_in_config:
                theme_dir = []
            theme_dir.insert(0, config['theme_dir'])

        config['theme_dir'] = theme_dir

        # Add the search assets to the theme_dir, this means that
        # they will then we copied into the output directory but can
        # be overwritten by themes if needed.
        search_assets = os.path.join(package_dir, 'assets', 'search')
        config['theme_dir'].append(search_assets)


class Theme(BaseConfigOption):
    """
    Theme Config Option

    Validate that the theme is one of the builtin Mkdocs theme names.
    """

    def run_validatuon(self, value):

        themes = utils.get_theme_names()

        if value in themes:
            return value

        raise ValidationError("Unrecognised theme.")


class Extras(BaseConfigOption):
    """
    Extras Config Option

    Validate the extra configs are a list and populate them with a set of files
    if not provided.
    """

    def __init__(self, file_match, **kwargs):
        super(Extras, self).__init__(**kwargs)
        self.file_match = file_match

    def run_validatuon(self, value):

        if isinstance(value, list):
            return value
        else:
            raise ValidationError(
                "Expected a list, got {0}".format(type(value)))

    def walk_docs_dir(self, docs_dir):
        for (dirpath, _, filenames) in os.walk(docs_dir):
            for filename in sorted(filenames):
                fullpath = os.path.join(dirpath, filename)
                relpath = os.path.normpath(os.path.relpath(fullpath, docs_dir))
                if self.file_match(relpath):
                    yield relpath

    def post_process(self, config, key_name):

        if config[key_name] is not None:
            return

        extras = []

        for filename in self.walk_docs_dir(config['docs_dir']):
            extras.append(filename)

        config[key_name] = extras


class Pages(Extras):
    """
    Pages Config Option

    Validate the pages config, performing comparability if the config appears
    to be the old structure. Automatically add all markdown files if none are
    provided.
    """

    def __init__(self, **kwargs):
        super(Pages, self).__init__(utils.is_markdown_file, **kwargs)

    def run_validatuon(self, value):

        if not isinstance(value, list):
            raise ValidationError(
                "Expected a list, got {0}".format(type(value)))

        if len(value) == 0:
            return

        # TODO: Remove in 1.0
        config_types = set(type(l) for l in value)

        if config_types.issubset(set([str, OrderedDict, ])):
            return value

        if config_types.issubset(set([str, list, ])):
            return legacy.pages_compat_shim(value)

        raise ValidationError("Invalid pages config.")

    def post_process(self, config, key_name):

        if config[key_name] is not None:
            return

        pages = []

        for filename in self.walk_docs_dir(config['docs_dir']):

            if os.path.splitext(filename)[0] == 'index':
                pages.insert(0, filename)
            else:
                pages.append(filename)

        config[key_name] = utils.nest_paths(pages)


class NumPages(BaseConfigOption):
    """
    NumPages Config Option

    Set the value to True if the number of pages is greater than the given
    number (defaults to 1).
    """

    def __init__(self, at_lest=1, **kwargs):
        super(NumPages, self).__init__(**kwargs)
        self.at_lest = at_lest

    def post_process(self, config, key_name):

        if config[key_name] is not None:
            return

        try:
            config[key_name] = len(config['pages']) > self.at_lest
        except TypeError:
            config[key_name] = False

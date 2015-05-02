import os

from six.moves.urllib import parse

from mkdocs import utils


class ValidationError(Exception):
    pass


class BaseValidator(object):

    def __init__(self, default=None, required=False):
        self.default = default
        self.required = required

    def is_required(self):
        return self.required

    def check(self, data_dict, value):

        if value is None:
            if self.default is not None:
                value = self.default
            elif not self.required:
                return
            elif self.required:
                raise ValidationError("Required parameter not provided.")

        return self._check(data_dict, value)

    def post_process(self, config, key_name):
        pass


class Type(BaseValidator):

    def __init__(self, type_, length=None, **kwargs):
        super(Type, self).__init__(**kwargs)
        self._type = type_
        self.length = length

    def _check(self, data_dict, value):

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


class URL(BaseValidator):

    def _check(self, data_dict, value):

        parsed_url = parse.urlparse(value)

        if parsed_url.scheme:
            return value

        raise ValidationError("Invalid URL.")


class RepoURL(URL):

    def _check(self, data_dict, value):

        parsed_url = parse.urlparse(value)

        if parsed_url.scheme:
            return value

        raise ValidationError("Invalid URL.")

    def post_process(self, config, key_name):

        if config['repo_url'] is not None and config['repo_name'] is None:
            repo_host = parse.urlparse(config['repo_url']).netloc.lower()
            if repo_host == 'github.com':
                config['repo_name'] = 'GitHub'
            elif repo_host == 'bitbucket.org':
                config['repo_name'] = 'Bitbucket'
            else:
                config['repo_name'] = repo_host.split('.')[0].title()


class Dir(BaseValidator):

    def __init__(self, exists=True, **kwargs):
        super(Dir, self).__init__(**kwargs)
        self.exists = exists

    def _check(self, data_dict, value):

        if self.exists and not os.path.isdir(value):
            raise ValidationError("The path doesn't exist")

        return value


class ThemeDir(Dir):

    def post_process(self, config, key_name):

        package_dir = os.path.join(os.path.dirname(__file__), '..')
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


class Theme(BaseValidator):

    def _check(self, data_dict, value):

        themes = utils.get_theme_names()

        if value in themes:
            return value

        raise ValidationError("Unrecognised theme.")


class Extras(BaseValidator):

    def __init__(self, file_match, **kwargs):
        super(Extras, self).__init__(**kwargs)
        self.file_match = file_match

    def _check(self, data_dict, value):

        if isinstance(value, list):
            return value
        elif value is not None:
            raise ValidationError(
                "Expected a list, got {0}".format(type(value)))

    def walk_docs_dir(self, docs_dir):
        for (dirpath, _, filenames) in os.walk(docs_dir):
            for filename in sorted(filenames):
                fullpath = os.path.join(dirpath, filename)
                relpath = os.path.normpath(os.path.relpath(fullpath, docs_dir))
                yield relpath

    def post_process(self, config, key_name):

        if config[key_name] is not None:
            return

        extras = []

        for filename in self.walk_docs_dir(config['docs_dir']):

            if self.file_match(filename):
                extras.append(filename)

        config[key_name] = extras


class Pages(Extras):

    def __init__(self, **kwargs):
        super(Pages, self).__init__(utils.is_markdown_file, **kwargs)

    def _check(self, data_dict, value):

        if isinstance(value, list):
            return value

        pages = []

        for filename in self.walk_docs_dir(data_dict['docs_dir']):

            if os.path.splitext(filename)[0] == 'index':
                pages.insert(0, filename)
            else:
                pages.append(filename)

        return pages


class NumPages(BaseValidator):

    def __init__(self, at_lest=1, **kwargs):
        super(NumPages, self).__init__(**kwargs)
        self.at_lest = at_lest

    def post_process(self, config, key_name):

        if config[key_name] is not None:
            return

        config[key_name] = len(config['pages']) > self.at_lest

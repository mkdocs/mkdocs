from __future__ import unicode_literals
import os

from mkdocs import utils, legacy
from mkdocs.config.base import Config, ValidationError


class BaseConfigOption(object):

    def __init__(self):
        self.warnings = []
        self.default = None

    def is_required(self):
        return False

    def validate(self, value):
        return self.run_validation(value)

    def reset_warnings(self):
        self.warnings = []

    def pre_validation(self, config, key_name):
        """
        After all options have passed validation, perform a post validation
        process to do any additional changes dependant on other config values.

        The post validation process method should be implemented by subclasses.
        """

    def run_validation(self, value):
        """
        Perform validation for a value.

        The run_validation method should be implemented by subclasses.
        """
        return value

    def post_validation(self, config, key_name):
        """
        After all options have passed validation, perform a post validation
        process to do any additional changes dependant on other config values.

        The post validation process method should be implemented by subclasses.
        """


class SubConfig(BaseConfigOption, Config):
    def __init__(self, *config_options):
        BaseConfigOption.__init__(self)
        Config.__init__(self, config_options)
        self.default = {}

    def validate(self, value):
        self.load_dict(value)
        return self.run_validation(value)

    def run_validation(self, value):
        Config.validate(self)
        return self


class OptionallyRequired(BaseConfigOption):
    """
    The BaseConfigOption adds support for default values and required values

    It then delegates the validation and (optional) post validation processing
    to subclasses.
    """

    def __init__(self, default=None, required=False):
        super(OptionallyRequired, self).__init__()
        self.default = default
        self.required = required

    def is_required(self):
        return self.required

    def validate(self, value):
        """
        Perform some initial validation.

        If the option is empty (None) and isn't required, leave it as such. If
        it is empty but has a default, use that. Finally, call the
        run_validation method on the subclass unless.
        """

        if value is None:
            if self.default is not None:
                value = self.default
            elif not self.required:
                return
            elif self.required:
                raise ValidationError("Required configuration not provided.")

        return self.run_validation(value)


class Type(OptionallyRequired):
    """
    Type Config Option

    Validate the type of a config option against a given Python type.
    """

    def __init__(self, type_, length=None, **kwargs):
        super(Type, self).__init__(**kwargs)
        self._type = type_
        self.length = length

    def run_validation(self, value):

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


class Deprecated(BaseConfigOption):

    def __init__(self, moved_to=None):
        super(Deprecated, self).__init__()
        self.default = None
        self.moved_to = moved_to

    def pre_validation(self, config, key_name):

        if config.get(key_name) is None or self.moved_to is None:
            return

        warning = ('The configuration option {0} has been deprecated and will '
                   'be removed in a future release of MkDocs.')
        self.warnings.append(warning)

        if '.' not in self.moved_to:
            target = config
            target_key = self.moved_to
        else:
            move_to, target_key = self.moved_to.rsplit('.', 1)

            target = config
            for key in move_to.split('.'):
                target = target.setdefault(key, {})

                if not isinstance(target, dict):
                    # We can't move it for the user
                    return

        target[target_key] = config.pop(key_name)


class URL(OptionallyRequired):
    """
    URL Config Option

    Validate a URL by requiring a scheme is present.
    """

    def __init__(self, default='', required=False):
        super(URL, self).__init__(default, required)

    def run_validation(self, value):
        if value == '':
            return value

        try:
            parsed_url = utils.urlparse(value)
        except (AttributeError, TypeError):
            raise ValidationError("Unable to parse the URL.")

        if parsed_url.scheme:
            return value

        raise ValidationError(
            "The URL isn't valid, it should include the http:// (scheme)")


class RepoURL(URL):
    """
    Repo URL Config Option

    A small extension to the URL config that sets the repo_name, based on the
    url if it hasn't already been provided.
    """

    def post_validation(self, config, key_name):

        if config['repo_url'] is not None and config.get('repo_name') is None:
            repo_host = utils.urlparse(
                config['repo_url']).netloc.lower()
            if repo_host == 'github.com':
                config['repo_name'] = 'GitHub'
            elif repo_host == 'bitbucket.org':
                config['repo_name'] = 'Bitbucket'
            else:
                config['repo_name'] = repo_host.split('.')[0].title()

        if config['repo_url'] is not None and config.get('edit_uri') is None:
            if config['repo_name'].lower() == 'github':
                config['edit_uri'] = 'edit/master/docs/'
            elif config['repo_name'].lower() == 'bitbucket':
                config['edit_uri'] = 'src/default/docs/'


class Dir(Type):
    """
    Dir Config Option

    Validate a path to a directory, optionally verifying that it exists.
    """

    def __init__(self, exists=False, **kwargs):
        super(Dir, self).__init__(type_=utils.string_types, **kwargs)
        self.exists = exists

    def run_validation(self, value):

        value = super(Dir, self).run_validation(value)

        if self.exists and not os.path.isdir(value):
            raise ValidationError("The path {0} doesn't exist".format(value))

        return os.path.abspath(value)

    def post_validation(self, config, key_name):

        # Validate that the dir is not the parent dir of the config file.
        if os.path.dirname(config['config_file_path']) == config[key_name]:
            raise ValidationError(
                ("The '{0}' should not be the parent directory of the config "
                 "file. Use a child directory instead so that the config file "
                 "is a sibling of the config file.").format(key_name))


class SiteDir(Dir):
    """
    SiteDir Config Option

    Validates the site_dir and docs_dir directories do not contain each other.
    """

    def post_validation(self, config, key_name):

        super(SiteDir, self).post_validation(config, key_name)

        # Validate that the docs_dir and site_dir don't contain the
        # other as this will lead to copying back and forth on each
        # and eventually make a deep nested mess.
        if (config['docs_dir'] + os.sep).startswith(config['site_dir'] + os.sep):
            raise ValidationError(
                ("The 'docs_dir' should not be within the 'site_dir' as this "
                 "can mean the source files are overwritten by the output or "
                 "it will be deleted if --clean is passed to mkdocs build."
                 "(site_dir: '{0}', docs_dir: '{1}')"
                 ).format(config['site_dir'], config['docs_dir']))
        elif (config['site_dir'] + os.sep).startswith(config['docs_dir'] + os.sep):
            raise ValidationError(
                ("The 'site_dir' should not be within the 'docs_dir' as this "
                 "leads to the build directory being copied into itself and "
                 "duplicate nested files in the 'site_dir'."
                 "(site_dir: '{0}', docs_dir: '{1}')"
                 ).format(config['site_dir'], config['docs_dir']))


class ThemeDir(Dir):
    """
    ThemeDir Config Option

    Post validation, verify the theme_dir and do some path munging.

    TODO: This could probably be improved and/or moved from here. It's a tad
    gross really.
    """

    def post_validation(self, config, key_name):

        theme_in_config = any(['theme' in c for c in config.user_configs])

        package_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..'))
        theme_dir = [utils.get_theme_dir(config['theme']), ]
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


class Theme(OptionallyRequired):
    """
    Theme Config Option

    Validate that the theme is one of the builtin Mkdocs theme names.
    """

    def run_validation(self, value):
        themes = utils.get_theme_names()

        # These themes have been moved to the mkdocs-bootstrap and
        # mkdocs-bootswatch packages. At some point we wont depend on
        # these by default.
        moved_themes = [
            'bootstrap', 'amelia', 'cerulean', 'cosmo', 'cyborg',
            'flatly', 'journal', 'readable', 'simplex', 'slate',
            'spacelab', 'united', 'yeti'
        ]

        if value in themes:
            return value

        elif value in moved_themes:
            raise ValidationError(
                ("The theme '{0}' is no longer included in MkDocs by default "
                 "and must be installed with pip. See http://www.mkdocs.org"
                 "/about/release-notes/#add-support-for-installable-themes"
                 "for more details").format(value)
            )

        raise ValidationError(
            "Unrecognised theme '{0}'. The available installed themes "
            "are: {1}".format(value, ', '.join(themes))
        )


class Extras(OptionallyRequired):
    """
    Extras Config Option

    Validate the extra configs are a list and populate them with a set of files
    if not provided.
    """

    def __init__(self, file_match=None, **kwargs):
        super(Extras, self).__init__(**kwargs)
        self.file_match = file_match

    def run_validation(self, value):

        if isinstance(value, list):
            return value
        else:
            raise ValidationError(
                "Expected a list, got {0}".format(type(value)))

    def walk_docs_dir(self, docs_dir):

        if self.file_match is None:
            raise StopIteration

        for (dirpath, dirs, filenames) in os.walk(docs_dir):
            dirs.sort()
            for filename in sorted(filenames):
                fullpath = os.path.join(dirpath, filename)

                # Some editors (namely Emacs) will create temporary symlinks
                # for internal magic. We can just ignore these files.
                if os.path.islink(fullpath):
                    fp = os.path.join(dirpath, os.readlink(fullpath))
                    if not os.path.exists(fp):
                        continue

                relpath = os.path.normpath(os.path.relpath(fullpath, docs_dir))
                if self.file_match(relpath):
                    yield relpath

    def post_validation(self, config, key_name):

        if config[key_name] is not None:
            return

        extras = []

        for filename in self.walk_docs_dir(config['docs_dir']):
            extras.append(filename)

        config[key_name] = extras

        if not extras:
            return

        self.warnings.append((
            'The following files have been automatically included in the '
            'documentation build and will be added to the HTML: {0}. This '
            'behavior is deprecated. In version 1.0 and later they will '
            "need to be explicitly listed in the '{1}' config setting."
        ).format(','.join(extras), key_name))


class Pages(Extras):
    """
    Pages Config Option

    Validate the pages config, performing comparability if the config appears
    to be the old structure. Automatically add all markdown files if none are
    provided.
    """

    def __init__(self, **kwargs):
        super(Pages, self).__init__(utils.is_markdown_file, **kwargs)

    def run_validation(self, value):

        if not isinstance(value, list):
            raise ValidationError(
                "Expected a list, got {0}".format(type(value)))

        if len(value) == 0:
            return

        # TODO: Remove in 1.0
        config_types = set(type(l) for l in value)

        if config_types.issubset(set([utils.text_type, dict, str])):
            return value

        if config_types.issubset(set([utils.text_type, list, str])):
            return legacy.pages_compat_shim(value)

        raise ValidationError("Invalid pages config. {0} {1}".format(
            config_types,
            set([utils.text_type, dict, ])
        ))

    def post_validation(self, config, key_name):

        if config[key_name] is not None:
            return

        pages = []

        for filename in self.walk_docs_dir(config['docs_dir']):

            if os.path.splitext(filename)[0] == 'index':
                pages.insert(0, filename)
            else:
                pages.append(filename)

        config[key_name] = utils.nest_paths(pages)


class NumPages(OptionallyRequired):
    """
    NumPages Config Option

    Set the value to True if the number of pages is greater than the given
    number (defaults to 1).
    """

    def __init__(self, at_lest=1, **kwargs):
        super(NumPages, self).__init__(**kwargs)
        self.at_lest = at_lest

    def pre_validation(self, config, key_name):
        # TODO: delete deprecated `NumPages` class in version 1.0
        # Numpages is only used by `include_nav` and `include_next_prev`,
        # which are both deprecated, so we can delete the entire Option type.
        if config.get(key_name) is not None:
            # Only issue warning if option is defined by user.
            warning = ('The configuration option {0} has been deprecated and will '
                       'be removed in a future release of MkDocs.').format(key_name)
            self.warnings.append(warning)

    def post_validation(self, config, key_name):

        if config[key_name] is not None:
            return

        try:
            config[key_name] = len(config['pages']) > self.at_lest
        except TypeError:
            config[key_name] = False


class Private(OptionallyRequired):
    """
    Private Config Option

    A config option only for internal use. Raises an error if set by the user.
    """

    def run_validation(self, value):
        raise ValidationError('For internal use only.')


class MarkdownExtensions(OptionallyRequired):
    """
    Markdown Extensions Config Option

    A list of extensions. If a list item contains extension configs,
    those are set on the private  setting passed to `configkey`. The
    `builtins` keyword accepts a list of extensions which cannot be
    overriden by the user. However, builtins can be duplicated to define
    config options for them if desired.
    """
    def __init__(self, builtins=None, configkey='mdx_configs', **kwargs):
        super(MarkdownExtensions, self).__init__(**kwargs)
        self.builtins = builtins or []
        self.configkey = configkey
        self.configdata = {}

    def run_validation(self, value):
        if not isinstance(value, (list, tuple)):
            raise ValidationError('Invalid Markdown Extensions configuration')
        extensions = []
        for item in value:
            if isinstance(item, dict):
                if len(item) > 1:
                    raise ValidationError('Invalid Markdown Extensions configuration')
                ext, cfg = item.popitem()
                extensions.append(ext)
                if cfg is None:
                    continue
                if not isinstance(cfg, dict):
                    raise ValidationError('Invalid config options for Markdown '
                                          "Extension '{0}'.".format(ext))
                self.configdata[ext] = cfg
            elif isinstance(item, utils.string_types):
                extensions.append(item)
            else:
                raise ValidationError('Invalid Markdown Extensions configuration')
        return utils.reduce_list(self.builtins + extensions)

    def post_validation(self, config, key_name):
        config[self.configkey] = self.configdata

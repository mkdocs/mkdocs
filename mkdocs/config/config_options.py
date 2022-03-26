import os
from collections import namedtuple
from collections.abc import Sequence
from urllib.parse import urlsplit, urlunsplit
import ipaddress
import markdown

from mkdocs import utils, theme, plugins
from mkdocs.config.base import Config, ValidationError


class BaseConfigOption:

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
        Before all options are validated, perform a pre-validation process.

        The pre-validation process method should be implemented by subclasses.
        """

    def run_validation(self, value):
        """
        Perform validation for a value.

        The run_validation method should be implemented by subclasses.
        """
        return value

    def post_validation(self, config, key_name):
        """
        After all options have passed validation, perform a post-validation
        process to do any additional changes dependent on other config values.

        The post-validation process method should be implemented by subclasses.
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


class ConfigItems(BaseConfigOption):
    """
    Config Items Option

    Validates a list of mappings that all must match the same set of
    options.
    """
    def __init__(self, *config_options, **kwargs):
        BaseConfigOption.__init__(self)
        self.item_config = SubConfig(*config_options)
        self.required = kwargs.get('required', False)

    def __repr__(self):
        return f'{self.__class__.__name__}: {self.item_config}'

    def run_validation(self, value):
        if value is None:
            if self.required:
                raise ValidationError("Required configuration not provided.")
            else:
                return ()

        if not isinstance(value, Sequence):
            raise ValidationError(f'Expected a sequence of mappings, but a '
                                  f'{type(value)} was given.')

        return [self.item_config.validate(item) for item in value]


class OptionallyRequired(BaseConfigOption):
    """
    A subclass of BaseConfigOption that adds support for default values and
    required values. It is a base class for config options.
    """

    def __init__(self, default=None, required=False):
        super().__init__()
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
                if hasattr(self.default, 'copy'):
                    # ensure no mutable values are assigned
                    value = self.default.copy()
                else:
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
        super().__init__(**kwargs)
        self._type = type_
        self.length = length

    def run_validation(self, value):

        if not isinstance(value, self._type):
            msg = f"Expected type: {self._type} but received: {type(value)}"
        elif self.length is not None and len(value) != self.length:
            msg = (f"Expected type: {self._type} with length {self.length}"
                   f" but received: {value} with length {len(value)}")
        else:
            return value

        raise ValidationError(msg)


class Choice(OptionallyRequired):
    """
    Choice Config Option

    Validate the config option against a strict set of values.
    """

    def __init__(self, choices, **kwargs):
        super().__init__(**kwargs)
        try:
            length = len(choices)
        except TypeError:
            length = 0

        if not length or isinstance(choices, str):
            raise ValueError(f'Expected iterable of choices, got {choices}')

        self.choices = choices

    def run_validation(self, value):
        if value not in self.choices:
            msg = f"Expected one of: {self.choices} but received: {value}"
        else:
            return value

        raise ValidationError(msg)


class Deprecated(BaseConfigOption):
    """
    Deprecated Config Option

    Raises a warning as the option is deprecated. Uses `message` for the
    warning. If `move_to` is set to the name of a new config option, the value
    is moved to the new option on pre_validation. If `option_type` is set to a
    ConfigOption instance, then the value is validated against that type.
    """

    def __init__(self, moved_to=None, message=None, removed=False, option_type=None):
        super().__init__()
        self.default = None
        self.moved_to = moved_to
        if not message:
            if removed:
                message = "The configuration option '{}' was removed from MkDocs."
            else:
                message = (
                    "The configuration option '{}' has been deprecated and "
                    "will be removed in a future release of MkDocs."
                )
            if moved_to:
                message += f" Use '{moved_to}' instead."

        self.message = message
        self.removed = removed
        self.option = option_type or BaseConfigOption()

        self.warnings = self.option.warnings

    def pre_validation(self, config, key_name):
        self.option.pre_validation(config, key_name)

        if config.get(key_name) is not None:
            if self.removed:
                raise ValidationError(self.message.format(key_name))
            self.warnings.append(self.message.format(key_name))

            if self.moved_to is not None:
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

    def validate(self, value):
        return self.option.validate(value)

    def post_validation(self, config, key_name):
        self.option.post_validation(config, key_name)

    def reset_warnings(self):
        self.option.reset_warnings()
        self.warnings = self.option.warnings


class IpAddress(OptionallyRequired):
    """
    IpAddress Config Option

    Validate that an IP address is in an appropriate format
    """

    def run_validation(self, value):
        try:
            host, port = value.rsplit(':', 1)
        except Exception:
            raise ValidationError("Must be a string of format 'IP:PORT'")

        if host != 'localhost':
            try:
                # Validate and normalize IP Address
                host = str(ipaddress.ip_address(host))
            except ValueError as e:
                raise ValidationError(e)

        try:
            port = int(port)
        except Exception:
            raise ValidationError(f"'{port}' is not a valid port")

        class Address(namedtuple('Address', 'host port')):
            def __str__(self):
                return f'{self.host}:{self.port}'

        return Address(host, port)

    def post_validation(self, config, key_name):
        host = config[key_name].host
        if key_name == 'dev_addr' and host in ['0.0.0.0', '::']:
            self.warnings.append(
                (f"The use of the IP address '{host}' suggests a production environment "
                 "or the use of a proxy to connect to the MkDocs server. However, "
                 "the MkDocs' server is intended for local development purposes only. "
                 "Please use a third party production-ready server instead.")
            )


class URL(OptionallyRequired):
    """
    URL Config Option

    Validate a URL by requiring a scheme is present.
    """

    def __init__(self, default='', required=False, is_dir=False):
        self.is_dir = is_dir
        super().__init__(default, required)

    def run_validation(self, value):
        if value == '':
            return value

        try:
            parsed_url = urlsplit(value)
        except (AttributeError, TypeError):
            raise ValidationError("Unable to parse the URL.")

        if parsed_url.scheme and parsed_url.netloc:
            if self.is_dir and not parsed_url.path.endswith('/'):
                parsed_url = parsed_url._replace(path=f'{parsed_url.path}/')
            return urlunsplit(parsed_url)

        raise ValidationError(
            "The URL isn't valid, it should include the http:// (scheme)")


class RepoURL(URL):
    """
    Repo URL Config Option

    A small extension to the URL config that sets the repo_name and edit_uri,
    based on the url if they haven't already been provided.
    """

    def post_validation(self, config, key_name):
        repo_host = urlsplit(config['repo_url']).netloc.lower()
        edit_uri = config.get('edit_uri')

        # derive repo_name from repo_url if unset
        if config['repo_url'] is not None and config.get('repo_name') is None:
            if repo_host == 'github.com':
                config['repo_name'] = 'GitHub'
            elif repo_host == 'bitbucket.org':
                config['repo_name'] = 'Bitbucket'
            elif repo_host == 'gitlab.com':
                config['repo_name'] = 'GitLab'
            else:
                config['repo_name'] = repo_host.split('.')[0].title()

        # derive edit_uri from repo_name if unset
        if config['repo_url'] is not None and edit_uri is None:
            if repo_host == 'github.com' or repo_host == 'gitlab.com':
                edit_uri = 'edit/master/docs/'
            elif repo_host == 'bitbucket.org':
                edit_uri = 'src/default/docs/'
            else:
                edit_uri = ''

        # ensure a well-formed edit_uri
        if edit_uri and not edit_uri.endswith('/'):
            edit_uri += '/'

        config['edit_uri'] = edit_uri


class FilesystemObject(Type):
    """
    Base class for options that point to filesystem objects.
    """

    def __init__(self, exists=False, **kwargs):
        super().__init__(type_=str, **kwargs)
        self.exists = exists
        self.config_dir = None

    def pre_validation(self, config, key_name):
        self.config_dir = os.path.dirname(config.config_file_path) if config.config_file_path else None

    def run_validation(self, value):
        value = super().run_validation(value)
        if self.config_dir and not os.path.isabs(value):
            value = os.path.join(self.config_dir, value)
        if self.exists and not self.existence_test(value):
            raise ValidationError(f"The path {value} isn't an existing {self.name}.")
        return os.path.abspath(value)


class Dir(FilesystemObject):
    """
    Dir Config Option

    Validate a path to a directory, optionally verifying that it exists.
    """
    existence_test = staticmethod(os.path.isdir)
    name = 'directory'

    def post_validation(self, config, key_name):
        if config.config_file_path is None:
            return

        # Validate that the dir is not the parent dir of the config file.
        if os.path.dirname(config.config_file_path) == config[key_name]:
            raise ValidationError(
                (f"The '{key_name}' should not be the parent directory of the"
                 " config file. Use a child directory instead so that the"
                 f" '{key_name}' is a sibling of the config file."))


class File(FilesystemObject):
    """
    File Config Option

    Validate a path to a file, optionally verifying that it exists.
    """
    existence_test = staticmethod(os.path.isfile)
    name = 'file'


class ListOfPaths(OptionallyRequired):
    """
    List of Paths Config Option

    A list of file system paths. Raises an error if one of the paths does not exist.
    """

    def __init__(self, default=[], required=False):
        self.config_dir = None
        super().__init__(default, required)

    def pre_validation(self, config, key_name):
        self.config_dir = os.path.dirname(config.config_file_path) if config.config_file_path else None

    def run_validation(self, value):
        if not isinstance(value, list):
            raise ValidationError(f"Expected a list, got {type(value)}")
        if len(value) == 0:
            return
        paths = []
        for path in value:
            if self.config_dir and not os.path.isabs(path):
                path = os.path.join(self.config_dir, path)
            if not os.path.exists(path):
                raise ValidationError(f"The path {path} does not exist.")
            path = os.path.abspath(path)
            paths.append(path)
        return paths


class SiteDir(Dir):
    """
    SiteDir Config Option

    Validates the site_dir and docs_dir directories do not contain each other.
    """

    def post_validation(self, config, key_name):

        super().post_validation(config, key_name)

        # Validate that the docs_dir and site_dir don't contain the
        # other as this will lead to copying back and forth on each
        # and eventually make a deep nested mess.
        if (config['docs_dir'] + os.sep).startswith(config['site_dir'].rstrip(os.sep) + os.sep):
            raise ValidationError(
                ("The 'docs_dir' should not be within the 'site_dir' as this "
                 "can mean the source files are overwritten by the output or "
                 "it will be deleted if --clean is passed to mkdocs build."
                 "(site_dir: '{}', docs_dir: '{}')"
                 ).format(config['site_dir'], config['docs_dir']))
        elif (config['site_dir'] + os.sep).startswith(config['docs_dir'].rstrip(os.sep) + os.sep):
            raise ValidationError(
                ("The 'site_dir' should not be within the 'docs_dir' as this "
                 "leads to the build directory being copied into itself and "
                 "duplicate nested files in the 'site_dir'."
                 "(site_dir: '{}', docs_dir: '{}')"
                 ).format(config['site_dir'], config['docs_dir']))


class Theme(BaseConfigOption):
    """
    Theme Config Option

    Validate that the theme exists and build Theme instance.
    """

    def __init__(self, default=None):
        super().__init__()
        self.default = default

    def validate(self, value):
        if value is None and self.default is not None:
            value = {'name': self.default}

        if isinstance(value, str):
            value = {'name': value}

        themes = utils.get_theme_names()

        if isinstance(value, dict):
            if 'name' in value:
                if value['name'] is None or value['name'] in themes:
                    return value

                raise ValidationError(
                    f"Unrecognised theme name: '{value['name']}'. "
                    f"The available installed themes are: {', '.join(themes)}"
                )

            raise ValidationError("No theme name set.")

        raise ValidationError(f'Invalid type "{type(value)}". Expected a string or key/value pairs.')

    def post_validation(self, config, key_name):
        theme_config = config[key_name]

        if not theme_config['name'] and 'custom_dir' not in theme_config:
            raise ValidationError("At least one of 'theme.name' or 'theme.custom_dir' must be defined.")

        # Ensure custom_dir is an absolute path
        if 'custom_dir' in theme_config and not os.path.isabs(theme_config['custom_dir']):
            config_dir = os.path.dirname(config.config_file_path)
            theme_config['custom_dir'] = os.path.join(config_dir, theme_config['custom_dir'])

        if 'custom_dir' in theme_config and not os.path.isdir(theme_config['custom_dir']):
            raise ValidationError("The path set in {name}.custom_dir ('{path}') does not exist.".
                                  format(path=theme_config['custom_dir'], name=key_name))

        if 'locale' in theme_config and not isinstance(theme_config['locale'], str):
            raise ValidationError(f"'{theme_config['name']}.locale' must be a string.")

        config[key_name] = theme.Theme(**theme_config)


class Nav(OptionallyRequired):
    """
    Nav Config Option

    Validate the Nav config.
    """

    def run_validation(self, value, *, top=True):
        if isinstance(value, list):
            for subitem in value:
                self._validate_nav_item(subitem)
            if top and not value:
                value = None
        elif isinstance(value, dict) and value and not top:
            # TODO: this should be an error.
            self.warnings.append(f"Expected nav to be a list, got {self._repr_item(value)}")
            for subitem in value.values():
                self.run_validation(subitem, top=False)
        elif isinstance(value, str) and not top:
            pass
        else:
            raise ValidationError(f"Expected nav to be a list, got {self._repr_item(value)}")
        return value

    def _validate_nav_item(self, value):
        if isinstance(value, str):
            pass
        elif isinstance(value, dict):
            if len(value) != 1:
                raise ValidationError(f"Expected nav item to be a dict of size 1, got {self._repr_item(value)}")
            for subnav in value.values():
                self.run_validation(subnav, top=False)
        else:
            raise ValidationError(f"Expected nav item to be a string or dict, got {self._repr_item(value)}")

    @classmethod
    def _repr_item(cls, value):
        if isinstance(value, dict) and value:
            return f"dict with keys {tuple(value.keys())}"
        elif isinstance(value, (str, type(None))):
            return repr(value)
        else:
            return f"a {type(value).__name__}: {value!r}"


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

    A list or dict of extensions. Each list item may contain either a string or a one item dict.
    A string must be a valid Markdown extension name with no config options defined. The key of
    a dict item must be a valid Markdown extension name and the value must be a dict of config
    options for that extension. Extension configs are set on the private setting passed to
    `configkey`. The `builtins` keyword accepts a list of extensions which cannot be overridden by
    the user. However, builtins can be duplicated to define config options for them if desired. """
    def __init__(self, builtins=None, configkey='mdx_configs', **kwargs):
        super().__init__(**kwargs)
        self.builtins = builtins or []
        self.configkey = configkey
        self.configdata = {}

    def validate_ext_cfg(self, ext, cfg):
        if not isinstance(ext, str):
            raise ValidationError(f"'{ext}' is not a valid Markdown Extension name.")
        if not cfg:
            return
        if not isinstance(cfg, dict):
            raise ValidationError(f"Invalid config options for Markdown Extension '{ext}'.")
        self.configdata[ext] = cfg

    def run_validation(self, value):
        if not isinstance(value, (list, tuple, dict)):
            raise ValidationError('Invalid Markdown Extensions configuration')
        extensions = []
        if isinstance(value, dict):
            for ext, cfg in value.items():
                self.validate_ext_cfg(ext, cfg)
                extensions.append(ext)
        else:
            for item in value:
                if isinstance(item, dict):
                    if len(item) > 1:
                        raise ValidationError('Invalid Markdown Extensions configuration')
                    ext, cfg = item.popitem()
                    self.validate_ext_cfg(ext, cfg)
                    extensions.append(ext)
                elif isinstance(item, str):
                    extensions.append(item)
                else:
                    raise ValidationError('Invalid Markdown Extensions configuration')

        extensions = utils.reduce_list(self.builtins + extensions)

        # Confirm that Markdown considers extensions to be valid
        try:
            markdown.Markdown(extensions=extensions, extension_configs=self.configdata)
        except Exception as e:
            raise ValidationError(e.args[0])

        return extensions

    def post_validation(self, config, key_name):
        config[self.configkey] = self.configdata


class Plugins(OptionallyRequired):
    """
    Plugins config option.

    A list or dict of plugins. If a plugin defines config options those are used when
    initializing the plugin class.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.installed_plugins = plugins.get_plugins()
        self.config_file_path = None

    def pre_validation(self, config, key_name):
        self.config_file_path = config.config_file_path

    def run_validation(self, value):
        if not isinstance(value, (list, tuple, dict)):
            raise ValidationError('Invalid Plugins configuration. Expected a list or dict.')
        plgins = plugins.PluginCollection()
        if isinstance(value, dict):
            for name, cfg in value.items():
                plgins[name] = self.load_plugin(name, cfg)
        else:
            for item in value:
                if isinstance(item, dict):
                    if len(item) > 1:
                        raise ValidationError('Invalid Plugins configuration')
                    name, cfg = item.popitem()
                    item = name
                else:
                    cfg = {}
                plgins[item] = self.load_plugin(item, cfg)
        return plgins

    def load_plugin(self, name, config):
        if not isinstance(name, str):
            raise ValidationError(f"'{name}' is not a valid plugin name.")
        if name not in self.installed_plugins:
            raise ValidationError(f'The "{name}" plugin is not installed')

        config = config or {}  # Users may define a null (None) config
        if not isinstance(config, dict):
            raise ValidationError(f"Invalid config options for the '{name}' plugin.")

        Plugin = self.installed_plugins[name].load()

        if not issubclass(Plugin, plugins.BasePlugin):
            raise ValidationError(
                f'{Plugin.__module__}.{Plugin.__name__} must be a subclass of'
                f' {plugins.BasePlugin.__module__}.{plugins.BasePlugin.__name__}')

        plugin = Plugin()
        errors, warnings = plugin.load_config(config, self.config_file_path)
        self.warnings.extend(warnings)
        errors_message = '\n'.join(
            f"Plugin '{name}' value: '{x}'. Error: {y}"
            for x, y in errors
        )
        if errors_message:
            raise ValidationError(errors_message)
        return plugin

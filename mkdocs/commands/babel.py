from distutils.errors import DistutilsOptionError
from os import path
from pkg_resources import EntryPoint
from babel.messages import frontend as babel


DEFAULT_MAPPING_FILE = path.normpath(path.join(
    path.abspath(path.dirname(__file__)), '../themes/babel.cfg'
))


class ThemeMixin:
    def get_theme_dir(self):
        ''' Validate theme option and return path to theme's root obtained from entry point. '''
        entry_points = EntryPoint.parse_map(self.distribution.entry_points, self.distribution)
        if 'mkdocs.themes' not in entry_points:
            raise DistutilsOptionError("no mkdocs.themes are defined in entry_points")
        if self.theme not in entry_points['mkdocs.themes']:
            raise DistutilsOptionError("you must specify a valid theme name to work on")
        theme = entry_points['mkdocs.themes'][self.theme]
        return path.dirname(theme.resolve().__file__)


class compile_catalog(babel.compile_catalog, ThemeMixin):
    user_options = babel.compile_catalog.user_options + [
        ("theme=", "t", "theme name to work on"),
    ]

    def initialize_options(self):
        super().initialize_options()
        self.theme = None

    def finalize_options(self):
        if self.theme:
            theme_dir = self.get_theme_dir()
            self.directory = f"{theme_dir}/locales"
        super().finalize_options()


class extract_messages(babel.extract_messages, ThemeMixin):
    user_options = babel.extract_messages.user_options + [
        ("theme=", "t", "theme name to work on"),
    ]

    def initialize_options(self):
        super().initialize_options()
        self.theme = None

    def finalize_options(self):
        if not self.version:
            version = self.distribution.get_version()
            self.version = ".".join([i for i in version.split(".") if "dev" not in i])
        if not self.mapping_file:
            self.mapping_file = DEFAULT_MAPPING_FILE
        if self.theme:
            theme_dir = self.get_theme_dir()
            self.input_paths = theme_dir
            self.output_file = f"{theme_dir}/messages.pot"
        super().finalize_options()


class init_catalog(babel.init_catalog, ThemeMixin):
    user_options = babel.init_catalog.user_options + [
        ("theme=", "t", "theme name to work on"),
    ]

    def initialize_options(self):
        super().initialize_options()
        self.theme = None

    def finalize_options(self):
        if self.theme:
            theme_dir = self.get_theme_dir()
            self.input_file = f"{theme_dir}/messages.pot"
            self.output_dir = f"{theme_dir}/locales"
        super().finalize_options()


class update_catalog(babel.update_catalog, ThemeMixin):
    user_options = babel.update_catalog.user_options + [
        ("theme=", "t", "theme name to work on"),
    ]

    def initialize_options(self):
        super().initialize_options()
        self.theme = None

    def finalize_options(self):
        if self.theme:
            theme_dir = self.get_theme_dir()
            self.input_file = f"{theme_dir}/messages.pot"
            self.output_dir = f"{theme_dir}/locales"
        super().finalize_options()

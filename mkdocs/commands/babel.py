from distutils.errors import DistutilsOptionError
from os import path
from babel.messages import frontend as babel


DEFAULT_MAPPING_FILE = path.normpath(path.join(
    path.abspath(path.dirname(__file__)), '../themes/babel.cfg'
))


class ThemeMixin:
    def get_theme_dir(self):
        ''' Validate theme option and return path to theme's root obtained from entry point. '''
        if 'mkdocs.themes' not in self.distribution.entry_points:
            raise DistutilsOptionError("no mkdocs.themes are defined in entry_points")
        themes = {}
        for theme in self.distribution.entry_points['mkdocs.themes']:
            name, path = theme.split('=', 1)
            themes[name.strip()] = path.replace('.', '/').strip()
        if self.theme not in themes:
            raise DistutilsOptionError("you must specify a valid theme name to work on")
        return themes[self.theme]


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
        if not self.project:
            self.project = self.distribution.get_name()
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

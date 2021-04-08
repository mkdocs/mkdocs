from distutils.errors import DistutilsOptionError
from pathlib import Path

from mkdocs import __version__

from babel.messages import frontend as babel

VALID_THEMES = [
    d.name for d in Path("mkdocs/themes/").iterdir() if d.is_dir() and d.name[0] != "_"
]


class compile_catalog(babel.compile_catalog):
    user_options = babel.compile_catalog.user_options + [
        ("theme=", "t", "theme name to work on"),
    ]

    def initialize_options(self):
        super().initialize_options()
        self.theme = None
        self.statistics = True

    def finalize_options(self):
        if self.theme not in VALID_THEMES:
            raise DistutilsOptionError("you must specify a valid theme name to work on")
        self.domain = "messages"
        self.directory = f"mkdocs/themes/{self.theme}/locales"
        super().finalize_options()


class extract_messages(babel.extract_messages):
    user_options = babel.extract_messages.user_options + [
        ("theme=", "t", "theme name to work on"),
    ]

    def initialize_options(self):
        super().initialize_options()
        self.copyright_holder = "MkDocs"
        self.msgid_bugs_address = "https://github.com/mkdocs/mkdocs/issues"
        self.no_wrap = True
        self.project = "MkDocs"
        self.theme = None
        self.version = ".".join([i for i in __version__.split(".") if "dev" not in i])

    def finalize_options(self):
        if self.theme not in VALID_THEMES:
            raise DistutilsOptionError("you must specify a valid theme name to work on")
        self.input_paths = f"mkdocs/themes/{self.theme}"
        self.mapping_file = "mkdocs/themes/babel.cfg"
        self.output_file = f"mkdocs/themes/{self.theme}/messages.pot"
        super().finalize_options()


class init_catalog(babel.init_catalog):
    user_options = babel.init_catalog.user_options + [
        ("theme=", "t", "theme name to work on"),
    ]

    def initialize_options(self):
        super().initialize_options()
        self.theme = None

    def finalize_options(self):
        if self.theme not in VALID_THEMES:
            raise DistutilsOptionError("you must specify a valid theme name to work on")
        self.domain = "messages"
        self.input_file = f"mkdocs/themes/{self.theme}/messages.pot"
        self.output_dir = f"mkdocs/themes/{self.theme}/locales"
        super().finalize_options()


class update_catalog(babel.update_catalog):
    user_options = babel.update_catalog.user_options + [
        ("theme=", "t", "theme name to work on"),
    ]

    def initialize_options(self):
        super().initialize_options()
        self.ignore_obsolete = True
        self.theme = None
        self.update_header_comment = True

    def finalize_options(self):
        if self.theme not in VALID_THEMES:
            raise DistutilsOptionError("you must specify a valid theme name to work on")
        self.domain = "messages"
        self.input_file = f"mkdocs/themes/{self.theme}/messages.pot"
        self.output_dir = f"mkdocs/themes/{self.theme}/locales"
        super().finalize_options()

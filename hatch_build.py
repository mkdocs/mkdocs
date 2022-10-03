import os

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class CustomBuildHook(BuildHookInterface):
    def initialize(self, version, build_data):
        from babel.messages.frontend import compile_catalog

        for theme in 'mkdocs', 'readthedocs':
            cmd = compile_catalog()
            cmd.directory = os.path.join('mkdocs', 'themes', theme, 'locales')
            cmd.finalize_options()
            cmd.run()

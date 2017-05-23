# -*- coding: utf-8 -*-
"""
    Setuptools/distutils commands to assist the building of MkDocs
    documentation from python setup.py
"""

from distutils.cmd import Command

from mkdocs.__main__ import build_command


class BuildDoc(Command):
    """
    A custom command to build MkDocs documentation from setup.py
    """

    description = "Build MkDocs documentation"
    user_options = []
    boolean_options = []
    
    def initialize_options(self):
        pass
    
    def finalize_options(self):
        pass

    def run(self):
        Build = build_command
        Build()

from click import ClickException


class MkDocsException(ClickException):
    """Base exceptions for all MkDocs Exceptions"""


class ConfigurationError(MkDocsException):
    """Error in configuration"""


class BuildError(MkDocsException):
    """Error during the build process"""

    def __init__(self, message, reraise=False):
        super().__init__(message)
        self.reraise = reraise


class PluginError(BuildError):
    """Error in a plugin"""
